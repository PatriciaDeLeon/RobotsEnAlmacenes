#IMPORTS
from mesa.model import Model
from mesa.agent import Agent
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector

import numpy as np
import math


#AGENTES
class Celda(Agent):
    def __init__(self, unique_id, model, suciedad: bool = False):
        super().__init__(unique_id, model)
        self.sucia = suciedad

class Cargador(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

class Caja(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

class Camion(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

class Robot(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.sig_pos = None
        self.movimientos = 0
        self.carga = 100

    #Seleccionar nueva posicion
    def seleccionar_nueva_pos(self, lista_de_vecinos):
        self.sig_pos = self.random.choice(lista_de_vecinos).pos
        while self.sig_pos not in posiciones_disponibles:
            self.sig_pos = self.random.choice(lista_de_vecinos).pos

   #Buscar cargadores cercanos
    def calcular_distancia(self, cargador, elemento_actual):
        # Utiliza la fórmula de distancia euclidiana para calcular la distancia entre dos puntos
        x1, y1 = cargador
        x2 = elemento_actual[0]
        y2 = elemento_actual[1]
        distancia = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        return distancia

    def buscar_cargadores(self,posiciones_cargadores, elemento_actual):
        if not posiciones_cargadores:
            return None  # Si la lista de posiciones de cargadores está vacía, no hay cargadores disponibles

        distancia_minima = float('inf')
        cargador_mas_cercano = None

        for cargador in posiciones_cargadores:
            distancia = self.calcular_distancia(cargador, elemento_actual)
            if distancia < distancia_minima:
                distancia_minima = distancia
                cargador_mas_cercano = cargador
        
        return cargador_mas_cercano
    
    #Moverse a cargador cercano
    def moverse_a_cargador(self, pos_cargador, celdas_sucias):
           #inferior izq
        if pos_cargador[0]==0 and pos_cargador[1]==0:
            if self.pos[0]!=0 and self.pos[1]!=0 :
               self.sig_pos = (self.pos[0]-1, self.pos[1]-1) 
            elif self.pos[0]!=0 and self.pos[1]==0:
               self.sig_pos = (self.pos[0]-1, self.pos[1])
            elif self.pos[0]==0 and self.pos[1]!=0:
               self.sig_pos = (self.pos[0], self.pos[1]-1)

        #superior izq
        elif pos_cargador[0]==0 and pos_cargador[1]!=0:
            if self.pos[0]!=0 and self.pos[1]!=0 :
               self.sig_pos = (self.pos[0]-1, self.pos[1]+1)
            elif self.pos[0]==0 and self.pos[1]!=pos_cargador[1]:
               self.sig_pos = (self.pos[0], self.pos[1]+1)
            elif self.pos[0]!=0 and self.pos[1]==pos_cargador[1]:
               self.sig_pos = (self.pos[0]-1, self.pos[1])

        #superior der
        elif pos_cargador[0]!=0 and pos_cargador[1]!=0:
            if self.pos[0]!=0 and self.pos[1]!=0 :
               self.sig_pos = (self.pos[0]+1, self.pos[1]+1)
            elif self.pos[0]==pos_cargador[0] and self.pos[1]!=pos_cargador[1]:
               self.sig_pos = (self.pos[0], self.pos[1]+1)
            elif self.pos[0]!=pos_cargador[0] and self.pos[1]==pos_cargador[1]:
               self.sig_pos = (self.pos[0]+1, self.pos[1])

        #inferior der
        elif pos_cargador[0]!=0 and pos_cargador[1]==0:
            if self.pos[0]!=0 and self.pos[1]!=0 :
               self.sig_pos = (self.pos[0]+1, self.pos[1]-1)
            elif self.pos[0]==pos_cargador[0] and self.pos[1]!=0:
               self.sig_pos = (self.pos[0], self.pos[1]-1)
            elif self.pos[0]!=pos_cargador[0] and self.pos[1]==0:
               self.sig_pos = (self.pos[0]+1, self.pos[1])
        
        #si hay obstaculos
        while self.sig_pos not in posiciones_disponibles and self.sig_pos not in posiciones_cargadores:   
                mov1 = np.random.choice([0, 1, -1], size=1, replace=True)
                mov2 = np.random.choice([0, 1, -1], size=1, replace=True)
                self.sig_pos = (self.pos[0]+int(mov1), self.pos[1]+int(mov2))

        #si esta sucia    
        for celda in celdas_sucias:
            if self.sig_pos == celda.pos:
                celda.sucia=False

    #Cargar robot
    def cargar(self):
        self.carga+=25
        if self.carga>=99:
            self.carga=99
        self.sig_pos=self.pos

    #STEP
    def step(self):
        vecinos = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False)

        for vecino in vecinos:
            if isinstance(vecino, (Caja, Robot)):
                vecinos.remove(vecino)

    #Avanzar
    def advance(self):
        if self.pos != self.sig_pos:
            self.movimientos += 1

        if self.carga > 0:
            self.model.grid.move_agent(self, self.sig_pos)

    
class Habitacion(Model):
    def __init__(self, M: int, N: int,
                 num_agentes: int = 5,
                 ):

        self.num_agentes = num_agentes

        self.grid = MultiGrid(M, N, False)
        self.schedule = SimultaneousActivation(self)


        # posicionamiento de cargadores
        global posiciones_cargadores
        posiciones_cargadores= ((0, 0), (0, N-1), (M-1, 0), (M-1, N-1))

        for id, pos in enumerate(posiciones_cargadores):
            cargador = Cargador(int(f"{num_agentes}0{id}") + 1, self)
            self.grid.place_agent(cargador, pos)

        global posiciones_disponibles
        posiciones_disponibles = [pos for _, pos in self.grid.coord_iter() if pos not in posiciones_cargadores]

        self.datacollector = DataCollector(
            model_reporters={"Grid": get_grid},
        )

        
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

def get_grid(model: Model) -> np.ndarray:
    """
    Método para la obtención de la grid y representarla en un notebook
    :param model: Modelo (entorno)
    :return: grid
    """
    grid = np.zeros((model.grid.width, model.grid.height))
    for cell in model.grid.coord_iter():
        cell_content, pos = cell
        x, y = pos
        for obj in cell_content:
            if isinstance(obj, Robot):
                grid[x][y] = 2
            elif isinstance(obj, Celda):
                grid[x][y] = int(obj.sucia)
    return grid

def get_movimientos(agent: Agent) -> dict:
    if isinstance(agent, Robot):
        return {agent.unique_id: agent.movimientos}

