"""Mesh simulator"""

from __future__ import annotations

__version__ = "0.0.2"


from mesa.experimental import JupyterViz

from mesh_simulator.model import MeshModel
from mesh_simulator.vis import agent_portrayal, connections

model_params = {
    "n_agents": {
        "type": "SliderInt",
        "value": 7,
        "label": "Number of agents:",
        "min": 2,
        "max": 200,
        "step": 1,
    },
    "width": 10,
    "height": 10,
}


page = JupyterViz(
    MeshModel,
    model_params,
    measures=[connections, "Reachability", "Robustness", "Power Efficiency"],
    name="Mesh Network",
    agent_portrayal=agent_portrayal,
)
