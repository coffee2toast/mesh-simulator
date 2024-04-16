from __future__ import annotations

from typing import TYPE_CHECKING

from mesh_simulator.protocols import Protocol
from mesh_simulator.routing import RoutingAlgorithm

if TYPE_CHECKING:
    from mesh_simulator.devices import DeviceAgent
    from mesh_simulator.packets import Packet


class RandomRouting(RoutingAlgorithm):
    def route(self, _sender: DeviceAgent, protocol: Protocol, packet: Packet):
        next_hop = self.device.random.choice(self.device.established_neighbors)
        if next_hop is not None:
            self.device.send_packet(protocol, packet, next_hop)
        # packet dropped if no neighbors
