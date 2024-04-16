"""Tests the top-level mesh simulator module."""

from __future__ import annotations

import networkx as nx
import pytest

from mesh_simulator.analysis.graph import Node


@pytest.fixture
def graph():
    g = nx.Graph()
    a, b, c, d = Node(10.5, 50), Node(3.7, 73.3), Node(2.5, 20), Node(5.1, 100)
    g.add_edge(a, b, established=True, latency=0.5, bandwidth=10)
    g.add_edge(a, c, established=True, latency=0.1, bandwidth=100)
    g.add_edge(c, b, established=True, latency=0.3, bandwidth=20)
    g.add_edge(b, d, established=False, latency=0.2, bandwidth=50)
    return g


def test_reachability(graph):
    from mesh_simulator.analysis.metrics import reachability

    assert reachability(graph) == 0.5


def test_robustness(graph):
    from mesh_simulator.analysis.metrics import robustness

    assert robustness(graph) == 0.5


def test_bandwidth(graph):
    from mesh_simulator.analysis.metrics import bandwidth

    assert bandwidth(graph) == 1.0


def test_latency(graph):
    from mesh_simulator.analysis.metrics import latency

    assert latency(graph) == 1.0


def test_power(graph):
    from mesh_simulator.analysis.metrics import power

    assert power(graph) == 2 / 3
