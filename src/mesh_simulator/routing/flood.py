from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from mesh_simulator.protocols import Protocol
from mesh_simulator.routing import RoutingAlgorithm

if TYPE_CHECKING:
    from mesh_simulator.devices import DeviceAgent
    from mesh_simulator.packets import Packet


class FloodRouting(RoutingAlgorithm):
    def route(self, sender: DeviceAgent, protocol: Protocol, packet: Packet):
        if packet.ttl <= 0:
            return  # packet dropped
        new_packet = packet.with_ttl(packet.ttl - 1)
        if sender.is_connected(new_packet.destination):
            logger.debug(f"Sending packet directly to {new_packet.destination}")
            self.device.send_packet(protocol, new_packet, new_packet.destination)
            return
        logger.info(f"Looping over {len(self.device.connections)} connections")
        for proto, neighbor in self.device.connections:
            if neighbor != sender:
                logger.debug(
                    f"Routing packet from {sender} to {neighbor}, expected destination: {new_packet.destination}"
                )
                self.device.send_packet(proto, new_packet, neighbor)
