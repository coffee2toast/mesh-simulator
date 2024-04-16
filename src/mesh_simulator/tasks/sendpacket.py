from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from mesh_simulator.protocols import Protocol
from mesh_simulator.tasks import Task, TaskStatus

if TYPE_CHECKING:
    from mesh_simulator.devices import DeviceAgent
    from mesh_simulator.packets import Packet


class SendPacketTask(Task):
    def __init__(
        self,
        destination: DeviceAgent,
        protocol: Protocol,
        packet: Packet,
    ):
        super().__init__("Send Packet Task")
        self._destination = destination
        self._protocol = protocol
        self._packet = packet
        self._delay = ((packet.size_estimate // protocol.bandwidth) + 1) + protocol.latency

    def step(self, agent: DeviceAgent):
        self._delay -= 1

        # The connection must exist for the entire duration of the task
        if not (self._protocol, self._destination) in agent.connections:
            agent._routing_algorithm.route(agent, self._protocol, self._packet)
            logger.debug(f"Routed packet from {agent} to {self._destination} with size {self._packet.size_estimate}")
            self._status = TaskStatus.COMPLETED
            return

        if self._delay <= 0:
            agent.send_packet_immediate(self._protocol, self._packet, self._destination)
            logger.debug(f"Sent packet from {agent} to {self._destination} with size {self._packet.size_estimate}")
            self._status = TaskStatus.COMPLETED
