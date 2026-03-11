"""
Módulo para construção de todos os objetos exteriores, i.e,
a garagem e mais outros elementos !
Desenvolvido por:
    - Diogo Vasconcelos, fc61809
    - Miguel Guise, fc61822
    - Simão da Luz, fc61816
Em: 01/12/2026
"""

from utils.helpers import *
from utils.variables import *

garage_gate_angle = 90.0
garage_gate_opening = True
garage_gate_tilting = False

def draw_lamp(size=0.2, height=0.3, color=(0.7,0.7,0.7)):
    """
    Função responsável pela construção de uma lâmpada.
    - size: tamanho da esfera
    - height: altura do cilindro
    - color: cor do cilindro
    """
    glColor3f(*color)
    glPushMatrix()

    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (0.79, 0.78, 0.96, 1.0))
    glutSolidSphere(size, 24, 24)
    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (0.0, 0.0, 0.0, 1.0))
    glTranslatef(0.0, size * 0.25, 0.0)
    
    glRotatef(-90.0, 1.0, 0.0, 0.0)
    draw_closed_cylinder(base=size * 0.7, top=size * 0.3, height=height, 
                         color=color)
    
    glTranslatef(0.0, 0.0, height)

    draw_closed_cylinder(base=size * 0.1, top=size * 0.1, height=height, 
                         color=color)
    glPopMatrix()

