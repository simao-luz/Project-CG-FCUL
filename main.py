"""
Módulo principal da aplicação.
Desenvolvido por:
    - Diogo Vasconcelos, fc61809
    - Miguel Guise, fc61822
    - Simão da Luz, fc61816
Em: 01/12/2026
"""

import sys
from utils.helpers import *
from utils.variables import *

from car.hood import (draw_hood, 
                  draw_headlight, 
                  v5, v2)

from car.cockpit import (draw_seat,
                     draw_steering_wheel,
                     draw_brakes,
                     draw_pedals,
                     draw_dashboard)

from car.door import (draw_door,
                  draw_door_handle,
                  draw_door_protection)

from car.car_upper_body import (draw_windshield,
                            draw_roll_cage,
                            draw_lat_rearview_mirror,
                            draw_central_rearview_mirror,
                            draw_protection)

from car.rear import (draw_rear_bumper_wall, 
                  draw_rear_light)

from car.wheel import draw_wheel

from scene.outside import (draw_garage_structure, 
                     draw_garage_gate, interact_garage_gate, 
                     start_opening_gate, start_closing_gate,
                     draw_tree,
                     draw_street_light, draw_lamp)

# Classe Node - Base do grafo de cena
#Parametros
#  geom(node): função que desenha a geometria (opcional)
#  transform(node): função que aplica as transformações locais (opcional)
#  updater(node, dt): avança o estado (opcional)
#  state: dicionário com parâmetros arbitrários do nó (ex.: ângulos, escalas)
#         que poderão ser alterados pelos vários eventos da aplicação    

class Node:
    """
    Classe fornecida pelos professores.
    """
    def __init__(self, name, geom=None, transform=None, updater=None, state=None):
        self.name = name
        self.geom = geom
        self.transform = transform  #função de transformação
        self.updater = updater      #será uma função (actualiza o state)
        self.state = state or {}    #parametros da função de update e transform
        self.children = []

    #aqui acrescentam-se os filhos de cada nó
    def add(self, *kids):
        for k in kids:
            self.children.append(k)
        return self

    #aqui faz-se a actualização da geometria
    def update(self, dt):
        if self.updater:
            self.updater(self, dt)
        for c in self.children:
            c.update(dt)

    #é aqui que tudo é desenhado
    def draw(self):
        glPushMatrix()
        if self.transform:
            self.transform(self)
        if self.geom:
            self.geom()
        for c in self.children:
            c.draw()
        glPopMatrix()

win_w, win_h = 800, 600
last_time = 0.0

# Nodes que podem sofrer de alterações !
CAR_NODE = None
DOOR_1_NODE = None
DOOR_2_NODE = None
TRUNK_NODE = None
GARAGE_GATE_NODE = None

# Posição da câmara;
eye_x, eye_y, eye_z = -20.0, 5.5, 0.0
yaw, pitch = 0.0, 0.0
third_person = 0

# Variáveis globais para texturas;
tex_floor = None
tex_car = None
tex_garage_gate = None
tex_garage_outside = None



def tf_transform(tx=0, ty=0, tz=0, 
                 sx=1, sy=1, sz=1,
                 rx=0, ry=0, rz=0, angle=0,
                 switch_side=False):
    """
    Função responsável pela devolução de uma função
    de transformação a um Node; Permite translação,
    escalamento e rotação.
    - tx:          deslocamento em x
    - ty:          deslocamento em y
    - tz:          deslocamento em z
    - sx:          escalamento em x
    - sy:          escalamento em y
    - sz:          escalamento em z
    - rx:          rotação em x
    - ry:          rotação em y
    - rz:          rotação em x
    - angle:       ângulo de rotação
    - switch_side: True if esta à esquerda do carro visto de trás
    """
    def _tf(node):
        glFrontFace(GL_CCW) # Garante CCW ao início de qualquer transformação
        if switch_side:
            glFrontFace(GL_CW)

        glTranslatef(tx, ty, tz)
        glScalef(sx, sy, sz)
        glRotatef(angle, rx, ry, rz)
        if switch_side:
            glScalef(1, 1, -1)
    return _tf

def tf_chain(*tfs):
    """
    Função que recebe várias funções de transform e aplica-as em sequência.
    """
    def _tf(node):
        for f in tfs:
            f(node)
    return _tf

def tf_car_movement(movement_x="movement_x", movement_z="movement_z", car_yaw="car_yaw"):
    """
    Função que recebe que recebe os estados de movimento de um carro e os aplica.
    - movement_x: movimento em x
    - movement_z: movimento em z
    - car_yaw:    rotação do carro
    """
    def _tf(node):
        x = node.state.get(movement_x, 0.0)
        z = node.state.get(movement_z, 0.0)
        angle = node.state.get(car_yaw, 0.0)

        glTranslatef(x, 0.0, z)
        glRotatef(angle, 0.0, 1.0, 0.0)
    return _tf

def tf_door_movement(door_open="door_open", side1=True):
    """
    Função que recebe que recebe o estado de movimento de uma porta e o aplica.
    - door_open: abertura da porta
    - side1:     True se o lado da porta for o direito visto de trás
    """
    def _tf(node):
        open = node.state.get(door_open, 0.0)
        if not side1:
            open = -open
        glRotatef(open, 0.0, 1.0, 0.0)
    return _tf

def tf_steering_wheel_movement(car_node=None):
    """
    Função que recebe que recebe o estado de um carro e o aplica a um volante.
    - car_node: carro que controla o volante
    """
    def _tf(node):
        angle = car_node.state.get("steering", 0.0)
        glRotatef(angle * 10.0, 1.0, 0.0, 0.0)
    return _tf

def tf_trunk_movement(trunk_open="trunk_open", rot_x=0, rot_y=0, rot_z=0):
    """
    Função que recebe que recebe o estado de movimento de um porta-bagagens e o aplica.
    - trunk_open: abertura do porta-bagagens
    - rot_x: deslocação do porta-bagagens nos x para rodar on eixo correto
    - rot_y: deslocação do porta-bagagens nos y para rodar on eixo correto
    - rot_z: deslocação do porta-bagagens nos z para rodar on eixo correto
    """
    def _tf(node):
        angle = node.state.get(trunk_open, 0.0)

        glTranslatef(rot_x, rot_y, rot_z)
        glRotatef(angle, 0.0, 1.0, 0.0)
        glTranslatef(-rot_x, -rot_y, -rot_z)
    return _tf

