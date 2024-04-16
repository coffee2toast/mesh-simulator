from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mesh_simulator.devices import DeviceAgent


class Protocol(ABC):
    def __init__(self, device: DeviceAgent):
        self.device = device

    @property
    @abstractmethod
    def scan_radius(self) -> int: ...

    @property
    @abstractmethod
    def scan_cost(self) -> int: ...

    @property
    @abstractmethod
    def scan_duration(self) -> int: ...

    @property
    @abstractmethod
    def connection_cost(self) -> int: ...

    @property
    @abstractmethod
    def latency(self) -> int: ...

    @property
    @abstractmethod
    def bandwidth(self) -> int: ...

    def can_connect(self, other: DeviceAgent) -> bool:
        if not any(isinstance(protocol, type(self)) for protocol in other.protocols):
            return False
        x, y = self.device.pos
        ox, oy = other.pos
        return (x - ox) ** 2 + (y - oy) ** 2 <= self.scan_radius**2

    def connect(self, other: DeviceAgent) -> None:
        if not self.can_connect(other):
            raise ValueError("Attempted invalid connection")
        self.device.connections.add((self, other))
