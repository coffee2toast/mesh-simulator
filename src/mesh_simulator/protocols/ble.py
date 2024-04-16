from __future__ import annotations

from mesh_simulator.protocols import Protocol


class BLE(Protocol):
    @property
    def scan_radius(self) -> int:
        return 50

    @property
    def scan_cost(self) -> int:
        return 1

    @property
    def scan_duration(self) -> int:
        return 10

    @property
    def connection_cost(self) -> int:
        return 2

    @property
    def latency(self) -> int:
        return 1

    @property
    def bandwidth(self) -> int:
        return 10