def tf_wheels_movement(car_node=None, front=False):
    """
    Função que recebe que recebe o estado de um carro e o aplica a uma roda.
    - car_node: carro que controla a roda
    - front: True se a roda for dianteira
    """
    def _tf(node):
        rotation = car_node.state.get("rotation", 0.0)
        if front:
            angle = car_node.state.get("steering", 0.0)
            glRotatef(angle, 0, 1, 0)
            glRotatef(rotation * (REAR_WHEEL_R / FRONT_WHEEL_R), 0.0, 0.0, 1.0)         
        else:
            glRotatef(rotation, 0, 0, 1)

    return _tf


# aqui é construído o grafo de cena
def build_scene():
    """
    Função que cria a cena que vai ser desenhada !
    """
    global CAR_NODE, DOOR_1_NODE, DOOR_2_NODE, TRUNK_NODE, GARAGE_GATE_NODE

    # Nó raiz (mundo) - apenas um contentor
    world = Node("World")

    # Posição e dmento do carro (nó transform)
    car = Node("Car",
               transform=tf_chain(tf_transform(ty=CAR_ELEVATION), # Levanta o carro para não estar
                                                                  # dentro de general_floor !
                                  tf_car_movement(movement_x="movement_x",
                                                  movement_z="movement_z",
                                                  car_yaw="car_yaw"),
                                 ),
               state={"movement_x":0.0, # Deslocamento em x
                      "movement_z":0.0, # Deslocamento em z
                      "car_yaw":0.0,    # Orientação do carro (ângulo)
                      "steering":0.0,
                      "rotation":0.0
                    }
               )
    CAR_NODE = car


    # Nó raiz do capô; É o pai do capô em si!
    hood_floor = Node("Hood_floor",
                      geom=lambda: draw_box(width=HOOD_FLOOR_WIDTH,
                                            height=CAR_FLOOR_DEPTH,
                                            depth=CAR_FLOOR_HEIGHT,
                                            corners=[0, 1],     # Parte da frente curvada...
                                            r=HOOD_SIDE_WIDTH,  # de acordo com o raio dos cilindros do capô

                                            color_front=CAR_CABIN_FLOOR_COLOR,
                                            color_side=CAR_OUTSIDE_COLOR,
                                            color_back=CAR_UNDERNEATH_COLOR),

                      transform=tf_transform(tx=-CABIN_FLOOR_WIDTH * 0.5 - HOOD_FLOOR_WIDTH,
                                             ty=-CAR_FLOOR_HEIGHT * 0.5,
                                             tz=CAR_FLOOR_DEPTH * 0.5,
                                             rx=1.0,
                                             angle=-90.0),
                     )
    
    # Nó do próprio capô; Será o pai dos faróis
    hood = Node("Hood", 
                geom=lambda: draw_hood(color_tex=CAR_OUTSIDE_COLOR,
                                       color_others=HOOD_FRONT_COLOR,
                                       color_rad=RADIATOR_COLOR,
                                       tex_hood=tex_car,
                                       tex_rad=tex_radiator), # A textura abrigará apenas partes do hood (see in: draw_hood)
                transform=tf_chain(tf_transform(rx=1.0, angle=90), # Ajeitamos para orientação normal
                                   tf_transform(tx=HOOD_FLOOR_WIDTH,
                                                ty=HOOD_LAT_HEIGHT,
                                                tz=-CAR_FLOOR_DEPTH, 
                                                ry=1.0, angle=-90))    
               )
    
    # v5 e v2 serão os vértice onde serão colocados o faróis do lado direito e esquerdo, respetivamente. 
    # (see in: draw_hood)
    headlight1 = Node("Headlight1", geom=lambda: draw_headlight(v5, GL_LIGHT1))
    headlight2 = Node("Headlight2", geom=lambda: draw_headlight(v2, GL_LIGHT2))


    # Nó raiz da cabine (a.k.a. habitáculo do veículo)!
    # O chão do habitáculo do veículo é pai dos assentos do travão de mão, da caixa de mudanças 
    # de ambas as portas e de todas as paredes que constituem a cabine!
    cabin_floor = Node("Cabin_floor", 
                       geom=lambda: draw_box(width=CABIN_FLOOR_WIDTH,
                                             height=CAR_FLOOR_DEPTH,
                                             depth=CAR_FLOOR_HEIGHT,

                                             color_front=CAR_CABIN_FLOOR_COLOR,
                                             color_side=CAR_OUTSIDE_COLOR,
                                             color_back=CAR_UNDERNEATH_COLOR,
                                             tex_s=tex_car,
                                             tile_v_side=0.05),

                       transform=tf_transform(tx=-CABIN_FLOOR_WIDTH * 0.5,
                                              ty=-CAR_FLOOR_HEIGHT * 0.5,
                                              tz=CAR_FLOOR_DEPTH * 0.5,
                                              rx=1.0, angle=-90.0)
                      )
    
    seat1 = Node("Seat1",
                 geom=lambda: draw_seat(), # possível definir uma cor
                 transform=tf_transform(tx=CABIN_FLOOR_WIDTH * 0.35, # still x
                                        ty=CAR_FLOOR_DEPTH * 0.28,   # novo z, pela rot do pai
                                        sx=0.35, sy=0.28, sz=0.35,
                                        rx=1.0, angle=90) # Restabelece posição natural
                )
    
    seat2 = Node("Seat2",
                 geom=lambda: draw_seat(),
                 transform=tf_transform(tx=CABIN_FLOOR_WIDTH * 0.35,
                                        ty=CAR_FLOOR_DEPTH * 0.72,
                                        sx=0.35, sy=0.28, sz=0.35,
                                        rx=1.0, angle=90)
                )

    brakes = Node("Brakes",
                  geom=lambda: draw_brakes(),
                  transform=tf_transform(tx=CABIN_FLOOR_WIDTH * 0.5,
                                         ty=CAR_FLOOR_DEPTH * 0.5,
                                         tz=CAR_FLOOR_HEIGHT * -0.6,  # novo y 
                                         rx=1.0, angle=90) # Restabelece posição natural
                 )
    
    door1 = Node("Door1",
                 geom=lambda: draw_door(color_front=CAR_OUTSIDE_COLOR,
                                        color_back=CAR_INSIDE_COLOR,
                                        color_side=PROTECTIONS_COLOR,
                                        tex_front=tex_car),
                 transform=tf_chain(tf_transform(tx=FRONT_SIDE_WALL_WIDTH,
                                                 ty=0.0,
                                                 tz=0.0,
                                                 rx=1.0, angle=90),
                                    tf_door_movement(door_open="door_open1")
                                    ),
                 state={"door_open1":0.0}
                )
    DOOR_1_NODE = door1

    door_handle1 = Node("Door_handle1",
                        geom=lambda: draw_door_handle(color_front=DOOR_HANDLE_COLOR,
                                                      color_back=DOOR_HANDLE_COLOR,
                                                      color_side=DOOR_HANDLE_COLOR)
                       )

    door_protection1 = Node("Door_protection1",
                            geom=lambda: draw_door_protection(width=DOOR_TOP_WIDTH,
                                                              height=WALL_THICKNESS + PROT_OFFSET,
                                                              depth=PROT_HEIGHT,

                                                              color=PROTECTIONS_COLOR),
                            transform=tf_transform(ty=DOOR_TOP_FRONT_HEIGHT + PROT_HEIGHT,
                                                   tz=PROT_OFFSET)
                           )

    door2 = Node("Door2",
                 geom=lambda: draw_door(color_front=CAR_OUTSIDE_COLOR,
                                        color_back=CAR_INSIDE_COLOR,
                                        color_side=PROTECTIONS_COLOR,
                                        tex_front=tex_car),
                 transform=tf_chain(tf_transform(tx=FRONT_SIDE_WALL_WIDTH,
                                                 ty=CAR_FLOOR_DEPTH,        # novo z
                                                 rx=1.0, angle=90,
                                                 switch_side=True),
                                    tf_door_movement(door_open="door_open2",
                                                     side1=False)
                                   ),
                 state={"door_open2":0.0}       
                )
    DOOR_2_NODE = door2

    door_handle2 = Node("Door_handle2",
                        geom=lambda: draw_door_handle(color_front=DOOR_HANDLE_COLOR,
                                                      color_side=DOOR_HANDLE_COLOR,
                                                      color_back=DOOR_HANDLE_COLOR),
                        transform=tf_transform(tz=DOOR_HANDLE_THICKNESS,
                                               switch_side=True)
                       )

    door_protection2 = Node("Door_protection2",
                            geom=lambda: draw_door_protection(width=DOOR_TOP_WIDTH,
                                                              height=WALL_THICKNESS + PROT_OFFSET,
                                                              depth=PROT_HEIGHT,

                                                              color=PROTECTIONS_COLOR),
                            transform=tf_transform(ty=DOOR_TOP_FRONT_HEIGHT + PROT_HEIGHT + 0.001,
                                                   tz=-PROT_OFFSET,
                                                   switch_side=True)
                           )

    # Cada wall é pai da sua respetiva proteção (<wall>_protection)
    front_side_wall1 = Node("Front_side_wall1",
                            geom=lambda: draw_box(width=FRONT_SIDE_WALL_WIDTH,
                                          height=DOOR_TOP_FRONT_HEIGHT,
                                          depth=WALL_THICKNESS,

                                          color_front=CAR_OUTSIDE_COLOR,
                                          color_back=CAR_INSIDE_COLOR,
                                          color_side=CAR_OUTSIDE_COLOR,
                                          tex_f=tex_car,
                                          tex_s=tex_car,
                                          tile_u_front=0.5, tile_v_front=0.5,
                                          tile_u_side=0.7, tile_v_side=0.2),
                            transform=tf_transform(rx=1.0, angle=90) # Restabelecer orientação natural
                           )
                           
    front_side_wall_protection1 = Node("Front_side_wall_protection1",
                                       geom=lambda: draw_protection(width=FRONT_SIDE_WALL_WIDTH,
                                                             height=WALL_THICKNESS + PROT_OFFSET,
                                                             depth=PROT_HEIGHT,
                                                             corners=[1],

                                                             color=PROTECTIONS_COLOR),
                                       transform=tf_transform(ty=DOOR_TOP_FRONT_HEIGHT + PROT_HEIGHT,
                                                              tz=PROT_OFFSET,
                                                              rx=1.0, angle=-90)
                                      )
    
    lat_rearview_mirror1 = Node("Lat_rearview_mirror1",
                                geom=lambda: draw_lat_rearview_mirror(color=HOOD_FRONT_COLOR),
                                transform=tf_chain(tf_transform(rx=1.0, angle=90),
                                                   tf_transform(tx=FRONT_SIDE_WALL_WIDTH * 0.65,
                                                                ty=-0.05,
                                                                tz=WALL_THICKNESS * 1.55,
                                                                sx=0.6, sy=0.6, sz=0.6,
                                                                ry=1.0, angle=30))
                               )
          
    front_side_wall2 = Node("Front_side_wall2",
                            geom=lambda: draw_box(width=FRONT_SIDE_WALL_WIDTH,
                                                  height=DOOR_TOP_FRONT_HEIGHT,
                                                  depth=WALL_THICKNESS,

                                                  color_front=CAR_OUTSIDE_COLOR,
                                                  color_back=CAR_INSIDE_COLOR,
                                                  color_side=CAR_OUTSIDE_COLOR,
                                                  tex_f=tex_car,
                                                  tex_s=tex_car,
                                                  tile_u_front=0.5, tile_v_front=0.5,
                                                  tile_u_side=0.7, tile_v_side=0.2),
                            transform=tf_transform(ty=CAR_FLOOR_DEPTH,
                                                   rx=1.0, angle=90,
                                                   switch_side=True)
                           )
    
    front_side_wall_protection2 = Node("Front_side_wall_protection2",
                                       geom=lambda: draw_protection(width=FRONT_SIDE_WALL_WIDTH,
                                                             height=WALL_THICKNESS + PROT_OFFSET,
                                                             depth=PROT_HEIGHT, 
                                                             corners=[0],
                                                            
                                                            color=PROTECTIONS_COLOR),
                                       transform=tf_transform(ty=DOOR_TOP_FRONT_HEIGHT + PROT_HEIGHT + 0.0001,
                                                              tz=-PROT_OFFSET,
                                                              rx=1.0, angle=90,
                                                              switch_side=True)
                                      )
    
    lat_rearview_mirror2 = Node("Lat_rearview_mirror2",
                                geom=lambda: draw_lat_rearview_mirror(color=HOOD_FRONT_COLOR),
                                transform=tf_chain(tf_transform(rx=1.0, angle=90),
                                                   tf_transform(tx=FRONT_SIDE_WALL_WIDTH * 0.65,
                                                                ty=-0.05,
                                                                tz=-WALL_THICKNESS * 3.55,
                                                                sx=0.6, sy=0.6, sz=0.6,
                                                                ry=1.0, angle=-30,
                                                                switch_side=True))
                               )
    
    back_side_wall1 = Node("Back_side_wall1",
                           geom=lambda: draw_box(width=BACK_SIDE_WALL_WIDTH,
                                                  height=DOOR_TOP_REAR_HEIGHT,
                                                  depth=WALL_THICKNESS,

                                                  color_front=CAR_OUTSIDE_COLOR,
                                                  color_back=CAR_INSIDE_COLOR,
                                                  color_side=CAR_INSIDE_COLOR,
                                                  tex_f=tex_car,
                                                  tile_u_front=0.2, tile_v_front=0.7),
                           transform=tf_transform(tx=CABIN_FLOOR_WIDTH - BACK_SIDE_WALL_WIDTH,
                                                  ty=0.0,
                                                  tz=0.0,
                                                  rx=1.0, angle=90)
                           )

    back_side_wall_protection1 = Node("Back_side_wall_protection1",
                                      geom=lambda: draw_protection(width=BACK_SIDE_WALL_WIDTH + TRUNK_FLOOR_WIDTH + R_TRUNK + PROT_OFFSET,
                                                                   height=WALL_THICKNESS + PROT_OFFSET,
                                                                   depth=PROT_HEIGHT,
                                                                   corners=[2, 3],

                                                                   color=PROTECTIONS_COLOR),
                                      transform=tf_transform(ty=DOOR_TOP_REAR_HEIGHT + PROT_HEIGHT,
                                                             tz=PROT_OFFSET,
                                                             rx=1.0, angle=-90)
                                     )

    back_side_wall2 = Node("Back_side_wall2",
                           geom=lambda: draw_box(width=BACK_SIDE_WALL_WIDTH,
                                                  height=DOOR_TOP_REAR_HEIGHT,
                                                  depth=WALL_THICKNESS,

                                                  color_front=CAR_OUTSIDE_COLOR,
                                                  color_back=CAR_INSIDE_COLOR,
                                                  color_side=CAR_INSIDE_COLOR,
                                                  tex_f=tex_car,
                                                  tile_u_front=0.2, tile_v_front=0.7),
                           transform=tf_transform(tx=CABIN_FLOOR_WIDTH - BACK_SIDE_WALL_WIDTH,
                                                  ty=CAR_FLOOR_DEPTH,
                                                  rx=1.0, angle=90,
                                                  switch_side=True)
                          )

    back_side_wall_protection2 = Node("Back_side_wall_protection2",
                                      geom=lambda: draw_protection(width=BACK_SIDE_WALL_WIDTH + TRUNK_FLOOR_WIDTH + R_TRUNK + PROT_OFFSET,
                                                                   height=WALL_THICKNESS + PROT_OFFSET,
                                                                   depth=PROT_HEIGHT,
                                                                   corners=[2, 3],
                                                            
                                                                   color=PROTECTIONS_COLOR),
                                      transform=tf_transform(ty=DOOR_TOP_REAR_HEIGHT + 0.001,
                                                             tz=PROT_OFFSET,
                                                             rx=1.0, angle=-90,
                                                             switch_side=True)
                                     )

    # A Front_wall para além de ser filho do chão do habitáculo, ele é pai do painel do veículo, bem como dos pedais deste !
    front_wall = Node("Front_wall",
                      geom=lambda: draw_box(width=CAR_FLOOR_DEPTH - 2 * WALL_THICKNESS,
                                            height=DOOR_TOP_FRONT_HEIGHT,
                                            depth=WALL_THICKNESS,

                                            color_front=CAR_INSIDE_COLOR,
                                            color_back=CAR_OUTSIDE_COLOR,
                                            color_side=PROTECTIONS_COLOR,
                                            tex_b=tex_car),
                      transform=tf_chain(tf_transform(rx=1.0, angle=90), # Ajeitamos para orientação normal
                                         tf_transform(tx=WALL_THICKNESS,
                                                      tz=-WALL_THICKNESS, 
                                                      ry=1.0, angle=90)) # Fazemos transf. necessárias
                     )

    # O Dashboard é pai do volante.
    dashboard = Node("Dashboard",
                     geom=draw_dashboard,
                     transform=tf_transform(ty=DOOR_TOP_FRONT_HEIGHT - TABLE_HEIGHT,
                                            ry=1.0, angle=-90)
                    )
      
    steering_wheel = Node("Steering_wheel",
                          geom=lambda: draw_steering_wheel(),
                          transform=tf_chain(tf_transform(tx=TABLE_WIDTH + 0.1,
                                                          ty=TABLE_HEIGHT - 0.05,
                                                          tz=-CAR_FLOOR_DEPTH * 0.2,
                                                          sx=0.35, sy=0.35, sz=0.35),
                                             tf_steering_wheel_movement(car_node=car)
                                            )
                         )

    pedals = Node("Pedals", 
                  geom=lambda: draw_pedals(),
                  transform=tf_transform(tx=0.26 * CAR_FLOOR_DEPTH, # -z
                                         ty=0.10 * DOOR_TOP_FRONT_HEIGHT,
                                         tz=1.25 * WALL_THICKNESS)  # x
                 )

    rear_wall = Node("Rear_wall",
                      geom=lambda: draw_box(width=CAR_FLOOR_DEPTH - 2 * WALL_THICKNESS,
                                            height=DOOR_TOP_REAR_HEIGHT,
                                            depth=WALL_THICKNESS,
                                            
                                            color_front=CAR_INSIDE_COLOR,
                                            color_back=CAR_INSIDE_COLOR,
                                            color_side=CAR_OUTSIDE_COLOR),
                      transform=tf_chain(tf_transform(rx=1.0, angle=90),
                                         tf_transform(tx=CABIN_FLOOR_WIDTH,
                                                      tz=-WALL_THICKNESS, 
                                                      ry=1.0, angle=90))
                    )


    # Nó raiz do porta-malas - É pai do chão do parachoques traseiro,
    # de todas as paredes que compõem o porta-malas e a porta da bagageira!
    trunk_floor = Node("Trunk_floor",
                       geom=lambda: draw_box(width=TRUNK_FLOOR_WIDTH,
                                             height=CAR_FLOOR_DEPTH,
                                             depth=CAR_FLOOR_HEIGHT,

                                             color_front=CAR_CABIN_FLOOR_COLOR,
                                             color_side=CAR_OUTSIDE_COLOR,
                                             color_back=CAR_UNDERNEATH_COLOR),
                       transform=tf_transform(tx=CABIN_FLOOR_WIDTH * 0.5,
                                              ty=-CAR_FLOOR_HEIGHT * 0.5,
                                              tz=CAR_FLOOR_DEPTH * 0.5,
                                              rx=1.0,
                                              angle=-90.0)
                      )
    
    # Nó de todos os objetos constituintes do parachoques! Subordinado ao chão do porta-malas.
    rear_bumper_floor = Node("Rear_bumper_floor", 
                             geom=lambda: draw_box(width=REAR_BUMPER_WIDTH,
                                                   height=CAR_FLOOR_DEPTH,
                                                   depth=CAR_FLOOR_HEIGHT,

                                                   color_front=REAR_BUMPER_COLOR,
                                                   color_side=CAR_OUTSIDE_COLOR,
                                                   color_back=CAR_UNDERNEATH_COLOR,
                                                   tex_s=tex_car,
                                                   tile_v_side=0.05),
                              transform=tf_transform(tx=TRUNK_FLOOR_WIDTH)
                                  )
    
    # Nó que representa uma das paredes do parachoques; É o pai de uma farol traseiro.
    rear_bumper_wall1 = Node("Rear_bumper_wall1",
                             geom=lambda: draw_rear_bumper_wall(tex=tex_car),
                             transform=tf_transform(rx=1.0, angle=90)
                                  )
    
    rear_light1 = Node("Rear_light1",
                       geom=lambda: draw_rear_light(),
                       transform=tf_transform(tx=REAR_BUMPER_WIDTH + 0.01, 
                                              ty=DOOR_TOP_REAR_HEIGHT * 0.6,
                                              tz=-WALL_THICKNESS * 0.5)
                      ) 

    rear_bumper_wall2 = Node("Rear_bumper_wall2",
                             geom=lambda: draw_rear_bumper_wall(tex=tex_car),
                             transform=tf_transform(ty=CAR_FLOOR_DEPTH,
                                                    rx=1.0, angle=90,
                                                    switch_side=True)
                            )

    rear_light2 = Node("Rear_light2",
                       geom=lambda: draw_rear_light(),
                       transform=tf_transform(tx=REAR_BUMPER_WIDTH + 0.01, 
                                              ty=DOOR_TOP_REAR_HEIGHT * 0.6,
                                              tz=-WALL_THICKNESS * 0.5,
                                              ry=1.0, angle=180) # Por conta do switch
                      )

    trunk_side_wall1 = Node("Trunk_side_wall1",
                            geom=lambda: draw_box(width=TRUNK_FLOOR_WIDTH,
                                                  height=DOOR_TOP_REAR_HEIGHT,
                                                  depth=WALL_THICKNESS,

                                                  color_front=CAR_OUTSIDE_COLOR,
                                                  color_back=CAR_INSIDE_COLOR,
                                                  color_side=CAR_OUTSIDE_COLOR,
                                                  tex_f=tex_car,
                                                  tile_u_front=0.7, tile_v_front=0.7),
                            transform=tf_transform(rx=1.0, angle=90)
                           )
    
    trunk_side_wall2 = Node("Trunk_side_wall2",
                            geom=lambda: draw_box(width=TRUNK_FLOOR_WIDTH,
                                                  height=DOOR_TOP_REAR_HEIGHT,
                                                  depth=WALL_THICKNESS,

                                                  color_front=CAR_OUTSIDE_COLOR,
                                                  color_back=CAR_INSIDE_COLOR,
                                                  color_side=CAR_OUTSIDE_COLOR,
                                                  tex_f=tex_car,
                                                  tile_u_front=0.7, tile_v_front=0.7),                
                            transform=tf_transform(ty=CAR_FLOOR_DEPTH,
                                                   rx=1.0, angle=90,
                                                   switch_side=True)                
                           )

    trunk_rear_wall = Node("Trunk_rear_wall",
                           geom=lambda: draw_box(width=CAR_FLOOR_DEPTH - 2 * WALL_THICKNESS,
                                                 height=DOOR_TOP_FRONT_HEIGHT + PROT_HEIGHT,
                                                 depth=WALL_THICKNESS,

                                                 color_front=CAR_OUTSIDE_COLOR,
                                                 color_back=CAR_INSIDE_COLOR,
                                                 color_side=CAR_OUTSIDE_COLOR,
                                                 tex_f=tex_car),
                           transform=tf_chain(tf_transform(rx=1.0, angle=90),
                                              tf_transform(tx=TRUNK_FLOOR_WIDTH,
                                                           tz=-WALL_THICKNESS, 
                                                           ry=1.0, angle=90))
                          )

    trunk_move = Node("Trunk_move",
                      transform=tf_trunk_movement(trunk_open="trunk_open",
                                                  rot_x = WALL_THICKNESS + R_TRUNK - 0.6,
                                                  rot_y = WALL_THICKNESS,
                                                  rot_z = DOOR_TOP_REAR_HEIGHT - R_TRUNK * 0.5),
                      state={"trunk_open":0.0} 
                     )
    TRUNK_NODE = trunk_move

    trunk_door = Node("Trunk_door",
                      geom=lambda: draw_rounded_panel(width=2*(R_TRUNK + PROT_HEIGHT),
                                                      height=2*(R_TRUNK + PROT_HEIGHT),
                                                      depth=CAR_FLOOR_DEPTH - 2 * WALL_THICKNESS,
                                                      dx=TRUNK_FLOOR_WIDTH - R_TRUNK + 0.10,
                                                      r=R_TRUNK,
                                                      
                                                      color_front=CAR_INSIDE_COLOR,
                                                      color_back=CAR_INSIDE_COLOR,
                                                      color_side=CAR_OUTSIDE_COLOR),
                      transform=tf_transform(tx=WALL_THICKNESS + R_TRUNK - 0.08, 
                                             ty=WALL_THICKNESS,
                                             tz=DOOR_TOP_REAR_HEIGHT - R_TRUNK, # Y
                                             sx=-1,
                                             rx=1, angle=90)
                     )


    # Nó contentor que armazena todas as componentes da parte superior do veículo
    # (o para-brisas, a roll cage e os retrovisores)
    car_upper_body = Node("car_upper_body")
    
    # Tem como filho o retrovisor !
    windshield = Node("Windshield",
                      geom=lambda: draw_windshield(),
                      transform=tf_transform(tx=-CABIN_FLOOR_WIDTH * 0.5 + PIPE_WIDTH * 0.5,
                                             ty=DOOR_TOP_FRONT_HEIGHT - CAR_FLOOR_HEIGHT * 0.5,
                                             tz=CAR_FLOOR_DEPTH * 0.5 - WALL_THICKNESS + PIPE_WIDTH,
                                             ry=1.0, angle=90.0)
                     )
    
    central_rearview_mirror = Node("Central_rearview_mirror",
                                   geom=lambda: draw_central_rearview_mirror(color=PIPE_COLOR),
                                   transform=tf_chain(tf_transform(ry=1.0, angle=-90),
                                                      tf_transform(tx=0.18,
                                                                   ty=1.2,
                                                                   tz=-CAR_FLOOR_DEPTH * 0.5 + 0.45,
                                                                   sx=0.5, sy=0.5, sz=0.5,
                                                                   rz=1.0, angle=WINDSHIELD_ANGLE),
                                                      tf_transform(ry=1.0, angle=90))
                                   )

    roll_cage = Node("Roll_cage", 
                     geom=lambda: draw_roll_cage(PIPE_COLOR))




    # Nó contentor que abriga todas as rodas do veículo
    wheels = Node("Wheels")
    
    wheel_front1 = Node("Wheel_front1",
                        geom=lambda: draw_wheel(front=True),
                        transform=tf_chain(tf_transform(tx=-0.5 * CABIN_FLOOR_WIDTH - 0.15,
                                               tz=0.53 * CAR_FLOOR_DEPTH,
                                               sx=0.35, sy=0.35, sz=0.35),
                                           tf_wheels_movement(car_node=car, front=True)
                                          )
                       )

    wheel_front2 = Node("Wheel_front2",
                        geom=lambda: draw_wheel(front=True),
                        transform=tf_chain(tf_transform(tx=-0.5 * CABIN_FLOOR_WIDTH - 0.15,
                                                        tz=-0.53 * CAR_FLOOR_DEPTH - REAR_WHEEL_DEPTH * 0.25,
                                                        sx=0.35, sy=0.35, sz=0.35),
                                           tf_wheels_movement(car_node=car, front=True)
                                          )
                       )
    
    wheel_back1 = Node("Wheel_back1",
                       geom=lambda: draw_wheel(),
                       transform=tf_chain(tf_transform(tx=0.5 * CABIN_FLOOR_WIDTH + 0.8,
                                                       ty=0.2,
                                                       tz=0.5 * CAR_FLOOR_DEPTH,
                                                       sx=0.35, sy=0.35, sz=0.35),
                                          tf_wheels_movement(car_node=car)
                                         )   
                      )
    
    wheel_back2 = Node("Wheel_back2",
                       geom=lambda: draw_wheel(),
                       transform=tf_chain(tf_transform(tx=0.5 * CABIN_FLOOR_WIDTH + 0.8,
                                                       ty=0.2,
                                                       tz=-0.5 * CAR_FLOOR_DEPTH - FRONT_WHEEL_DEPTH * 0.45,
                                                       sx=0.35, sy=0.35, sz=0.35),
                                          tf_wheels_movement(car_node=car)                                            
                                         )
                      )
    

    outside = Node("Outside",
                   transform=tf_transform(tx=2.0))

    # A garagem é pai do portão da garagem, que tem que existir como objeto independente
    # por conta do seu movimento
    garage = Node("Garage",
                  geom=lambda: draw_garage_structure(tex_outside=tex_garage_outside),
                 )
    
    garage_lamp = Node("Garage_lamp",
                  geom=lambda: draw_lamp(),
                  transform=tf_transform(ty=GARAGE_HEIGHT - GARAGE_WALL_THICKNESS * 2)
                 )
    
    garage_gate = Node("Garage_gate",
                       geom=lambda: draw_garage_gate(tex_front=tex_garage_gate),
                       transform=tf_transform(tx=-GARAGE_DEPTH * 0.5 + GARAGE_WALL_THICKNESS * 0.5,
                                              ty=0.0,
                                              tz=GARAGE_WIDTH * 0.5 - GARAGE_FRONT_WALL_THICKNESS - GARAGE_WALL_THICKNESS,
                                              ry=1.0, angle=90,
                                              switch_side=True),
                      )
    GARAGE_GATE_NODE = garage_gate
       
    tree = Node("Tree",
                  geom=lambda: draw_tree(),
                  transform=tf_transform(tz=10)
                 )
    
    street_light = Node("Street_light",
                        geom=lambda: draw_street_light(),
                        transform=tf_transform(tx=-4.5,
                                               tz=-6.6,
                                               ry=1.0, angle=-50))

    # Ligações (hierarquia)
    world.add(
        car.add(
            hood_floor.add(hood.add(headlight1, 
                                    headlight2)
            ),
            
            cabin_floor.add(seat1, 
                            seat2,
                            brakes,
                            door1.add(door_handle1,
                                      door_protection1),
                            door2.add(door_handle2,
                                      door_protection2),
                            front_side_wall1.add(front_side_wall_protection1.add(lat_rearview_mirror1)),
                            front_side_wall2.add(front_side_wall_protection2.add(lat_rearview_mirror2)),
                            back_side_wall1.add(back_side_wall_protection1),
                            back_side_wall2.add(back_side_wall_protection2),
                            front_wall.add(dashboard.add(steering_wheel),
                                           pedals),
                            rear_wall
            ),

            trunk_floor.add(
                rear_bumper_floor.add(rear_bumper_wall1.add(rear_light1),
                                      rear_bumper_wall2.add(rear_light2)),
                trunk_side_wall1,
                trunk_side_wall2,
                trunk_rear_wall,
                trunk_move.add(trunk_door)
            ),
            
            car_upper_body.add(windshield.add(central_rearview_mirror), 
                                roll_cage
            ),
            
            wheels.add(wheel_front1,
                       wheel_front2,
                       wheel_back1,
                       wheel_back2)
        ),
        outside.add(garage.add(garage_gate,
                               garage_lamp),
                    tree,
                    street_light
        )
    )

    return world

