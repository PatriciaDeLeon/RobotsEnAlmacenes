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
total_steps = 60
state = 1


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
    "M": 20,
    "N": 20,
    "total_steps": total_steps,  # Aquí debes proporcionar un valor adecuado para total_steps
    "state": state
}

app = Flask(__name__)

def make_model(num_agentes, num_cargadores, num_cajas_entrada, num_cajas_salida, total_steps, state, M, N):
    return Habitacion(
        num_agentes=num_agentes,
        num_cargadores=num_cargadores,
        num_cajas_entrada=num_cajas_entrada,
        num_cajas_salida=num_cajas_salida,
        total_steps=total_steps,
        state = 1,
        M=M,
        N=N
    )


server = mesa.visualization.ModularServer(
    make_model, [grid],
    "botCleaner", model_params, 8521
)

@app.route("/receive_data", methods=["POST"])
def receive_data():
    global robots
    global server
    global chargers
    global in_boxes
    global out_boxes
    try:
        data_json = request.json
        print(data_json)

        robots = data_json["robots"]
        chargers = data_json["chargers"]
        minutes = data_json["minutes"]
        seconds = data_json["seconds"]
        in_boxes = data_json["inBoxes"]
        out_boxes = data_json["outBoxes"]
        
        # Calcular el número total de steps
        total_steps = minutes * 60 + seconds

       
        model_params["num_agentes"].value = robots
        model_params["num_cargadores"].value = chargers
        model_params["num_cajas_entrada"].value = in_boxes
        model_params["num_cajas_salida"].value = out_boxes
        model_params["total_steps"] = total_steps
        tiempo = 0
        state = 1


 # Actualizamos el modelo
        server.model = make_model(
            num_agentes = robots,
            num_cargadores=chargers,
            num_cajas_entrada=in_boxes,
            num_cajas_salida=out_boxes,
            M=model_params["M"],
            N=model_params["N"],
            total_steps = total_steps,
            state = 1
        )

        # Lanzamos la simulación
        server.launch()
        server.model.step()
  

        return jsonify({"message": "Simulación reiniciada correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)})
    
@app.route("/get_robot_positions")
def get_robot_positions():
    model = server.model

    if isinstance(model, Habitacion):
        positions = model.get_robot_positions()
        return jsonify(positions)
    else:
        return jsonify({"error": "Model is not an instance of Habitacion"})
    
@app.route("/get_box_positions")
def get_box_positions():
    model = server.model

    if isinstance(model, Habitacion):
        positions = model.get_box_positions()
        return jsonify(positions)
    else:
        return jsonify({"error": "El modelo no es una instancia de Habitacion"})

@app.route("/get_cargador_positions")
def get_cargador_positions():
    model = server.model

    if isinstance(model, Habitacion):
        positions = model.get_cargador_positions()
        return jsonify(positions)
    else:
        return jsonify({"error": "El modelo no es una instancia de Habitacion"})
    
@app.route("/get_estante_positions")
def get_estante_positions():
    model = server.model

    if isinstance(model, Habitacion):
        positions = model.get_estante_positions()
        return jsonify(positions)
    else:
        return jsonify({"error": "El modelo no es una instancia de Habitacion"})
    
# Definir una ruta para obtener los datos
@app.route('/get_simulation_data', methods=['GET'])
def get_simulation_data():
    model = server.model
    
    if isinstance(model, Habitacion):
        data = model.send_data_to_api()
        return jsonify(data)
    else:
        return jsonify({"error": "El modelo no es una instancia de Habitacion"})
    
@app.route("/receive_state", methods=["POST"])
def receive_state():
    global state
    try:
        data_json = request.json
        print(data_json)
        state = data_json["state"]

        # Llama al método en tu modelo para procesar los datos de Unity
        server.model.receive_state(state)

        return jsonify({"success": True})  # Agrega una respuesta de éxito
    except Exception as e:
        print(str(e))
        return jsonify({"error": str(e)})

    
if __name__ == "__main__":
    app.run(port=5000)