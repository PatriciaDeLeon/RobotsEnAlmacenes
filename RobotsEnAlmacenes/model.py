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

class Estante(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        
class Cargador(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

class Caja(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.sig_pos = None
        self.movimientos = 0
        self.objetivo = None
        self.id = ""

class Robot(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.sig_pos = None
        self.movimientos = 0
        self.carga = 100
        self.objetivo = None
        self.celdas_sucias = 0

    # ✓ Función que encuentra las celdas disponibles alrededor de un robot
    def buscar_celdas_disponibles(self, tipo_agente):
        # Encuentra los vecinos
        vecinos = self.model.grid.get_neighbors(self.pos, moore = True, include_center = False)

        # Lista de celdas
        celdas = list()

        # Para cada uno de los vecinos
        for vecino in vecinos:
            # Si el elemento es una instancia del elemento del tipo de agente
            if isinstance(vecino, tipo_agente):
                celdas.append(vecino) # Lo mete al arreglo de celdas

        # Lista de celdas disponibles
        celdas_disponibles = list()

        # Por cada una de las celdas
        for celda in celdas:
            # Se obtiene la posición de cada una de las celdas y puede incluir varios agentes y otros objetos en la celda.
            posicion_celda = self.model.grid.get_cell_list_contents(celda.pos)
            # Esto lo hace para evitar una celda ocupada por un robot
            robots_cargando = [agente for agente in posicion_celda if isinstance(agente, Robot)]

            # Si no están esos robots 
            if not robots_cargando:
                # Mete la celda a una disponible
                celdas_disponibles.append(celda)

        # Se devuelven las celdas disponibles
        return celdas_disponibles

    # ✓ Función que encuentra una celda sucia y procede a limpiarla
    def limpiar_una_celda(self, celdas_sucias):
        # De lo contrario, comienza la limpieza y elige una celda random de la lista de celdas sucias
        celda_elegida = self.random.choice(celdas_sucias)
        # Ahora, marca esa celda sucia como limpia
        celda_elegida.sucia = False
        # Disminuye de las celdas sucias esa celda
        self.celdas_sucias -= 1
        # La siguiente posición es la nueva posición a limpiar
        self.sig_pos = celda_elegida.pos

    # ✓ Función que selecciona la nueva posición a avanzar
    def seleccionar_nueva_pos(self):
        # Encuentra todas las celdas disponibles
        celdas_disponibles = self.buscar_celdas_disponibles((Celda))
        # Si no hay celdas disponibles
        if len(celdas_disponibles) == 0:
            # El robot se queda quieto
            self.sig_pos = self.pos
            return # Sale de la función
        else:
            # De lo contrario, busca una posición random dentro de los vecinos
            self.sig_pos = self.random.choice(celdas_disponibles).pos

    # ✓ Función que calcula la distancia entre 2 puntos
    def distancia_euclidiana(self, punto1, punto2):
        return math.sqrt(pow(punto1[0] - punto2[0], 2) + pow(punto1[1] - punto2[1], 2))
    
    # ✓ Función que selecciona un cargador y lo establece como objetivo del robot
    def seleccionar_cargador(self, cargadores):
        # Se inicializan variables del cargador más cercano y la distancia mínima
        cargador_mas_cercano = cargadores[0]
        distancia_minima = float("infinity")

        # Por cada cargador en la lista de cargadores
        for cargador in cargadores:
            # Se encuentra la distancia actual entre la posición del robot y el cargador
            distancia_actual = self.distancia_euclidiana(cargador, self.pos)  
            # Si la distancia actual encontrada es menor a la distancia mínima
            if distancia_actual < distancia_minima:
                # La distancia mínima se reemplaza por la distancia actual
                distancia_minima = distancia_actual
                # El cargador se asigna como el más cercano
                cargador_mas_cercano = cargador

        # El objetivo es el cargador más cercano
        self.objetivo = cargador_mas_cercano

    # ✓ Función que mueve un robot a una posición específica
    def viajar_a_objetivo(self):  
        # Si tiene como objetivo ir a un cargador    
        if self.objetivo in self.model.pos_cargadores:
            # Busca las celdas en donde están los cargadores
            celdas_objetivo = self.buscar_celdas_disponibles((Celda, Cargador))
        else:
            # De lo contrario, busca cualquier tipo de celda disponible
            celdas_objetivo = self.buscar_celdas_disponibles((Celda))

        # Si no hay celdas disponibles
        if len(celdas_objetivo) == 0:
            # El robot se queda quieto
            self.sig_pos = self.pos
            return # Sale de la función
        else:
            # De lo contrario, ordena de menor a mayor las distancias entre el objetivo y el siguiente paso a dar
            celdas_objetivo = sorted(celdas_objetivo, key = lambda vecino: self.distancia_euclidiana(self.objetivo, vecino.pos))
            # Selecciona el recorrido más corto (el menor del sorted) como siguiente posición
            self.sig_pos = celdas_objetivo[0].pos
            # Se obtiene la posición de cada una de las celdas y puede incluir varios agentes y otros objetos en la celda.
            celdas = self.model.grid.get_cell_list_contents(self.sig_pos)
            # Por cada celda en las celdas
            for celda in celdas:
                # Si en el proceso de llegar al cargador hay una celda sucia
                if isinstance(celda, Celda) and celda.sucia:
                    # Procede a limpiarla
                    celda.sucia = False
    
    # ✓ Función que carga la batería de un robot
    def cargar_robot(self):
        # Si la carga del robot es menor a 100
        if self.carga < 100:
            # Se aumenta la carga en 25
            self.carga += 25
            # Esto asegura que la carga no exceda el valor máximo de 100
            self.carga = min(self.carga, 100)
            # Mientras esté cargando, el robot se queda quieto
            self.sig_pos = self.pos

            # Si la carga es 100, cantidad de cargas completas aumenta en 1 (para gráficas)
            if self.carga == 100:
                self.model.cantidad_recargas += 1

    # ✓ Función para verificar si un robot puede ayudar a resolver un problema
    def pedir_ayuda(self, pos):
        # Si el robot está buscando un cargador o tiene basura a su alrededor 
        if self.celdas_sucias > 0 or self.objetivo:
            # No se procesa la solicitud
            return False
        else:
            # De lo contrario, el objetivo toma lugar como la solicitud
            self.objetivo = pos
            # Se procesa la solicitud
            return True
    
    # ✓ Función para encontrar todos las celdas vecinas que están sucias
    @staticmethod
    def buscar_celdas_sucias(lista_de_vecinos):
        # Se inicializa una lista de celdas sucias
        celdas_sucias = list()

        # Para cada celda vecina
        for vecino in lista_de_vecinos:
            # Si se encuentra sucia
            if isinstance(vecino, Celda) and vecino.sucia:
                # Se agrega a la lista de celdas sucias
                celdas_sucias.append(vecino)

        # Se devuelven las celdas sucias
        return celdas_sucias

    # ✓ Función encargada de ejecutar un paso en la simulación 
    def step(self):
        # El robot llegó a su objetivo
        if self.pos == self.objetivo:
            # Se desmarca el objetivo
            self.objetivo = None
        
        # REGLAS DE LA SIMULACIÓN
        # 1. El robot se encuentra cargándose
        if self.carga < 100 and self.pos in self.model.pos_cargadores:
            # Aumentar la carga
            self.cargar_robot()
        # 2. El robot tiene un cargador asignado y está viajando hacia este
        elif self.objetivo:
            # Acercarse al cargador
            self.viajar_a_objetivo()
        # 3. El robot tiene batería baja y necesita cargarse
        elif self.carga <= 30:
            # Se le asigna el cargador más cercano y se acerca al cargador
            self.seleccionar_cargador(self.model.pos_cargadores)
            self.viajar_a_objetivo()
        # 4. El robot se encarga de limpiar celdas
        else:
            # Obtiene las celdas sucias
            celdas_sucias = self.buscar_celdas_sucias(self.buscar_celdas_disponibles(Celda))
            # Actualiza el número de celdas sucias alrededor
            self.celdas_sucias = len(celdas_sucias)
            # Si el tamaño de las celdas sucias es 0
            if self.celdas_sucias == 0:
                # El robot se mueve a una posición random o se queda quieto
                self.seleccionar_nueva_pos()
            else:
                # De lo contrario, si el número de celdas sucias es mayor o igual a 4
                if self.celdas_sucias >= 4:
                    # Se agrega un problema
                    self.model.pedir_ayuda_aux(self.pos, self.celdas_sucias)
                
                # Limpia una celda
                self.limpiar_una_celda(celdas_sucias)

        # Se avanza en la simulación
        self.advance()

    # ✓ Función encargada para avanzar al robot en la simulación
    def advance(self):
        # Si el robot no se quedó quieto
        if self.pos != self.sig_pos and self.carga > 0:
            # Aumenta el número de movimientos en el robot y para el análisis de datos
            self.movimientos += 1
            self.model.movimientos += 1

            # Se disminuye la carga en 1
            self.carga -= 1
            self.model.grid.move_agent(self, self.sig_pos)


class Habitacion(Model):
    def __init__(self, M: int, N: int,
                 num_agentes: int = 5,
                 porc_celdas_sucias: float = 0.6,
                 porc_muebles: float = 0.1,
                 modo_pos_inicial: str = 'Fija',
                 ):

        self.num_agentes = num_agentes
        self.porc_celdas_sucias = porc_celdas_sucias
        self.porc_muebles = porc_muebles
        self.todas_celdas_limpias = False

        # Calcula la posición central del plano cartesiano más un avance en las celdas
        center_x = (M // 2) + 5
        center_y = (N // 2) + 5

        # Se guardan las posiciones de los cargadores
        self.pos_cargadores = [
            (center_x, center_y),
            (center_x - 11, center_y),
            (center_x, center_y - 11),
            (center_x - 11, center_y - 11)
        ]

# Se guardan las posiciones de los cargadores
  
        self.pos_estantes = [
            for i in range()
            x=random.choice(0,4)
            y=random.choice(0,1)
            pos_estantes.append((x,y))
        ]

        # Inicializamos un listado de problemas
        self.problemas = list()

        # Inicialización de variables para gráficas
        self.tiempo = 0
        self.movimientos = 0
        self.cantidad_recargas = 0

        # Permite la habilitación de las capas en el ambiente
        self.grid = MultiGrid(M, N, False)
        # Permite que los robots se activen en un órden simultáneo
        self.schedule = SimultaneousActivation(self)

        posiciones_disponibles = [pos for _, pos in self.grid.coord_iter()]

        # Posicionamiento de cargadores
        for id, pos in enumerate(self.pos_cargadores):
            cargador = Cargador(int(f"{num_agentes}0{id}") + 1, self)
            self.grid.place_agent(cargador, pos)
            posiciones_disponibles.remove(pos)

        # Posicionamiento de muebles
        num_muebles = int(M * N * porc_muebles)
        posiciones_muebles = self.random.sample(posiciones_disponibles, k = num_muebles)
        for id, pos in enumerate(posiciones_muebles):
            mueble = Estante(int(f"{num_agentes}0{id}") + 1, self)
            self.grid.place_agent(mueble, pos)
            posiciones_disponibles.remove(pos)

        # Posicionamiento de celdas sucias
        self.celdas_sucias = int(M * N * porc_celdas_sucias)
        posiciones_celdas_sucias = self.random.sample(posiciones_disponibles, k = self.celdas_sucias)
        for id, pos in enumerate(posiciones_disponibles):
            suciedad = pos in posiciones_celdas_sucias
            celda = Celda(int(f"{num_agentes}{id}") + 1, self, suciedad)
            self.grid.place_agent(celda, pos)

        # Posicionamiento de agentes robot
        if modo_pos_inicial == 'Aleatoria':
            pos_inicial_robots = self.random.sample(posiciones_disponibles, k = num_agentes)
        else: # 'Fija'
            pos_inicial_robots = [(1, 1)] * num_agentes
        for id in range(num_agentes):
            robot = Robot(id, self)
            self.grid.place_agent(robot, pos_inicial_robots[id])
            self.schedule.add(robot)

        # Variables utilizadas para las gráficas en el server.py
        self.datacollector = DataCollector(
            model_reporters = {"Grid": get_grid,
                                "CeldasSucias": get_sucias,
                                "Tiempo": "tiempo",
                                "Movimientos": "movimientos",
                                "Recargas": "cantidad_recargas"
                            })

    # ✓ Función encargada de ejecutar un paso en la simulación 
    def step(self):
        # Recolecta la información de las gráficas
        self.datacollector.collect(self)
        
        # Si no está todo limpio
        if not self.salon_limpio():
            # Programa un step
            self.schedule.step()
            
            # Se obtienen todas las celdas sucias
            celdas_sucias = self.get_celdas_sucias()
            # Selecciona aleatoriamente un grupo de celdas sucias para notificar un problema
            grupo_celdas_sucias = self.random.sample(celdas_sucias, k = min(len(celdas_sucias), self.num_agentes))
            # Por cada celda sucia en el grupo de esas celdas
            for celda_sucia in grupo_celdas_sucias:
                # Crea un problema
                self.pedir_ayuda_aux(celda_sucia, 1)

            # Notifica el problema a todos los robots
            self.notificar_problema()
            # Se aumenta el tiempo en 1 (Para gráfica)
            self.tiempo += 1

            # Verifica si todas las celdas sucias han sido limpiadas
            if len(self.get_celdas_sucias()) == 0:
                self.todas_celdas_limpias = True
        else:
            # Si todas las celdas sucias han sido limpiadas, finaliza la simulación
            self.running = False

    # ✓ Función que calcula la distancia entre 2 puntos
    def distancia_euclidiana(self, punto1, punto2):
        return math.sqrt(pow(punto1[0] - punto2[0], 2) + pow(punto1[1] - punto2[1], 2))

    # ✓ Función que verifica que todo el salón esté limpio
    def salon_limpio(self):
        for (content, pos) in self.grid.coord_iter():
            for celda in content:
                if isinstance(celda, Celda) and celda.sucia:
                    return False
        return True
    
    # ✓ Función que obtiene la posición actual de las celdas sucias
    def get_celdas_sucias(self):
        celdas_sucias = list()
        for(content, pos) in self.grid.coord_iter():
            for celda in content:
                if isinstance(celda, Celda) and celda.sucia:
                    celdas_sucias.append(pos)
        return celdas_sucias
    
    # ✓ Función que obtiene la posición actual de los robots
    def get_robots(self):
        robots = list()
        for (content, pos) in self.grid.coord_iter():
            for celda in content:
                if isinstance(celda, Robot):
                    robots.append((celda, pos))
        return robots
    
    # ✓ Función para añadir problemas a la lista de estos
    def pedir_ayuda_aux(self, pos, num_sucias):
        self.problemas.append((num_sucias, pos))

    # ✓ Función que notifica que existe mucha basura en un área a todos los robots
    def notificar_problema(self):
        # Organiza los problemas por gravedad (cantidad de celdas sucias) de mayor a menor
        self.problemas = sorted(self.problemas, key = lambda problema: problema[0], reverse = True)
        # Obtiene la posición de todos los robots
        posiciones_robots = self.get_robots()

        # Por cada problema en la lista de problemas
        for problema in self.problemas:
            # Verifica cuál robot está más cerca del problema (la mínima distancia)
            posiciones_robots = sorted(posiciones_robots, key = lambda posicion_robot: self.distancia_euclidiana(problema[1], posicion_robot[1]))
            # Se examina cada posición del robot
            for posicion_robot in posiciones_robots:
                # Se verifica si el robot puede o no encargarse del problema
                resultado = posicion_robot[0].pedir_ayuda(problema[1])
                # En caso de que sí se pueda, se le asigna el problema
                if resultado:
                    break
        
        # Limpia la lista de problemas para no iterar todo en cada step de la simulación
        self.problemas = list()

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
    return sum_sucias / model.celdas_sucias