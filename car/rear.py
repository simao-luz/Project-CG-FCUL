"""
Módulo para construção da traseira de um veículo,
bem como dos seus faróis traseiros.
    - Diogo Vasconcelos, fc61809
    - Miguel Guise, fc61822
    - Simão da Luz, fc61816
Em: 01/12/2026
"""

from utils.helpers import *
from utils.variables import *

def draw_rear_bumper_wall(tex=None): 
    """
    Função responsável pela construção de um poliedro
    que representa uma parede traseira ao para-choques
    do veículo
    - tex: textura a aplicar nessa parede/poliedro
    """

    outline=[(0.0, 0.0), 
            (REAR_BUMPER_WIDTH, 0.0),
            (REAR_BUMPER_WIDTH, DOOR_TOP_FRONT_HEIGHT),
            (REAR_BUMPER_WIDTH - R_TRUNK * 0.5, DOOR_TOP_REAR_HEIGHT),
            (0.0, DOOR_TOP_REAR_HEIGHT),
            (0.0, DOOR_TOP_FRONT_HEIGHT)]
    
    extrude_outline(outline, z_center=0.0,
                    thick_front=0.0,
                    thick_back=WALL_THICKNESS,

                    color_front=CAR_OUTSIDE_COLOR,
                    color_side=CAR_OUTSIDE_COLOR,
                    color_back=CAR_OUTSIDE_COLOR,
                    tex_front=tex,
                    tex_back=tex,
                    tex_side=tex,
                    tile_u_front=0.7, tile_v_front=0.7,
                    tile_u_side=0.7, tile_v_side=0.2)


def draw_rear_light(color=(2.0, 0.0, 0.0)):
    """
    Função responsável pela construção de um farol traseiro
    - color: cor dos farol
    """

    quadric = gluNewQuadric()

    glPushMatrix()
    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (*color, 1.0))
    glRotatef(90, 0, 1, 0)
    gluDisk(quadric, 0.0, 0.15, 32, 1)
    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (0.0, 0.0, 0.0, 1.0)) # Resetar material
    glPopMatrix()

    gluDeleteQuadric(quadric)