SCENE = None  # será criado no main()

def setup():
    """
    Função que inicializa as luzes, as texturas e outras definições gerais.
    """
    global tex_floor, tex_car, tex_garage_gate, tex_garage_outside, tex_radiator

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glClearColor(0.0157, 0.0314, 0.0627, 1.0)  # De noite.
    
    glEnable(GL_DEPTH_TEST)

    glEnable(GL_CULL_FACE)
    glFrontFace(GL_CCW)
    glCullFace(GL_BACK)

    glEnable(GL_NORMALIZE)
    glEnable(GL_COLOR_MATERIAL)
    glShadeModel(GL_SMOOTH)

    glEnable(GL_LIGHTING) 
    glEnable(GL_LIGHT0)     # Luz ambiente global
    glEnable(GL_LIGHT1)     # Luz para o farol da direita
    glEnable(GL_LIGHT2)     # Luz para o farol da esquerda
    glEnable(GL_LIGHT3)     # Luz do poste de rua
    glEnable(GL_LIGHT4)     # Luz da lâmpada dentro da garagem

    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (0.08, 0.08, 0.08, 1.0))

    # Abaixo definir-se-á os valores fixos para cada uma das luzes !
    # GL_LIGHT0:
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.3, 0.3, 0.3, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.2, 0.2, 0.2, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (0.25, 0.25, 0.25, 1.0))

    # GL_LIGHT1 
    glLightfv(GL_LIGHT1, GL_AMBIENT, (0.0, 0.0, 0.0, 1.0))
    glLightfv(GL_LIGHT1, GL_DIFFUSE, (0.3, 0.3, 0.3, 1.0))
    glLightfv(GL_LIGHT1, GL_SPECULAR, (0.4, 0.4, 0.4, 1.0))
    glLightf(GL_LIGHT1, GL_SPOT_CUTOFF, 20.0)
    glLightf(GL_LIGHT1, GL_SPOT_EXPONENT, 1.0)
    glLightf(GL_LIGHT1, GL_CONSTANT_ATTENUATION, 1.0)

    # GL_LIGHT2:
    glLightfv(GL_LIGHT2, GL_AMBIENT, (0.0, 0.0, 0.0, 1.0))
    glLightfv(GL_LIGHT2, GL_DIFFUSE, (0.3, 0.3, 0.3, 1.0))
    glLightfv(GL_LIGHT2, GL_SPECULAR, (0.4, 0.4, 0.4, 1.0))
    glLightf(GL_LIGHT2, GL_SPOT_CUTOFF, 20.0)
    glLightf(GL_LIGHT2, GL_SPOT_EXPONENT, 1.0)
    glLightf(GL_LIGHT2, GL_CONSTANT_ATTENUATION, 1.0)

    # GL_LIGHT3:
    glLightfv(GL_LIGHT3, GL_AMBIENT, (0.0, 0.0, 0.0, 1.0))
    glLightfv(GL_LIGHT3, GL_DIFFUSE, (0.96, 0.91, 0.11, 1.0)) # amarelo torrado
    glLightfv(GL_LIGHT3, GL_SPECULAR, (0.8, 1.0, 0.8, 1.0))
    glLightf(GL_LIGHT3, GL_SPOT_CUTOFF, 30.0)
    glLightf(GL_LIGHT3, GL_SPOT_EXPONENT, 1.0)
    glLightf(GL_LIGHT3, GL_CONSTANT_ATTENUATION, 1.0)

    # GL_LIGHT4:
    glLightfv(GL_LIGHT4, GL_AMBIENT, (0.096, 0.091, 0.011, 1.0))
    glLightfv(GL_LIGHT4, GL_DIFFUSE, (0.0, 0.0, 0.0, 1.0))
    glLightfv(GL_LIGHT4, GL_SPECULAR, (0.0, 0.0, 0.12, 1.0))
    glLightf(GL_LIGHT4, GL_SPOT_CUTOFF, 5.0)
    glLightf(GL_LIGHT4, GL_SPOT_EXPONENT, 0.3)
    glLightf(GL_LIGHT4, GL_CONSTANT_ATTENUATION, 2.0)

    #Material GLOBAL (Default)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.0, 0.0, 0.0, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, 0)

    tex_floor = load_texture(GENERAL_FLOOR_TEX_PATH, repeat=True)
    tex_car = load_texture(CAR_OUTSIDE_TEX_PATH, repeat=False)
    tex_garage_gate = load_texture(GARAGE_GATE_TEX_PATH, repeat=False)
    tex_garage_outside = load_texture(GARAGE_OUTSIDE_TEX_PATH, repeat=False)
    tex_radiator = load_texture(RADIATOR_TEX_PATH, repeat=False)

