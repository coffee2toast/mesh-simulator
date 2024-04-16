from __future__ import annotations

from typing import TYPE_CHECKING

from mesh_simulator.devices import DeviceAgent
from mesh_simulator.layout.flood import FloodLayout
from mesh_simulator.protocols.ble import BLE
from mesh_simulator.protocols.wifi import Wifi2G
from mesh_simulator.routing.flood import FloodRouting

if TYPE_CHECKING:
    from mesh_simulator.model import MeshModel


class Microbit(DeviceAgent):
    def __init__(self, name: str, model: MeshModel):
        super().__init__(name, model, [BLE, Wifi2G], lambda d: FloodLayout(d, 300), FloodRouting)
