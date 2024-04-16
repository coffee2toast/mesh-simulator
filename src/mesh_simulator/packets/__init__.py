from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mesh_simulator.devices import DeviceAgent


class Packet:

    def __init__(self, source: DeviceAgent, destination: DeviceAgent, size_estimate: int, ttl: int = 30):
        self._source = source
        self._destination = destination
        self._size_estimate = size_estimate
        self._ttl = ttl
        self._initial_ttl = ttl

    @property
    def size_estimate(self):
        return self._size_estimate

    @property
    def source(self):
        return self._source

    @property
    def destination(self):
        return self._destination

    @property
    def ttl(self):
        return self._ttl

    @property
    def initial_ttl(self):
        return self._initial_ttl

    def with_ttl(self, ttl: int):
        return Packet(self.source, self.destination, self.size_estimate, ttl)
