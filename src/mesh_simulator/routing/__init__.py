from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from mesh_simulator.packets import Packet
from mesh_simulator.protocols import Protocol

if TYPE_CHECKING:
    from mesh_simulator.devices import DeviceAgent


class RoutingAlgorithm(ABC):

    def __init__(self, device: DeviceAgent):
        self.device = device

    def step(self):
        """Perform any necessary periodic tasks."""
        pass

    @abstractmethod
    def route(self, sender: DeviceAgent, protocol: Protocol, packet: Packet):
        """Route a packet, or drop it if it cannot be routed.

        Args:
            sender (GenericDeviceAgent): The device that the packet was received from.
            packet (Packet): The packet to route.
        """
        pass
