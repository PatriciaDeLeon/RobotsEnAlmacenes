import mesa
from flask import Flask, jsonify, request
from threading import Thread
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid

from model import Habitacion, Robot, Celda, Estante, Cargador, Caja

MAX_NUMBER_ROBOTS = 20
MAX_CARGADORES = 3
MAX_CAJAS = 100
MAX_STEPS = 3600
robots = 2
chargers = 3
in_boxes = 6
out_boxes = 3
steps = 120


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
        2, # Valor inicial al correr la simulación
        1, # Valor mínimo
        MAX_NUMBER_ROBOTS, # Valor máximo
        1, # Salto del slider
        description = "Escoge cuántos robots deseas implementar en el modelo",
    ),
    "num_cargadores": mesa.visualization.Slider(
        "Número de Cargadores",
        2, # Valor inicial al correr la simulación
        1, # Valor mínimo
        MAX_CARGADORES, # Valor máximo
        1, # Salto del slider
        description = "Escoge cuántos cargadores deseas implementar en el modelo",
    ),
    "num_cajas_entrada": mesa.visualization.Slider(
        "Número de Cajas de Entrada",
        6, # Valor inicial al correr la simulación
        1, # Valor mínimo
        MAX_CAJAS, # Valor máximo
        1, # Salto del slider
        description = "Escoge cuántas cajas de entrada deseas implementar en el modelo",
    ),
    "num_cajas_salida": mesa.visualization.Slider(
        "Número de Cajas de Salida",
        3, # Valor inicial al correr la simulación
        1, # Valor mínimo
        MAX_CAJAS, # Valor máximo
        1, # Salto del slider
        description = "Escoge cuántas cajas de salida deseas implementar en el modelo",
    ),
    "num_steps": mesa.visualization.Slider(
        "Número de Steps",
        120, # Valor inicial al correr la simulación
        60, # Valor mínimo
        MAX_STEPS, # Valor máximo
        60, # Salto del slider
        description = "Escoge cuántos steps deseas implementar en el modelo",
    ),
    "M": 20,
    "N": 20,
}

app = Flask(__name__)

def make_model(num_agentes, num_cargadores, num_cajas_entrada, num_cajas_salida, num_steps, M, N):
    return Habitacion(
        num_agentes=num_agentes,
        num_cargadores=num_cargadores,
        num_cajas_entrada=num_cajas_entrada,
        num_cajas_salida=num_cajas_salida,
        num_steps=num_steps,
        M=M,
        N=N
    )

server = mesa.visualization.ModularServer(
    make_model, [grid],
    "botCleaner", model_params, 8521
)

if __name__ == "__main__":
    app.run(port=5000)