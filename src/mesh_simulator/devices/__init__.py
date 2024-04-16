from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import mesa
from loguru import logger

from mesh_simulator.packets import Packet
from mesh_simulator.packets.handshake import (HandshakePacket,
                                              HandshakePacketType)
from mesh_simulator.protocols import Protocol
from mesh_simulator.tasks import Task, TaskStatus
from mesh_simulator.tasks.handshake import HandshakeTask
from mesh_simulator.tasks.scan import ScanTask
from mesh_simulator.tasks.sendpacket import SendPacketTask

if TYPE_CHECKING:
    from mesh_simulator.layout import LayoutAlgorithm
    from mesh_simulator.model import MeshModel
    from mesh_simulator.routing import RoutingAlgorithm


class DeviceAgent(mesa.Agent):
    def __init__(
        self,
        name: str,
        model: MeshModel,
        protocols: list[type[Protocol]],
        layout_algorithm: Callable[[DeviceAgent], LayoutAlgorithm],
        routing_algorithm: Callable[[DeviceAgent], RoutingAlgorithm],
    ):
        """The base class for all devices in the simulation

        Args:
            name (str): A display name for the device.
            model (MeshModel): The model the device is attached to.
            protocols (list[type[Protocol]]): A list of protocols that are attached to the device. Note that each device must have their own instance of the protocol, as it is 'attached' to the device.
            layout_algorithm (Callable[[DeviceAgent], LayoutAlgorithm]): The layout algorithm factory to use for the device. If the layout algorithm isn't parameterized, this can be the class of the layout algorithm itself.
            routing_algorithm (Callable[[DeviceAgent], RoutingAlgorithm]): The routing algorithm factory to use for the device. If the routing algorithm isn't parameterized, this can be the class of the routing algorithm itself.
        """
        super().__init__(name, model)
        self._name = name
        self._tasks: list[Task] = []
        self._protocols: list[Protocol] = [protocol(self) for protocol in protocols]
        self.own_data: int = 0
        """The amount of data submitted to the network by the device in the current simulation"""
        self.total_data: int = 0
        """The total amount of data forwarded by the device in the current simulation"""
        self.consumed_energy = 0
        """The amount of energy consumed by the device in the current simulation"""
        self._layout_algorithm = layout_algorithm(self)
        self._routing_algorithm = routing_algorithm(self)
        self._connections: set[tuple[Protocol, DeviceAgent]] = set()
        self._received_packets: dict[int, list[Packet]] = {}

    @property
    def name(self) -> str:
        return self._name

    @property
    def protocols(self) -> list[Protocol]:
        return self._protocols

    def __str__(self):
        return f"DeviceAgent {self.name} at {self.pos}"

    def __repr__(self):
        return f"DeviceAgent({self.name}, ...)"

    @property
    def connections(self):
        return self._connections

    @property
    def received_packets(self):
        return self._received_packets

    def _pre_tasks(self):
        ...
        # sort all ScanTasks to the back
        # self._tasks.sort(key=lambda task: not isinstance(task, ScanTask))

    def step(self):
        logger.trace(f"Stepping {self.name}")

        self._pre_tasks()
        self._layout_algorithm.step()
        self._routing_algorithm.step()

        while self._tasks and self._tasks[0].status != TaskStatus.PENDING:
            self._tasks.pop(0)

        if not self._tasks:
            logger.trace(f"No tasks for {self.name}")
        else:
            active_task = self._tasks[0]
            logger.debug(f"{self.name}: Active task: {active_task}")
            active_task.step(self)
            if active_task.status == TaskStatus.COMPLETED or active_task.status == TaskStatus.FAILED:
                self._tasks.pop(0)

        self._drop_timeout_connections()
        self._move()
        self._post_tasks()

    def _post_tasks(self):
        return
        if self.random.random() < 0.1:  # and self.name == "Agent 0":
            target = self.random.choice(self.model.schedule.agents)
            if target != self:
                logger.debug(f"Sending packet to {target.name}")
                self.send_packet_any_protocol(Packet(self, target, 1, 10), target)

    def _drop_timeout_connections(self):
        # Check for any dead connections
        for protocol, other in self._connections.copy():
            if not protocol.can_connect(other):
                self._connections.remove((protocol, other))

    def _move(self):
        if self.random.random() < 0.1:
            new_cell = self.random.choice(self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False))
            self.model.grid.move_agent(self, new_cell)

    def queue_task(self, task: Task):
        logger.trace(f"Queuing task: {task}. Tasks: {len(self._tasks)}")
        self._tasks.append(task)

    def send_packet(self, protocol: Protocol, packet: Packet, destination: DeviceAgent):
        logger.trace(f"Queueing packet: {packet}")
        if protocol is None and self.is_connected(destination):
            proto = next(proto for proto, device in self._connections if device == destination)
            self.queue_task(SendPacketTask(destination, proto, packet))
        else:
            self.queue_task(SendPacketTask(destination, protocol, packet))

    def send_packet_any_protocol(self, packet: Packet, destination: DeviceAgent):
        if self.is_connected(destination):
            logger.debug(f"Sending packet to {destination.name} using existing connection")
            proto = next(proto for proto, device in self._connections if device == destination)
            self.queue_task(SendPacketTask(destination, proto, packet))
        else:
            logger.debug(f"Sending packet to {destination.name} using routing algorithm")
            self._routing_algorithm.route(self, None, packet)

    def send_packet_immediate(self, protocol: Protocol, packet: Packet, destination: DeviceAgent):
        logger.trace(f"Sending packet: {packet}")
        if packet.source is self:
            self.own_data += packet.size_estimate
        self.total_data += packet.size_estimate
        destination.on_packet(self, protocol, packet)

    def on_packet(self, sender: DeviceAgent, protocol: Protocol, packet: Packet):
        if not any(type(protocol) == type(p) for p in self._protocols):
            logger.error(f"Received packet from {sender.name} using unsupported protocol {protocol}")
            return
        if packet.destination != self:
            self._routing_algorithm.route(sender, protocol, packet)
            return
        logger.trace(f"Received packet from {sender.name}: {packet}")
        logger.debug(f"{self.name}: {self.own_data}, {self.total_data}")
        if self._tasks and self._tasks[0].on_packet(self, sender, protocol, packet):
            # Packet was processed by the task
            return
        # The packet might be unsolicited

        # Check if the packet is a handshake request
        if isinstance(packet, HandshakePacket) and packet.state == HandshakePacketType.REQUEST:
            # Check if we are already handshaking with the sender
            for task in self._tasks:
                if isinstance(task, HandshakeTask) and task.other == sender:
                    return
            # Create a new task to handle the handshake
            task = HandshakeTask(sender, protocol, server=True)
            task.on_packet(self, sender, protocol, packet)
            self._tasks.append(task)
            return
        else:
            # This is a "normal" packet
            self._received_packets[self.model.schedule.steps] = self._received_packets.get(
                self.model.schedule.steps, []
            ) + [packet]

    def connect(self, other: DeviceAgent, protocol: Protocol):
        logger.trace(f"Connecting to {other.name} using {protocol}")
        assert protocol in self._protocols, f"{protocol} not attached to {self}"
        protocol.connect(other)

    def is_connected(self, other: DeviceAgent) -> bool:
        for _, device in self._connections:
            if device == other:
                return True
        return False
