from __future__ import annotations

from mesa.experimental import JupyterViz

from mesh_simulator.model import MeshModel
from mesh_simulator.vis import agent_portrayal, connections, topology_metrics

model_params = {
    "n_agents": {
        "type": "SliderInt",
        "value": 100,
        "label": "Number of agents:",
        "min": 2,
        "max": 200,
        "step": 1,
    },
    "width": 75,
    "height": 75,
}


Page = JupyterViz(
    MeshModel,
    model_params,
    measures=[connections, topology_metrics, "Average Transit Time"],
    name="Mesh Network",
    agent_portrayal=agent_portrayal,
)