def display():
    """
    Função que é responsável pelo funcionamento da câmera, bem como por 
    desenhar o chão e a cena num todo.
    """
    global eye_x, eye_y, eye_z

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if third_person == 1:
        angle_rad = math.radians(CAR_NODE.state["car_yaw"] + CAR_NODE.state["steering"])

        cam_x = CAR_NODE.state["movement_x"] + math.cos(angle_rad) * 8
        cam_z = CAR_NODE.state["movement_z"] - math.sin(angle_rad) * 8
        cam_y = 5

        center_x = CAR_NODE.state["movement_x"]
        center_y = 2
        center_z = CAR_NODE.state["movement_z"]

        gluLookAt(cam_x, cam_y, cam_z,
                center_x, center_y, center_z,
                0.0, 1.0, 0.0)
        
    elif third_person == 2:
        angle_rad = math.radians(CAR_NODE.state["car_yaw"] + CAR_NODE.state["steering"])

        cam_x = CAR_NODE.state["movement_x"] + math.cos(angle_rad) * 0.45
        cam_z = CAR_NODE.state["movement_z"] - math.sin(angle_rad) * 0.45
        cam_y = 3

        center_x = CAR_NODE.state["movement_x"]
        center_y = 3
        center_z = CAR_NODE.state["movement_z"]

        glTranslatef(0.45, 0, 0)
        gluLookAt(cam_x, cam_y, cam_z,
                  center_x, center_y, center_z,
                  0.0, 1.0, 0.0)
    else:
        # câmera
        dir_x, dir_y, dir_z = get_look_direction()
        gluLookAt(eye_x, eye_y, eye_z,
                  eye_x + dir_x, eye_y + dir_y, eye_z + dir_z,
                  0.0, 1.0, 0.0)

    draw_floor()
    SCENE.draw()
    glutSwapBuffers()


