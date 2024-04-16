from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING

from loguru import logger

from mesh_simulator.packets.handshake import (HandshakePacket,
                                              HandshakePacketType)
from mesh_simulator.protocols import Protocol
from mesh_simulator.tasks import Task, TaskStatus

if TYPE_CHECKING:
    from mesh_simulator.devices import DeviceAgent
    from mesh_simulator.packets import Packet


class HandshakeState(Enum):
    SEND_REQUEST = auto()
    SEND_RESPONSE = auto()
    SEND_ESTABLISH = auto()
    WAIT_RESPONSE = auto()
    WAIT_REQUEST = auto()
    WAIT_ESTABLISH = auto()


class HandshakeTask(Task):
    def __init__(self, other: DeviceAgent, protocol: Protocol, timeout: int = 5, server: bool = False):
        """Initializes a new HandshakeTask.

        Args:
            other (DeviceAgent): The other device to handshake with.
            timeout (int): The maximum number of steps to wait for the handshake to complete.
            server (bool, optional): If True, this HandshakeTask will not actively connect to the other
            DeviceAgent and simply wait for an incoming connection. Defaults to False.
        """
        super().__init__(f"Handshake with {other.name}")
        self._state = HandshakeState.SEND_REQUEST if not server else HandshakeState.WAIT_REQUEST
        self._timeout = timeout
        self._other = other
        self._protocol = protocol

    @property
    def other(self) -> DeviceAgent:
        return self._other

    def on_packet(self, agent: DeviceAgent, sender: DeviceAgent, protocol: Protocol, pkt: Packet) -> bool:
        """Processes incoming packets.

        Args:
            agent (DeviceAgent):The agent that received the packet.
            sender (DeviceAgent): The agent that sent the packet.
            pkt (Packet): The packet that was received.

        Returns:
            bool: Returns True if the packet was processed successfully.
        """
        if not isinstance(pkt, HandshakePacket) or self._other != sender:
            return False
        match (self._state, pkt.state):
            case (HandshakeState.WAIT_REQUEST, HandshakePacketType.REQUEST):
                self._state = HandshakeState.SEND_RESPONSE
                return True
            case (HandshakeState.WAIT_RESPONSE, HandshakePacketType.RESPONSE):
                self._state = HandshakeState.SEND_ESTABLISH
                return True
            case (HandshakeState.WAIT_ESTABLISH, HandshakePacketType.ESTABLISH):
                self._status = TaskStatus.COMPLETED
                agent.connections.add((self._protocol, self._other))
                return True
            case _:
                return False

    def step(self, agent: DeviceAgent):
        if self._status == TaskStatus.COMPLETED:
            return
        if self._timeout <= 0 or agent.is_connected(self._other):
            self._status = TaskStatus.FAILED
            return

        # if (agent.name == "Agent 0" and self._other.name != "Agent 1") or (
        #     self._other.name == "Agent 0" and agent.name != "Agent 1"
        # ):
        #     self._status = TaskStatus.FAILED
        #     return  # Simulate a failed handshake, so that packets between Agent 0 and Agent 1 must be routed

        if self._state == HandshakeState.SEND_REQUEST:
            agent.send_packet_immediate(
                self._protocol, HandshakePacket(agent, self._other, HandshakePacketType.REQUEST), self._other
            )
            self._state = HandshakeState.WAIT_RESPONSE
        elif self._state == HandshakeState.SEND_RESPONSE:
            agent.send_packet_immediate(
                self._protocol, HandshakePacket(agent, self._other, HandshakePacketType.RESPONSE), self._other
            )
            self._state = HandshakeState.WAIT_ESTABLISH
        elif self._state == HandshakeState.SEND_ESTABLISH:
            agent.send_packet_immediate(
                self._protocol, HandshakePacket(agent, self._other, HandshakePacketType.ESTABLISH), self._other
            )
            agent.connections.add((self._protocol, self._other))
            logger.info(f"Handshake completed between {agent.name} and {self._other.name}")
            self._status = TaskStatus.COMPLETED
        self._timeout -= 1
