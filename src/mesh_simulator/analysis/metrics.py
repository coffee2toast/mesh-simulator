from __future__ import annotations

from itertools import combinations
from statistics import StatisticsError, correlation

import networkx as nx

from mesh_simulator.analysis.graph import Node


def established_graph(g: nx.Graph) -> nx.Graph:
    return nx.subgraph_view(g, filter_edge=lambda u, v: g[u][v]["established"])


def reachability(g: nx.Graph) -> float:
    return len(list(nx.connected_components(g))) / len(list(nx.connected_components(established_graph(g))))


def _absolute_robustness(g: nx.Graph) -> int:
    count = 0
    for a, b in combinations(g, 2):
        seen: set[Node] = set()
        # Find all simple paths between a and b in the graph
        for path in nx.all_simple_paths(g, a, b):
            path_set = set(path)
            # Check if the path has only new nodes
            if seen & path_set == set():
                count += 1
            # Add the nodes of the path to the set of seen nodes
            seen.update(path_set)
    return count


def robustness(g: nx.Graph) -> float:
    try:
        return _absolute_robustness(established_graph(g)) / _absolute_robustness(g)
    except ZeroDivisionError:
        return 1.0


def _absolute_bandwidth(g: nx.Graph) -> float:
    total_bandwidth = 0.0
    for a, b in combinations(g, 2):
        if not nx.has_path(established_graph(g), a, b):
            continue
        bandwidth = float("-inf")
        # Find the minimum bandwidth of all paths between a and b in the graph
        for path in nx.all_simple_paths(g, a, b):
            bandwidth = max(bandwidth, min(g[u][v]["bandwidth"] for u, v in zip(path, path[1:])))
        if bandwidth != float("-inf"):
            total_bandwidth += bandwidth
    return total_bandwidth


def bandwidth(g: nx.Graph) -> float:
    try:
        return _absolute_bandwidth(g) / _absolute_bandwidth(established_graph(g))
    except ZeroDivisionError:
        return 1.0


def latency(g):
    total_latency = 0
    established_latency = 0
    for a, b in combinations(g, 2):
        try:
            p_potential = nx.shortest_path(g, a, b, weight="latency")
            p_established = nx.shortest_path(established_graph(g), a, b, weight="latency")
            total_latency += sum(g[u][v]["latency"] for u, v in zip(p_potential, p_potential[1:]))
            established_latency += sum(g[u][v]["latency"] for u, v in zip(p_established, p_established[1:]))
        except nx.NetworkXNoPath:
            continue
    if established_latency == 0:
        return 1.0
    return total_latency / established_latency


def power(g):
    established = established_graph(g)
    edges_count = len(established.edges)
    least_possible_edges = len(g) - len(list(nx.connected_components(established)))
    if edges_count == 0:
        return 1.0
    return least_possible_edges / edges_count


def fairness(g):
    try:
        own_data, total_data = zip(*((n.own_data, n.total_data) for n in g.nodes))
        return (correlation(own_data, total_data) + 1) / 2
    except StatisticsError:
        return 1.0


def evaluate_small(
    g,
    reachability_weight=1,
    robustness_weight=1,
    bandwidth_weight=1,
    latency_weight=1,
    power_weight=1,
    fairness_weight=1,
):
    w = [reachability_weight, robustness_weight, bandwidth_weight, latency_weight, power_weight, fairness_weight]
    f = [reachability, robustness, bandwidth, latency, power, fairness]
    return sum(wi * fi(g) for wi, fi in zip(w, f)) / sum(w)


def evaluate_large(
    g,
    reachability_weight=1,
    latency_weight=1,
    power_weight=1,
    fairness_weight=1,
):
    w = [reachability_weight, latency_weight, power_weight, fairness_weight]
    f = [reachability, latency, power, fairness]
    return sum(wi * fi(g) for wi, fi in zip(w, f)) / sum(w)