def idle():
    """
    Função fornecida pelos professores.
    """
    interact_garage_gate() # Corre de fundo e permite abrir e fechar a garagem

    glutPostRedisplay()

def reshape(w, h):
    """
    Função fornecida pelos professores.
    """
    if h == 0:
        h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, float(w)/float(h), 0.1, 1000.0)

def draw_floor():
    """
    Função fornecida pelos professores.
    """
    S = 100.0
    T = 50.0                   # Quantas vezes multiplicaremos a textura original no chão
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_floor)
    glColor3f(1.0, 1.0, 1.0)
    glNormal3f(0, 1, 0)

    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0); glVertex3f(-S, 0.0,  S)
    glTexCoord2f(T,   0.0); glVertex3f( S, 0.0,  S)
    glTexCoord2f(T,    T ); glVertex3f( S, 0.0, -S)
    glTexCoord2f(0.0,  T ); glVertex3f(-S, 0.0, -S)
    glEnd()
    

def keyboard(key, x, y):
    """
    w/a/s/d --- Mover a posição da câmara para a frente/esquerda/trás/direita da sua direção
    q/e     --- Mover a posição da câmara para cima/baixo em y
    i/j/k/l --- Rodar a direção da câmara para cima/esquerda/baixo/direita da sua direção
    g/f     --- Abrir/fechar o portão da garagem
    o/p     --- Abrir/fechar a porta esquerda de quem vê o carro de trás
    9/0     --- Abrir/fechar a porta direita de quem vê o carro de trás
    t/y     --- Abrir/fechar o porta-bagagens
    h       --- Controlar o movimento da câmara em relação ao carro 3ª pessoa/1ª pessoa/livre
    n/m     --- Rodar o volante no sentido anti-horário/horário de quem vê o carro de trás e controlar a direção do carro
    z/x     --- Mover o carro para a frente/trás de acordo com a rotação do volante
    ESC     --- Fechar o programa
    """
    global eye_x, eye_y, eye_z, yaw, pitch, third_person
    step = 0.3
    rot_speed = 2.0
    pitch = max(-89.9, min(89.9, pitch)) # Clamp pitch to avoid flipping
    dir_x, dir_y, dir_z = get_look_direction()

    right_x = math.cos(math.radians(yaw - 90))
    right_z = math.sin(math.radians(yaw - 90))

    match key:
        case b'w':# forward
            eye_x += dir_x * step
            eye_y += dir_y * step
            eye_z += dir_z * step

        case b's':  # backward
            eye_x -= dir_x * step
            eye_y -= dir_y * step
            eye_z -= dir_z * step

        case b'd':  # strafe right
            eye_x -= right_x * step
            eye_z -= right_z * step

        case b'a':  # strafe left
            eye_x += right_x * step
            eye_z += right_z * step



        case b'q':  # up
            eye_y += step

        case b'e':  # down
            eye_y -= step



        case b'j':  # turn left
            yaw -= rot_speed

        case b'l':  # turn right
            yaw += rot_speed

        case b'i':  # look up
            pitch += rot_speed

        case b'k':  # look down
            pitch -= rot_speed



        case b'g':  #abrir porta garagem
            start_opening_gate()

        case b'f':  #fechar porta garagem
            start_closing_gate()



        case b'o' if DOOR_1_NODE.state["door_open1"] >= -60:  # open door 1
            DOOR_1_NODE.state["door_open1"] -= rot_speed

        case b'p' if DOOR_1_NODE.state["door_open1"] < 0:  # close door 1
            DOOR_1_NODE.state["door_open1"] += rot_speed


        case b'9' if DOOR_2_NODE.state["door_open2"] <= 60:  # open door 2
            DOOR_2_NODE.state["door_open2"] += rot_speed
        
        case b'0' if DOOR_2_NODE.state["door_open2"] > 0:  # close door 2
            DOOR_2_NODE.state["door_open2"] -= rot_speed


        case b't' if TRUNK_NODE.state["trunk_open"] >= -75:  # open trunk
            TRUNK_NODE.state["trunk_open"] -= rot_speed

        case b'y' if TRUNK_NODE.state["trunk_open"] < 0:  # close trunk
            TRUNK_NODE.state["trunk_open"] += rot_speed



        case b'h':  # follow car with camera
            third_person = (third_person + 1) % 3


        case b'm' if CAR_NODE.state["steering"] >= -27:  # steering wheel clock-wise
            CAR_NODE.state["steering"] -= rot_speed
            

        case b'n' if CAR_NODE.state["steering"] <= 27:  # steering wheel anti-clock-wise
            CAR_NODE.state["steering"] += rot_speed


        case b'z':  # move forward
            angle_rad = math.radians(CAR_NODE.state["car_yaw"])
            CAR_NODE.state["movement_x"] -= math.cos(angle_rad) * step
            CAR_NODE.state["movement_z"] += math.sin(angle_rad) * step
            rot_dist = ((step / REAR_WHEEL_R)  * (180.0 / math.pi)) / 1
            CAR_NODE.state["car_yaw"] += CAR_NODE.state["steering"] / 15 % 360
            CAR_NODE.state["rotation"] += rot_dist % 360

        case b'x':  # move backward
            angle_rad = math.radians(CAR_NODE.state["car_yaw"])
            CAR_NODE.state["movement_x"] += math.cos(angle_rad) * step
            rot_dist = ((step / REAR_WHEEL_R)  * (180.0 / math.pi)) / 1
            CAR_NODE.state["movement_z"] -= math.sin(angle_rad) * step
            CAR_NODE.state["car_yaw"] -= CAR_NODE.state["steering"] / 15 % 360
            CAR_NODE.state["rotation"] -= rot_dist % 360



        case (b'\x1b'):  # ESC to close
            try:
                del_quadrics()
                glutLeaveMainLoop() 
            except Exception:
                sys.exit(0)

    glutPostRedisplay()

def get_look_direction():
    """
    Função fornecida pelos professores.
    """
    # Convert degrees to radians
    rad_yaw = math.radians(yaw)
    rad_pitch = math.radians(pitch)
    dir_x = math.cos(rad_pitch) * math.cos(rad_yaw)
    dir_y = math.sin(rad_pitch)
    dir_z = math.cos(rad_pitch) * math.sin(rad_yaw)
    return dir_x, dir_y, dir_z

def main():
    global SCENE
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(win_w, win_h)

    glutCreateWindow(b"Interactive 3D Car Scene")
    init_quadrics()

    setup()
    SCENE = build_scene()

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutIdleFunc(idle)
    glutMainLoop()

#chamada da função main
if __name__ == "__main__":
    main()