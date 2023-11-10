import random
import mesa

from .model import Habitacion, Robot, Celda, Caja, Cargador

MAX_NUMBER_ROBOTS = 20


def agent_portrayal(agent):
    if isinstance(agent, Robot):
        return {"Shape": "circle", "Filled": "false", "Color": "black", "Layer": 1, "r": 1.0,
                "text": f"{agent.carga}", "text_color": "yellow"}
    elif isinstance(agent, Caja):
        return {"Shape": "rect", "Filled": "true", "Color": "white", "Layer": 0,
                "w": 0.9, "h": 0.9, "text_color": "Black", "text": "📦"}
    elif isinstance(agent, Cargador):
        return {"Shape": "rect", "Filled": "true", "Color": "white", "Layer": 0,
                "w": 0.9, "h": 0.9, "text_color": "Black", "text": "🔌"}
    elif isinstance(agent, Camion):
        return {"Shape": "rect", "Filled": "true", "Color": "white", "Layer": 0,
                "w": 0.9, "h": 0.9, "text_color": "Black", "text": "🚌"}
    elif isinstance(agent, Celda):
        portrayal = {"Shape": "rect", "Filled": "true", "Layer": 0, "w": 0.9, "h": 0.9, "text_color": "Black"}

        portrayal["Color"] = "white"
        portrayal["text"] = ""
        return portrayal
    

grid = mesa.visualization.CanvasGrid(
    agent_portrayal, 20, 20, 400, 400)
chart_celdas = mesa.visualization.ChartModule(
    [{"Label": "CeldasSucias", "Color": '#36A2EB', "label": "Celdas Sucias"}],
    50, 200,
    data_collector_name="datacollector"
)

model_params = {
    "num_agentes": mesa.visualization.Slider(
        "Número de Robots",
        5,
        2,
        MAX_NUMBER_ROBOTS,
        1,
        description="Escoge cuántos robots deseas implementar en el modelo",
    ),
    "M": 20,
    "N": 20,
}

server = mesa.visualization.ModularServer(
    Habitacion, [grid, chart_celdas],
    "RobotsEnAlmacenes", model_params, 8521
)