def draw_street_light():
    """
    Função responsável pela construção de uma lâmpada de rua.
    """
    quadric = gluNewQuadric()
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.5, 0.5, 0.5, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, 100)

    glRotatef(-90, 1.0, 0.0, 0.0)
    glPushMatrix()
    draw_closed_cylinder(base=0.7, top=0.0, height=0.5,
                         color=STREET_LIGHT_COLOR)
    glPopMatrix()

    glPushMatrix()
    draw_closed_cylinder(base=0.3, top=0.3, height=STREET_LIGHT_HEIGHT,
                         color=STREET_LIGHT_COLOR)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0.0, 0.10, STREET_LIGHT_HEIGHT -  0.22)
    glRotatef(-90, 0.0, 0.0, 1.0)
    glRotatef(60, 0.0, 1.0, 0.0)
    draw_closed_cylinder(base=0.3, top=0.3, height=2.0,
                         color=STREET_LIGHT_COLOR)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0.0, -1.5, STREET_LIGHT_HEIGHT + 0.75)
    glRotatef(90, 1.0, 0.0, 0.0)
    draw_closed_cylinder(base=0.3, top=0.3, height=1.0,
                         color=STREET_LIGHT_COLOR)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0.0, -2.4, STREET_LIGHT_HEIGHT + 0.35)
    draw_closed_cylinder(base=0.7, top=0.0, height=0.5,
                         color=STREET_LIGHT_COLOR,
                         base_on=False)
    
    # - LUZ -
    glColor3f(1.0, 0.0, 1.0)
    glLightfv(GL_LIGHT3, GL_POSITION, (0.0, 0.0, 0.0, 1.0))
    glLightfv(GL_LIGHT3, GL_SPOT_DIRECTION, (0.0, 0.0, -1.0))
    
    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (1.0, 0.7, 0.0, 1.0))
    glRotatef(180, 1.0, 0.0, 0.0)
    gluDisk(quadric, 0.0, 0.7, 32, 1) 
    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (0.0, 0.0, 0.0, 1.0))


    glPopMatrix()

    gluDeleteQuadric(quadric)
    glMaterialfv(GL_FRONT, GL_SPECULAR, (0.0, 0.0, 0.0, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, 0)



def draw_tree(width=1.0, height=4.0):
    """
    Função responsável por criar uma árvore.
    """
    glPushMatrix()

    # Tronco
    glPushMatrix()
    glRotatef(-90.0, 1.0, 0.0, 0.0)
    draw_closed_cylinder(base=width*0.60, top=width*0.60, height=height, 
                         color=(0.4, 0.2, 0.05))
    glPopMatrix()

    # Folhas
    glPushMatrix()
    glTranslatef(0.0, height, 0.0)
    glRotatef(-90.0, 1.0, 0.0, 0.0)
    draw_closed_cylinder(base=width*2.5, top=0.0, height=height*1.80, 
                         color = (0.1, 0.4, 0.1))
    glPopMatrix()

    glPopMatrix()


def interact_garage_gate():
    global garage_gate_angle
    global garage_gate_opening, garage_gate_tilting

    speed_angle = 0.8

    if not garage_gate_tilting:
        return

    if garage_gate_opening:
        garage_gate_angle += speed_angle
        if garage_gate_angle >= 90.0:
            garage_gate_angle = 90.0
            garage_gate_tilting = False

    else:
        garage_gate_angle -= speed_angle
        if garage_gate_angle <= 0.0:
            garage_gate_angle = 0.0
            garage_gate_tilting = False


def start_opening_gate():
    global garage_gate_opening, garage_gate_tilting
    garage_gate_opening = True
    garage_gate_tilting = True

def start_closing_gate():
    global garage_gate_opening, garage_gate_tilting
    garage_gate_opening = False
    garage_gate_tilting = True

def draw_garage_structure(tex_outside=None):
    """
    Função responsável pela construção da estrutura da garagem.
    - tex_outside: textura a utilizar do lado de fora
    """
    glMaterialfv(GL_FRONT, GL_SPECULAR, (0.35, 0.35, 0.35, 1.0))
    glMaterialfv(GL_FRONT, GL_SHININESS, 50)

    glPushMatrix()
    glRotatef(-90.0, 0.0, 1.0, 0.0) # Restabelecer orientação natural

    # - PAREDE DA ESQUERDA -
    glPushMatrix()
    glFrontFace(GL_CW)

    glTranslatef(-GARAGE_WIDTH * 0.5, 0.0, GARAGE_DEPTH * 0.5)
    glRotatef(-90.0, 0.0, 1.0, 0.0)
    glScalef(-1.0, 1.0, 1.0) # Trocar front & back;
                             # Vamos fazer isso várias vezes para que os materiais fiquem 
                             # orientados para o lado correto !
    draw_box(width=GARAGE_DEPTH - GARAGE_WALL_THICKNESS, 
             height=GARAGE_HEIGHT, 
             depth=GARAGE_WALL_THICKNESS,
             
             color_front=GARAGE_OUTSIDE_COLOR,
             color_back=GARAGE_INSIDE_WALLS_COLOR,
             color_side=GARAGE_OUTSIDE_COLOR,
             tex_f=tex_outside,
             tex_s=tex_outside,
             tile_v_side=0.15)
    
    glFrontFace(GL_CCW)
    glPopMatrix()

    # - PAREDE DA DIREITA -
    glPushMatrix()

    glTranslatef(GARAGE_WIDTH * 0.5, 0.0, GARAGE_DEPTH * 0.5)
    glRotatef(90.0, 0.0, 1.0, 0.0)
    draw_box(width=GARAGE_DEPTH - GARAGE_WALL_THICKNESS, 
             height=GARAGE_HEIGHT, 
             depth=GARAGE_WALL_THICKNESS,
             
             color_front=GARAGE_OUTSIDE_COLOR,
             color_back=GARAGE_INSIDE_WALLS_COLOR,
             color_side=GARAGE_OUTSIDE_COLOR,
             tex_f=tex_outside,
             tex_s=tex_outside,
             tile_v_side=0.15)
    
    glPopMatrix()

    # - PAREDE DE TRÁS -
    glPushMatrix()
    glFrontFace(GL_CW)
    glTranslatef(-GARAGE_WIDTH * 0.5, 0.0, -GARAGE_DEPTH * 0.5)
    glScalef(1.0, 1.0, -1.0)
    draw_box(width=GARAGE_WIDTH, 
             height=GARAGE_HEIGHT, 
             depth=GARAGE_WALL_THICKNESS,
             
             color_front=GARAGE_OUTSIDE_COLOR,
             color_back=GARAGE_INSIDE_WALLS_COLOR,
             color_side=GARAGE_OUTSIDE_COLOR,
             tex_f=tex_outside,
             tex_s=tex_outside,
             tile_v_side=0.15)
    
    glFrontFace(GL_CCW)
    glPopMatrix()


    # - CHÃO -
    glPushMatrix()
    glFrontFace(GL_CW)

    glTranslatef(-GARAGE_WIDTH * 0.5 + GARAGE_WALL_THICKNESS, 
                 0.001, # Para não ficar colado ao general_floor
                 -GARAGE_DEPTH * 0.5 + GARAGE_WALL_THICKNESS)
    glRotatef(90.0, 1.0, 0.0, 0.0)
    glScalef(1.0, 1.0, -1.0)
    draw_box(width=GARAGE_WIDTH - 2 * GARAGE_WALL_THICKNESS, 
             height=GARAGE_DEPTH - 2 * GARAGE_WALL_THICKNESS, 
             depth=0.001, # Chão fininho !
             
             color_front=GARAGE_FLOOR_COLOR,
             color_back=GARAGE_OUTSIDE_COLOR,
             color_side=GARAGE_OUTSIDE_COLOR)
    
    glFrontFace(GL_CCW)
    glPopMatrix()


    # - TELHADO -
    glPushMatrix()
    glFrontFace(GL_CW)
    glTranslatef(-GARAGE_WIDTH * 0.5 + GARAGE_WALL_THICKNESS, 
                 GARAGE_HEIGHT, 
                 -GARAGE_DEPTH * 0.5 + GARAGE_WALL_THICKNESS)
    glRotatef(90, 1.0, 0.0, 0.0)
    glScalef(1.0, 1.0, -1.0)
    draw_box(width=GARAGE_WIDTH  - 2 * GARAGE_WALL_THICKNESS, 
             height=GARAGE_DEPTH - 2 * GARAGE_WALL_THICKNESS, 
             depth=GARAGE_WALL_THICKNESS,
             
             color_front=GARAGE_OUTSIDE_COLOR,
             color_back=GARAGE_INSIDE_WALLS_COLOR,
             color_side=GARAGE_OUTSIDE_COLOR,
             tex_f=tex_outside,
             tex_s=tex_outside,
             tile_v_side=0.15)
    
    glFrontFace(GL_CCW)
    glPopMatrix()

    # - PAREDES ADICIONAL FRONTAL DA ESQUERDA -
    glPushMatrix()
    glTranslatef(-GARAGE_WIDTH * 0.5 + GARAGE_WALL_THICKNESS, 
                 0.0, 
                 GARAGE_DEPTH * 0.5)

    draw_box(width=GARAGE_FRONT_WALL_THICKNESS, 
             height=GARAGE_HEIGHT, 
             depth=GARAGE_WALL_THICKNESS,
             
             color_front=GARAGE_OUTSIDE_COLOR,
             color_back=GARAGE_INSIDE_WALLS_COLOR,
             color_side=GARAGE_OUTSIDE_COLOR,
             tex_f=tex_outside,
             tile_u_front=0.10,
             tex_s=tex_outside,
             tile_v_side=0.15)

    glPopMatrix()

    # - PAREDE ADICIONAL FRONTAL DA DIREITA - 
    glPushMatrix()
    glTranslatef(GARAGE_WIDTH * 0.5 - GARAGE_WALL_THICKNESS - GARAGE_FRONT_WALL_THICKNESS, 
                 0.0, 
                 GARAGE_DEPTH * 0.5)

    draw_box(width=GARAGE_FRONT_WALL_THICKNESS, 
             height=GARAGE_HEIGHT, 
             depth=GARAGE_WALL_THICKNESS,
             
             color_front=GARAGE_OUTSIDE_COLOR,
             color_back=GARAGE_INSIDE_WALLS_COLOR,
             color_side=GARAGE_OUTSIDE_COLOR,
             tex_f=tex_outside,
             tile_u_front=0.10,
             tex_s=tex_outside,
             tile_v_side=0.15)
    
    glPopMatrix()

    # - PAREDE ADICIONAL FRONTAL DE CIMA - 
    glPushMatrix()
    glTranslatef(-GARAGE_WIDTH * 0.5 + GARAGE_WALL_THICKNESS + GARAGE_FRONT_WALL_THICKNESS, 
                 GARAGE_HEIGHT - GARAGE_WALL_THICKNESS - GARAGE_FRONT_WALL_THICKNESS, 
                 GARAGE_DEPTH * 0.5)

    draw_box(width=GARAGE_WIDTH - 2 * GARAGE_WALL_THICKNESS - 2 * GARAGE_FRONT_WALL_THICKNESS, 
             height=GARAGE_WALL_THICKNESS + GARAGE_FRONT_WALL_THICKNESS, 
             depth=GARAGE_WALL_THICKNESS,
             
             color_front=GARAGE_OUTSIDE_COLOR,
             color_back=GARAGE_INSIDE_WALLS_COLOR,
             color_side=GARAGE_OUTSIDE_COLOR,
             tex_f=tex_outside,
             tile_v_front=0.15,
             tex_s=tex_outside,
             tile_v_side=0.15)
    
    glPopMatrix()
    glPopMatrix()
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.0, 0.0, 0.0, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, 0)


