from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from mesh_simulator.protocols import Protocol
from mesh_simulator.tasks import Task, TaskStatus
from mesh_simulator.tasks.handshake import HandshakeTask

if TYPE_CHECKING:
    from mesh_simulator.devices import DeviceAgent
    from mesh_simulator.packets import Packet


class ScanTask(Task):
    def __init__(
        self,
        protocol: Protocol,
        on_device_discovered: Callable[[Protocol, DeviceAgent], None] = lambda _, __: None,
    ):
        super().__init__("Scan Task")
        self._protocol = protocol
        self._duration = protocol.scan_duration
        self._on_device_discovered = on_device_discovered

    def step(self, agent: DeviceAgent):
        self._duration -= 1

        if self._duration <= 0:
            agent.consumed_energy += self._protocol.scan_cost
            neighbors = agent.model.grid.get_neighbors(
                agent.pos, moore=False, include_center=True, radius=self._protocol.scan_radius
            )
            for neighbor in neighbors:
                if neighbor != agent:
                    self._on_device_discovered(self._protocol, neighbor)
            self._status = TaskStatus.COMPLETED
