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
        self.producto=""
        self.ocupado=0
        
class Cargador(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

class Caja(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.sig_pos = None
        self.movimientos = 0
        self.objetivo = None
        self.producto=""

    # ✓ Función encargada para avanzar a la caja en la simulación
    def advance(self):
        # Dejaron la caja en la salida
        if self.pos == (0,15):
                #desaparecerla
                self.model.schedule.remove(self)
                self.model.grid.remove_agent(self)
        else:
            celdadeCarga = self.model.grid.get_cell_list_contents((0,10)) #celda de salida

            #Solo en el momento que la caja apenas se va a salir de la entrada
            if self.sig_pos!=self.pos and self.pos==(0,10) and self.sig_pos != None:
                #crea una nueva caja con producto igual al primer producto que todavia tenga pedido
                for product, cantidad in self.model.pedido.items():
                    if cantidad[0]!=0:
                        nueva_caja = Caja(self.unique_id+1, self.model) 
                        nueva_caja.pos = celdadeCarga[0].pos
                        nueva_caja.producto=product
                        self.model.grid.place_agent(nueva_caja, self.pos)
                        self.model.schedule.add(nueva_caja)
                        break

            if self.sig_pos!=None:#Mover la caja en el grid
                self.model.grid.move_agent(self, self.sig_pos)

class Robot(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.sig_pos = None
        self.movimientos = 0
        self.carga = 100
        self.objetivo = None
        self.pos_inicial=None

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

                #Eliminar los estantes de disponibles a menos que su objetivo sea un estante
                if isinstance(vecino, Caja) or  isinstance(vecino, Estante):
                    if self.objetivo !=vecino or (self.objetivo.pos in self.model.pos_estantes and vecino!=self.objetivo) :
                        celdas.remove(vecino) # Lo sacamos

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

    # ✓ Función que calcula la distancia entre 2 puntos
    def distancia_euclidiana(self, punto1, punto2):
        return math.sqrt(pow(punto1[0] - punto2[0], 2) + pow(punto1[1] - punto2[1], 2))
    
    # ✓ Función que selecciona un cargador y lo establece como objetivo del robot
    def seleccionar_objetivo(self, objetivos):
        # Se inicializan variables del cargador más cercano y la distancia mínima
        objetivo_mas_cercano = objetivos[0]
        distancia_minima = float("infinity")

        # Por cada cargador en la lista de cargadores
        for objetivo in objetivos:
            # Se encuentra la distancia actual entre la posición del robot y el cargador
            distancia_actual = self.distancia_euclidiana(objetivo.pos, self.pos)  
            # Si la distancia actual encontrada es menor a la distancia mínima
            if distancia_actual < distancia_minima:
                # La distancia mínima se reemplaza por la distancia actual
                distancia_minima = distancia_actual
                # El cargador se asigna como el más cercano
                objetivo_mas_cercano = objetivo

        # El objetivo es el cargador más cercano
        self.objetivo = objetivo_mas_cercano

    # ✓ Función que mueve un robot a una posición específica
    def viajar_a_objetivo(self):  
        cajas= self.model.get_cajas()
        posi_cajas=[]
        for caja in cajas:
            posi_cajas.append(caja.pos)
        # Si tiene como objetivo ir a un cargador    
        if self.objetivo.pos in self.model.pos_cargadores:
            # Busca las celdas en donde están los cargadores
            celdas_objetivo = self.buscar_celdas_disponibles((Celda, Cargador))
        elif self.objetivo.pos in posi_cajas:
            # Busca las celdas en donde están las cajas
            celdas_objetivo = self.buscar_celdas_disponibles((Celda, Caja))
        elif self.objetivo.pos in self.model.pos_estantes:
            # Busca las celdas en donde están los estantes
            celdas_objetivo = self.buscar_celdas_disponibles((Celda, Estante))
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
            celdas_objetivo = sorted(celdas_objetivo, key = lambda vecino: self.distancia_euclidiana(self.objetivo.pos, vecino.pos))
            # Selecciona el recorrido más corto (el menor del sorted) como siguiente posición
            self.sig_pos = celdas_objetivo[0].pos
            print("AQUI", self.unique_id, self.sig_pos)
            
    
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
    
    # ✓ Función encargada de elegir una posicion aleatoria cuando esta abajo de un estante y no tiene objetivo 
    def seleccionar_pos_aleatoria(self, cajas, estantes, robots):
        vecinos =self.model.grid.get_neighborhood(
        self.pos, moore=True, include_center=False)
        vecinosF =list(vecinos)
        for vecino in vecinos:
            celda = self.model.grid.get_cell_list_contents(vecino) #celda de salida
            for agente in celda:
                if agente in cajas or agente in estantes or agente in robots:
                    vecinosF.remove(vecino) # Lo sacamos
                    break
        self.sig_pos = self.random.choice(vecinosF)

    # ✓ Función encargada de moverse a posicion inicial
    def moverse_posInicial(self):
        self.objetivo=self.pos_inicial
        self.viajar_a_objetivo()

    # ✓ Función encargada de ejecutar un paso en la simulación 
    def step(self):

        #Listas de agentes
        cargadores=self.model.get_cargadores()
        cajas=self.model.get_cajas()
        estantes=self.model.get_estantes()
        robots=self.model.get_robots()
        
        MitadPedidoCompleto = all(valor[0]==0 for valor in self.model.pedido.values())
        PedidoCompleto = all(valor[1] == 0 and valor[0]==0 for valor in self.model.pedido.values())

        aux=0 #variable que ayuda a saber cuando un robot esta un estante porque acaba de dejar una caja o porque va a recoger una
        celdadeCarga = self.model.grid.get_cell_list_contents((0,15)) #celda de salida

        #Lista de objetivos que ya marcaron los otros robots
        objetivos=[]
        for robot in robots:
            if robot!=self:
                objetivos.append(robot.objetivo)
        
        #Lista de objetivos que ya marcaron los otros robots
        pos_robots=[]
        for robot in robots:
            if robot!=self:
                pos_robots.append(robot.pos)


        # El robot llegó a su objetivo
        if self.objetivo is not None:
            if self.pos == self.objetivo.pos:
                #si su objetivo era una caja se guarda el producto que traia la caja para despues poder saber que tipo de estante hay que buscar
                if self.objetivo in cajas:
                    objetivo_producto=self.objetivo.producto
                #si el objetivo era un estante se cambia aux para despues poder saber que acabamos de dejar una caja
                if self.objetivo in estantes:
                    aux=1
                else: 
                    aux=0
                #para que cuando se llegue a la pos_inicial no se desmarque y no entre en el estado de buscar caja
                if self.objetivo !=self.pos_inicial:
                    # Se desmarca el objetivo
                    self.objetivo = None
        
        # REGLAS DE LA SIMULACIÓN
        # 1. El robot se encuentra cargándose
        if self.carga < 100 and self.pos in self.model.pos_cargadores:
            # Aumentar la carga
            print(self.unique_id,"estoy cargando")
            self.cargar_robot()

        # 2. El robot tiene un cargador y está viajando hacia este
        elif self.objetivo in cargadores:
            # Acercarse al cargador
            self.viajar_a_objetivo()
            print(self.unique_id,"estoy vianjando a cargador")

        # 3. Ya esta en la posicion de entrada para recoger
        elif self.pos == (0,10):
            for estante in estantes: #encuentra un estante del mismo tipo de la caja que esta recogiendo y que no este ocupado
                if estante.producto==objetivo_producto and estante.ocupado==0:
                    print(self.unique_id,"llevando a estante")
                    self.objetivo=estante
                    self.objetivo.ocupado=1 #y el estante se marca como ocupado
                    break
            #mueve la caja consigo
            for caja in cajas:
                if caja.pos==self.pos:
                    self.viajar_a_objetivo()
                    caja.sig_pos=self.sig_pos

        # 4. El robot tiene un estante y está viajando hacia este
        elif self.objetivo in estantes:
            for caja in cajas:
                if caja.pos==self.pos: #mueve la caja consigo
                    self.viajar_a_objetivo()
                    caja.sig_pos=self.sig_pos

        #5. Esta en algun estante para llevarla a salida
        elif self.pos in self.model.pos_estantes and aux==0:
            print(self.unique_id, "llevando a salida")
            self.objetivo=celdadeCarga[0] #su objetivo es la celda de salida
            self.viajar_a_objetivo()
            for caja in cajas: #mueve la caja consigo
                if caja.pos==self.pos:
                    caja.sig_pos=self.sig_pos
            for estante in estantes:
                if estante.pos == self.pos:
                    estante.ocupado=0

        #6. Esta viajando a salida
        elif self.objetivo == celdadeCarga[0]:
            self.viajar_a_objetivo()
            for caja in cajas:
                if caja.pos==self.pos:
                    caja.sig_pos=self.sig_pos

        #7. Esta yendo por una caja
        elif self.objetivo in cajas:
            self.viajar_a_objetivo()

        # 8. El robot tiene batería baja y necesita cargarse, entra aqui hasta su objetivo ya no sea un estante o la celda de salida
        elif self.carga <= 50 and self.objetivo == None :
            # Se le asigna el cargador más cercano y se acerca al cargador
            self.seleccionar_objetivo(cargadores)
            self.viajar_a_objetivo()
            print(self.unique_id,"necesito cargarme")

        # 9. El robot esta buscando caja
        elif self.objetivo == None or self.objetivo==self.pos_inicial:
            
            #Hay cajas en la entrada
            if not MitadPedidoCompleto:      
                for product, cantidad in self.model.pedido.items():
                    if cantidad[0] != 0:
                        break_outer = False  # Flag to signal if a break is requested
                        for caja in cajas:
                            if caja.pos == (0,10):
                                #si la caja del camion no es objetivo
                                if caja not in objetivos and caja.pos not in pos_robots:
                                    print(self.unique_id, "yendo a entrada")
                                    self.objetivo = caja #su objetivo es esa caja
                                    self.viajar_a_objetivo()
                                    self.model.pedido[product]=[cantidad[0]-1,cantidad[1]] #se disminuye uno al pedido
                                    break_outer = True  # Set the flag to True to request a break
                                    break
                        if break_outer:
                            break  # Break out of the outer loop as well
            
            #No encontro cajas para llevar a estante, pasa a buscar cajas para recoger de estantes
            if self.objetivo==None:
                for product, cantidad in self.model.pedido.items():
                    if cantidad[1] != 0:
                        break_outer = False  # Flag to signal if a break is requested
                        for caja in cajas:
                            if caja.pos in self.model.pos_estantes and caja.producto == product:
                                #si la caja del estante no ha sido marcada como objetivo
                                if caja not in objetivos and caja.pos not in pos_robots:
                                    print(self.unique_id, "yendo a estante a recoger")
                                    self.objetivo = caja #su objetivo es esa caja
                                    self.viajar_a_objetivo()
                                    self.model.pedido[product]=[cantidad[0],cantidad[1]-1] #se disminuye uno al pedido
                                    break_outer = True  # Set the flag to True to request a break
                                    break
                        if break_outer:
                            break  # Break out of the outer loop as well
            
            #No hay cajas en la entrada ni para recoger de estantes
            if PedidoCompleto == True:
                self.moverse_posInicial()
                if self.pos==self.pos_inicial.pos:
                    self.sig_pos=self.pos
            #El pedido no esta completo, no tiene objetivo, pero ya esta en su posicion inicial
            elif self.objetivo==None and self.pos == self.pos_inicial.pos or self.objetivo==self.pos_inicial and self.pos == self.pos_inicial.pos:
                self.sig_pos=self.pos
            #El pedido no esta completo, no tiene objetivo, pero todavia no llega a su posicion inicial
            elif self.objetivo==None and self.pos!=self.pos_inicial.pos or self.objetivo==self.pos_inicial: 
                self.moverse_posInicial()

        #Para que nunca esten estorbando en la posicion de salida o en un estante
        if self.pos in self.model.pos_estantes and self.objetivo==None:
            print(self.unique_id,"random")
            self.seleccionar_pos_aleatoria(cajas, estantes, robots)
          
        # Se avanza en la simulación
        self.advance()
        
        #Avanzara tambien a las cajas
        for caja in cajas:
            caja.advance()
        
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
                 pedido : dict = {},
                 ):
        
        self.num_agentes = num_agentes
        self.todas_celdas_limpias = False
        self.pedido=pedido

        # Inicialización de variables de datos
        self.tiempo = 0
        self.movimientos = 0
        self.cantidad_recargas = 0

        # Permite la habilitación de las capas en el ambiente
        self.grid = MultiGrid(M, N, False)
        # Permite que los robots se activen en un órden simultáneo
        self.schedule = SimultaneousActivation(self)

        posiciones_disponibles = [pos for _, pos in self.grid.coord_iter()]

        #El primer valor de la lista es la cantidad que se tiene que poner en estante, el segundo los que se tienen que llevar a camion
        pedido['SanAnna Water'] = [2,1]
        pedido['Bio Bottle'] = [2,1]
        pedido['Santhe'] = [2,1]
        pedido['Beauty'] = [2,1]
        pedido['Fruity Touch'] = [2,1]
        pedido['SantAnna Pro'] = [2,1]

        # Se guardan las posiciones de los cargadores
        self.pos_cargadores = [
            (10, 0),
            (11, 0),
            (12, 0),
        ]
        for elemento in self.pos_cargadores:
            posiciones_disponibles.remove(elemento)


        # Se guardan las posiciones de los estantes
        self.pos_estantes = [
            (10, 5), (11,5),(12,5),
            (10, 10),(11,10), (12,10),
            (10, 15),(11,15), (12,15),
            (15, 5), (16,5),(17,5),
            (15, 10),(16,10), (17,10),
            (15, 15),(16,15), (17,15)
        ]
        for elemento in self.pos_estantes:
            posiciones_disponibles.remove(elemento)

        # Se guardan las posiciones de las cajas
        self.pos_cajas = [
            (0, 10), (0,15)
        ]
        posiciones_disponibles.remove((0,10)) #no se eliminar la posicion de salida para que luego pueda haber una Celda ahi y despues usarla como objetivo

        pos_iniciales=[(0,0), (0,1), (1,0), (0,2), (2,0), (0,3), (3,0), (0,4), (4,0), (0,5)]
        # Asignar las posiciones a los primeros num_agentes robots
        self.pos_robots = pos_iniciales[:num_agentes]

         # Posicionamiento de celdas 
        for id, pos in enumerate(posiciones_disponibles):
            celda = Celda(int(f"{1}0{id}") + 1, self)
            self.grid.place_agent(celda, pos)
            self.schedule.add(celda)

        # Posicionamiento de robots
        for id, pos in enumerate(self.pos_robots):
            robot = Robot(int(f"{2}0{id}") + 1, self)
            #Obtener objeto celda en esa pocision
            celda = self.grid.get_cell_list_contents(pos)
            robot.pos_inicial=celda[0] #la posicion inicial del robot(descanso) es esa celda
            self.grid.place_agent(robot, self.pos_robots[id])
            self.schedule.add(robot)

        # Posicionamiento de cargadores
        for id, pos in enumerate(self.pos_cargadores):
            cargador = Cargador(int(f"{3}0{id}") + 1, self)
            self.grid.place_agent(cargador, pos)
            self.schedule.add(cargador)

        # Posicionamiento de estantes con 3 estantes de cada producto
        claves = list(pedido.keys())
        cont=0
        i=0
        for id, pos in enumerate(self.pos_estantes):
            estante = Estante(int(f"{4}0{id}") + 1, self)
            estante.producto = claves[i]
            self.grid.place_agent(estante, pos)
            self.schedule.add(estante)
            cont+=1
            if cont==3:
                i+=1
                cont=0
        
        # Posicionamiento de la caja de entrada inicial de acuerdo al pedido
        for product, cantidad in self.pedido.items():
            if cantidad[0]!=0:
                caja = Caja(int(f"{5}0{1}") + 1, self)
                caja.producto = product
                self.grid.place_agent(caja, self.pos_cajas[0])
                self.schedule.add(caja)
                break
        
        # Variables utilizadas para las gráficas en el server.py
        self.datacollector = DataCollector(
            model_reporters = {"Grid": get_grid})

    # ✓ Función encargada de ejecutar un paso en la simulación 
    def step(self):
        # Recolecta la información de las gráficas
        self.datacollector.collect(self)
        self.schedule.step()
    
    #Funciones para recolectar las listas de agentes
    def get_cargadores(self):
        cargadores = [agente for agente in self.schedule.agents if isinstance(agente, Cargador)]
        return cargadores  
    def get_cajas(self):
        cajas = [agente for agente in self.schedule.agents if isinstance(agente, Caja)]
        return cajas
    def get_estantes(self):
        estantes = [agente for agente in self.schedule.agents if isinstance(agente, Estante)]
        return estantes
    def get_robots(self):
        robots = [agente for agente in self.schedule.agents if isinstance(agente, Robot)]
        return robots
    
#    Método para la obtención de la grid y representarla en un notebook  
def get_grid(model: Model) -> np.ndarray:
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