from __future__ import annotations

import mesa

from mesh_simulator.analysis import metric_from_model
from mesh_simulator.analysis.metrics import (bandwidth, evaluate_large,
                                             evaluate_small, fairness, latency,
                                             power, reachability, robustness)
from mesh_simulator.devices.microbit import Microbit
from mesh_simulator.tasks.scan import ScanTask


class MeshModel(mesa.Model):
    def __init__(self, n_agents, width, height):
        super().__init__()
        self.schedule = mesa.time.RandomActivation(self)
        self.grid = mesa.space.MultiGrid(width, height, torus=False)
        for i in range(n_agents):
            a = Microbit(f"Agent {i}", self)
            self.schedule.add(a)
            coords = (self.random.randrange(0, self.grid.width), self.random.randrange(0, self.grid.height))
            self.grid.place_agent(a, coords)

        def avg_transit_time(model):
            total_time = 0
            total_packets = 0
            for agent in model.schedule.agents:
                for step in range(model.schedule.steps - 10, model.schedule.steps):
                    if step not in agent.received_packets:
                        continue
                    total_packets += len(agent.received_packets[step])
                    total_time += sum(p.initial_ttl - p.ttl for p in agent.received_packets[step])
            if total_packets == 0:
                return 0
            return total_time / total_packets

        reporters = {
            "Reachability": metric_from_model(reachability),
            "Routing Efficiency": metric_from_model(latency),
            "Power Efficiency": metric_from_model(power),
            "Fairness": metric_from_model(fairness),
            "Overall Evaluation": metric_from_model(evaluate_large),
            "Average Transit Time": avg_transit_time,
        }

        if n_agents < 10:
            reporters["Bandwidth Efficiency"] = metric_from_model(bandwidth)
            reporters["Robustness"] = metric_from_model(robustness)
            reporters["Overall Evaluation"] = metric_from_model(evaluate_small)

        self.datacollector = mesa.DataCollector(model_reporters=reporters)

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
