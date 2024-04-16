from __future__ import annotations

from mesh_simulator.devices import DeviceAgent
from mesh_simulator.protocols import Protocol


class Wifi2G(Protocol):
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
        return 100

    def can_connect(self, other: DeviceAgent) -> bool:
        # FIXME: Devices can only EITHER be in AP mode OR client mode.
        # This has to be considered here, because AP<->AP connections are not allowed.
        return super().can_connect(other)
