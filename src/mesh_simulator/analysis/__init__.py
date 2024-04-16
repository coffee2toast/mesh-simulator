from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import networkx as nx

from mesh_simulator.analysis.graph import Node

if TYPE_CHECKING:
    from mesh_simulator.model import MeshModel


def metric_from_model(metric_fn: Callable[[nx.Graph], float]) -> Callable[[MeshModel], float]:
    def wrapper(model: MeshModel) -> float:
        g = nx.Graph()
        for agent in model.schedule.agents:
            g.add_node(agent)
            for neighbor in model.schedule.agents:
                if agent == neighbor or not any(p.can_connect(neighbor) for p in agent.protocols):
                    continue
                if agent.is_connected(neighbor):
                    proto, _ = next(filter(lambda x: x[1] == neighbor, agent.connections))
                    g.add_edge(agent, neighbor, established=True, latency=proto.latency, bandwidth=proto.bandwidth)
                else:
                    connection_proto = next(filter(lambda p: p.can_connect(neighbor), agent.protocols))
                    g.add_edge(
                        agent,
                        neighbor,
                        established=False,
                        latency=connection_proto.latency,
                        bandwidth=connection_proto.bandwidth,
                    )
        return metric_fn(g)

    return wrapper
