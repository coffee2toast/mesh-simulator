from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING

from mesh_simulator.packets import Packet
from mesh_simulator.protocols import Protocol

if TYPE_CHECKING:
    from mesh_simulator.devices import DeviceAgent


class TaskStatus(Enum):
    """Enumeration of task statuses."""

    PENDING = 0
    COMPLETED = 1
    FAILED = 2


class Task(ABC):
    def __init__(self, name: str):
        self._name = name
        self._status = TaskStatus.PENDING

    @property
    def name(self) -> str:
        return self._name

    def __str__(self):
        return f"{self.name} ({self.status})"

    @property
    def status(self) -> TaskStatus:
        return self._status

    def on_packet(self, agent: DeviceAgent, sender: DeviceAgent, protocol: Protocol, data: Packet) -> bool:
        # By default, tasks do not process any packets
        return False

    @abstractmethod
    def step(self, agent: DeviceAgent): ...
