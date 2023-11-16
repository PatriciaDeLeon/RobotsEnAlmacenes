import mesa

from .model import Habitacion, Robot, Celda, Estante, Cargador, Caja

MAX_NUMBER_ROBOTS = 20


def agent_portrayal(agent):
    if isinstance(agent, Robot):
        return {"Shape": "rect", "Filled": "true", "Color": "white", "Layer": 1,
                "w": 0.9, "h": 0.9, "text": "🤖"}
    elif isinstance(agent, Cargador):
        return {"Shape": "rect", "Filled": "true", "Color": "yellow", "Layer": 0,
                "w": 0.9, "h": 0.9, "text": "🔋"}
    elif isinstance(agent, Estante):
        return {"Shape": "rect", "Filled": "true", "Color": "white", "Layer": 0,
                "w": 0.9, "h": 0.9, "text": "🗄️"}
    elif isinstance(agent, Celda):
        portrayal = {"Shape": "rect", "Filled": "true", "Layer": 0, "w": 0.9, "h": 0.9, "text_color": "Black"}
        portrayal["Color"] = "white"
        portrayal["text"] = ""
    elif isinstance(agent, Caja):
        return {"Shape": "rect", "Filled": "true", "Color": "white", "Layer": 2,
                "w": 0.9, "h": 0.9, "text": "📦"}


grid = mesa.visualization.CanvasGrid(agent_portrayal, 20, 20, 400, 400)

chart_celdas = mesa.visualization.ChartModule(
    [{"Label": "CeldasSucias", "Color": '#36A2EB', "label": "Celdas Sucias"}],
    50, 200,
    data_collector_name = "datacollector",
)
chart_tiempo = mesa.visualization.ChartModule(
    [{"Label": "Tiempo", "Color": '#34BA89', "label": "Tiempo Necesario para Limpiar Salón"}],
    50, 200,
    data_collector_name="datacollector"
)
chart_movimientos = mesa.visualization.ChartModule(
    [{"Label": "Movimientos", "Color": '#F59F3D', "label": "Número de Movimientos Realizados por Robots"}],
    50, 200,
    data_collector_name="datacollector"
)
chart_recarga = mesa.visualization.ChartModule(
    [{"Label": "Recargas", "Color": '#8D6BD5', "label": "Cantidad de Recargas Completas"}],
    50, 200,
    data_collector_name="datacollector"
)

model_params = {
    "num_agentes": mesa.visualization.Slider(
        "Número de Robots",
        5, # Valor inicial al correr la simulación
        2, # Valor mínimo
        MAX_NUMBER_ROBOTS, # Valor máximo
        1, # Salto del slider
        description = "Escoge cuántos robots deseas implementar en el modelo",
    ),
    "porc_celdas_sucias": mesa.visualization.Slider(
        "Porcentaje de Celdas Sucias",
        0.3, # Valor inicial al correr la simulación
        0.0, # Valor mínimo
        0.70, # Valor máximo
        0.05, # Salto del slider
        description = "Selecciona el porcentaje de celdas sucias",
    ),
    "porc_muebles": mesa.visualization.Slider(
        "Porcentaje de Muebles",
        0.1, # Valor inicial al correr la simulación
        0.0, # Valor mínimo
        0.20, # Valor máximo
        0.01, # Salto del slider
        description = "Selecciona el porcentaje de muebles",
    ),
    "modo_pos_inicial": mesa.visualization.Choice(
        "Posición Inicial de los Robots",
        "Aleatoria",
        ["Fija", "Aleatoria"],
        "Seleciona la forma se posicionan los robots"
    ),
    
    "M": 20,
    "N": 20,
}

server = mesa.visualization.ModularServer(
    Habitacion, [grid, chart_celdas, chart_tiempo, chart_movimientos, chart_recarga],
    "botCleaner", model_params, 8521
)
