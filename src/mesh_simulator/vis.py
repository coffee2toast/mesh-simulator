from __future__ import annotations

import solara
from matplotlib.figure import Figure


def agent_portrayal(agent):
    return {
        "color": "tab:blue",
        "size": 50,
    }


def connections(model):
    fig = Figure()
    ax = fig.subplots()
    for agent in model.schedule.agents:
        # dot for agent, and line to each connection
        color = "tab:blue"
        if not agent._tasks:
            color = "tab:gray"
        elif agent._tasks[0].__class__.__name__ == "HandshakeTask":
            color = "tab:orange"
        elif agent._tasks[0].__class__.__name__ == "ScanTask":
            color = "tab:red"
        ax.plot(agent.pos[0], agent.pos[1], "o", color=color)
        for _proto, connection in agent.connections:
            conn_color = "tab:green" if connection.is_connected(agent) else "tab:red"
            ax.plot(
                [agent.pos[0], connection.pos[0]],
                [agent.pos[1], connection.pos[1]],
                color=conn_color,
            )
    solara.FigureMatplotlib(fig)


def topology_metrics(model):
    data = model.datacollector.get_model_vars_dataframe()
    data = data.drop("Average Transit Time", axis=1)
    fig = Figure()
    ax = fig.subplots()
    ax.plot(data)
    ax.set(title="Topology Metrics", xlabel="Steps", ylabel="Value")
    ax.legend(data.columns)
    solara.FigureMatplotlib(fig)
