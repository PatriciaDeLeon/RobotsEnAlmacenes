from mesa.model import Model
from mesa.agent import Agent
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector

import numpy as np
import math

class Celda(Agent):
    def __init__(self, unique_id, model, suciedad: bool = False):
        super().__init__(unique_id, model)
        self.sucia = suciedad


class Cargador(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

class Mueble(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
class RobotLimpieza(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.sig_pos = None
        self.movimientos = 0
        self.carga = 100

    def limpiar_una_celda(self, lista_de_celdas_sucias):
        celda_a_limpiar = self.random.choice(lista_de_celdas_sucias)
        celda_a_limpiar.sucia = False
        self.sig_pos = celda_a_limpiar.pos

    def seleccionar_nueva_pos(self, lista_de_vecinos):
        self.sig_pos = self.random.choice(lista_de_vecinos).pos
        while self.sig_pos not in posiciones_disponibles:
            self.sig_pos = self.random.choice(lista_de_vecinos).pos

    @staticmethod
    def buscar_celdas_sucia(lista_de_vecinos):
        # #Opción 1
        # return [vecino for vecino in lista_de_vecinos
        #                 if isinstance(vecino, Celda) and vecino.sucia]
        # #Opción 2
        celdas_sucias = list()
        for vecino in lista_de_vecinos:
            if isinstance(vecino, Celda) and vecino.sucia:
                celdas_sucias.append(vecino)
        return celdas_sucias
    
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

    def cargar(self):
        self.carga+=25
        if self.carga>=99:
            self.carga=99
        self.sig_pos=self.pos

    def step(self):
        vecinos = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False)

        for vecino in vecinos:
            if isinstance(vecino, (Mueble, RobotLimpieza)):
                vecinos.remove(vecino)

        celdas_sucias = self.buscar_celdas_sucia(vecinos)

        if self.pos in posiciones_cargadores:#esta en un cargador
            if self.carga<99: #cargar
                self.cargar()  
            else: #ya termino de cargar
                if len(celdas_sucias) == 0:
                    self.seleccionar_nueva_pos(vecinos)
                else:
                    self.limpiar_una_celda(celdas_sucias)
        else:#no esta en un cargador
            if self.carga<60:
              pos_cargador=self.buscar_cargadores(posiciones_cargadores, self.pos)
              self.moverse_a_cargador(pos_cargador, celdas_sucias)
            else:
                if len(celdas_sucias) == 0:
                    self.seleccionar_nueva_pos(vecinos)
                else:
                    self.limpiar_una_celda(celdas_sucias)

    def advance(self):
        if self.pos != self.sig_pos:
            self.movimientos += 1

        if self.carga > 0:
            self.model.grid.move_agent(self, self.sig_pos)
            if self.pos not in posiciones_cargadores:
                self.carga -= 1

    
    
        

class Habitacion(Model):
    def __init__(self, M: int, N: int,
                 num_agentes: int = 5,
                 porc_celdas_sucias: float = 0.6,
                 porc_muebles: float = 0.1,
                 modo_pos_inicial: str = 'Fija',
                 num_cargadores: int = 4
                 ):

        self.num_agentes = num_agentes
        self.porc_celdas_sucias = porc_celdas_sucias
        self.porc_muebles = porc_muebles
        
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

        # Posicionamiento de muebles
        num_muebles = int(M * N * porc_muebles)
        posiciones_muebles = self.random.sample(posiciones_disponibles, k=num_muebles)
        for id, pos in enumerate(posiciones_muebles):
            mueble = Mueble(int(f"{num_agentes}0{id}") + 1, self)
            self.grid.place_agent(mueble, pos)
            posiciones_disponibles.remove(pos)


        # Posicionamiento de celdas sucias
        self.num_celdas_sucias = int(M * N * porc_celdas_sucias)
        posiciones_celdas_sucias = self.random.sample(
            posiciones_disponibles, k=self.num_celdas_sucias)

        for id, pos in enumerate(posiciones_disponibles):
            suciedad = pos in posiciones_celdas_sucias
            celda = Celda(int(f"{num_agentes}{id}") + 1, self, suciedad)
            self.grid.place_agent(celda, pos)

        # Posicionamiento de agentes robot
        if modo_pos_inicial == 'Aleatoria':
            pos_inicial_robots = self.random.sample(posiciones_disponibles, k=num_agentes)
        else:  # 'Fija'
            pos_inicial_robots = [(10, 3)] * num_agentes

        for id in range(num_agentes):
            robot = RobotLimpieza(id, self)
            self.grid.place_agent(robot, pos_inicial_robots[id])
            self.schedule.add(robot)


        self.datacollector = DataCollector(
            model_reporters={"Grid": get_grid, "Cargas": get_cargas,
                             "CeldasSucias": get_sucias},
        )

    def step(self):
        self.datacollector.collect(self)

        self.schedule.step()

    def todoLimpio(self):
        for (content, x, y) in self.grid.coord_iter():
            for obj in content:
                if isinstance(obj, Celda) and obj.sucia:
                    return False
        return True


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
            if isinstance(obj, RobotLimpieza):
                grid[x][y] = 2
            elif isinstance(obj, Celda):
                grid[x][y] = int(obj.sucia)
    return grid


def get_cargas(model: Model):
    return [(agent.unique_id, agent.carga) for agent in model.schedule.agents]


def get_sucias(model: Model) -> int:
    """
    Método para determinar el número total de celdas sucias
    :param model: Modelo Mesa
    :return: número de celdas sucias
    """
    sum_sucias = 0
    for cell in model.grid.coord_iter():
        cell_content, pos = cell
        for obj in cell_content:
            if isinstance(obj, Celda) and obj.sucia:
                sum_sucias += 1
    return sum_sucias / model.num_celdas_sucias


def get_movimientos(agent: Agent) -> dict:
    if isinstance(agent, RobotLimpieza):
        return {agent.unique_id: agent.movimientos}
    # else:
    #    return 0
