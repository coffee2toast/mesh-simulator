from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Node:
    own_data: float
    total_data: float

    def __hash__(self):
        return hash((self.own_data, self.total_data))
