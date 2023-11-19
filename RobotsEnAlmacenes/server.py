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
        portrayal= {"Shape": "rect", "Filled": "true", "Color": "white", "Layer": 2,
                "w": 0.9, "h": 0.9, "text": "📦"}
        if agent.producto=="SanAnna Water":
            portrayal["Color"] = "blue"
        if agent.producto=="Bio Bottle":
            portrayal["Color"] = "green"
        if agent.producto=="Santhe":
            portrayal["Color"] = "brown"
        if agent.producto=="Beauty":
            portrayal["Color"] = "pink"
        if agent.producto=="Fruity Touch":
            portrayal["Color"] = "red"
        if agent.producto=="SantAnna Pro":
            portrayal["Color"] = "black"
        return portrayal
    


grid = mesa.visualization.CanvasGrid(agent_portrayal, 20, 20, 400, 400)

model_params = {
    "num_agentes": mesa.visualization.Slider(
        "Número de Robots",
        5, # Valor inicial al correr la simulación
        2, # Valor mínimo
        MAX_NUMBER_ROBOTS, # Valor máximo
        1, # Salto del slider
        description = "Escoge cuántos robots deseas implementar en el modelo",
    ),
   
    "M": 20,
    "N": 20,
}

server = mesa.visualization.ModularServer(
    Habitacion, [grid],
    "botCleaner", model_params, 8521
)
