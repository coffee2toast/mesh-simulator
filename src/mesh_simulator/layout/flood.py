from __future__ import annotations

from typing import TYPE_CHECKING

from mesh_simulator.layout import LayoutAlgorithm
from mesh_simulator.tasks.handshake import HandshakeTask
from mesh_simulator.tasks.scan import ScanTask

if TYPE_CHECKING:
    from mesh_simulator.devices import DeviceAgent


class FloodLayout(LayoutAlgorithm):
    def __init__(self, device: DeviceAgent, scan_interval: int = 10):
        super().__init__(device)
        self.scan_interval = scan_interval
        """How many steps between each scan"""
        self.next_scan = device.random.randint(0, scan_interval)

    def step(self):
        if self.next_scan == 0:
            for protocol in self.device.protocols:
                self.device.queue_task(ScanTask(protocol, self.on_device_discovered))
            self.next_scan = self.scan_interval
        else:
            self.next_scan -= 1

    def on_device_discovered(self, protocol, device):
        """The flood algorithm connects to any device it discovers.

        Args:
            protocol (Protocol): The protocol used to connect to the device
            device (DeviceAgent): The device that was discovered
        """
        self.device.queue_task(HandshakeTask(device, protocol))