def draw_garage_gate(tex_front=None):
    """
    Função responsável pela construção do portão da garagem.
    - tex_front: textura do lado exterior do portão
    """
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.35, 0.35, 0.35, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, 50)
    rot_x = GARAGE_WIDTH * 0.5 - GARAGE_WALL_THICKNESS - GARAGE_FRONT_WALL_THICKNESS
    rot_y = GARAGE_HEIGHT - 2 * GARAGE_FRONT_WALL_THICKNESS - 0.40 # para não raspar no teto
    rot_z = -GARAGE_WALL_THICKNESS

    # Definir ponto de rotação (a dobradiça)
    glTranslatef(rot_x, rot_y, rot_z)
    glRotatef(-garage_gate_angle, 1.0, 0.0, 0.0)
    glTranslatef(-rot_x, -rot_y, -rot_z)

    draw_box(width=GARAGE_WIDTH - 2 * GARAGE_FRONT_WALL_THICKNESS - 2 * GARAGE_WALL_THICKNESS, 
             height=GARAGE_HEIGHT - GARAGE_WALL_THICKNESS - GARAGE_FRONT_WALL_THICKNESS, 
             depth=GARAGE_WALL_THICKNESS * 0.5,
             color_front=(0.90, 0.90, 0.90),
             color_back=GARAGE_OUTSIDE_COLOR,
             color_side=(1.0, 1.0, 1.0),
             tex_f=tex_front)

    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.0, 0.0, 0.0, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, 0)