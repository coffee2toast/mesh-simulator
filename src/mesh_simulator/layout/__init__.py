from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mesh_simulator.devices import DeviceAgent


class LayoutAlgorithm(ABC):

    def __init__(self, device: DeviceAgent):
        self.device = device

    @abstractmethod
    def step(self): ...
