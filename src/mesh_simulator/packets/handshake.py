from __future__ import annotations

from enum import Enum

from mesh_simulator.packets import Packet


class HandshakePacketType(Enum):
    REQUEST = 0
    RESPONSE = 1
    ESTABLISH = 2


class HandshakePacket(Packet):
    def __init__(self, source, destination, state: HandshakePacketType):
        super().__init__(source, destination, 1)
        self._state = state

    @property
    def state(self):
        return self._state

    def __str__(self):
        return f"HandshakePacket({self.state})"
