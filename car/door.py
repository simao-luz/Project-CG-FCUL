"""
Módulo para construção de uma porta de um veículo, bem como
do seu puxador e da sua proteção superior.
    - Diogo Vasconcelos, fc61809
    - Miguel Guise, fc61822
    - Simão da Luz, fc61816
Em: 01/12/2026
"""

from utils.helpers import *
from utils.variables import *

def draw_door_handle(color_front=(0,0,0), color_back=(0,0,0), color_side=(0,0,0)):
    """
    Função responsável pela criação do puxador de uma porta.
    - color_front: cor da frente do puxador
    - color_back:  cor de trás do puxador
    - color_side:  cor dos lados do puxador
    """

    def build_door_handle_outline(arc_segments=10):
        """
        Função responsável pela construção de um outline 2D para o puxador
        da porta, visto a ser extrusado.
        - arc_segments: número de segmentos utilizados no arredondamento
        """

        x0     = DOOR_WIDTH           * 0.70
        y0     = DOOR_TOP_REAR_HEIGHT * 0.50
        width  = DOOR_WIDTH           * 0.20 
        height = DOOR_TOP_REAR_HEIGHT * 0.10

        base_poly = [(x0, y0), (x0, y0 - height), (x0 + width, y0 - height), (x0 + width, y0)] # ccw
        corners = [2]
        
        r = 0.1

        rounded = round_outline(base_poly, corners, r, arc_segments)

        return rounded

    outline = build_door_handle_outline()
    glFrontFace(GL_CCW)

    glRotatef(DOOR_ANGLE, 0.0, 0.0, 1.0)

    extrude_outline(outline, 
                    z_center=0.0, 
                    thick_front=DOOR_HANDLE_THICKNESS, 
                    thick_back=0.0,
                    color_front=color_front, 
                    color_side=color_side,
                    color_back=color_back
    )


def draw_door(color_front, color_back, color_side, tex_front=None):
    """
    Função responsável pela criação de uma porta.
    - color_front: cor da frente da parte da frente
    - color_back:  cor de trás da parte de trás da porta
    - color_side:  cor dos lados da porta
    - tex_front:   textura a aplicar à parte da frente da porta
    """

    def build_door_outline(arc_segments=10):
        """
        Função responsável pela construção de um outline 2D para a porta 
        a fim de ser extrusado.
        - arc_segments: número de segmentos utilizados no arredondamento de um canto
        """
        base_poly = [(0.0, DOOR_TOP_FRONT_HEIGHT), (0.0, 0.0), (DOOR_WIDTH, 0.0), (DOOR_WIDTH, DOOR_TOP_REAR_HEIGHT)]

        corners = []

        rounded = round_outline(base_poly, corners, DOOR_R, arc_segments)

        return rounded

    outline = build_door_outline()

    extrude_outline(outline, 
                    z_center=0.0, 
                    thick_front=0.0, 
                    thick_back=DOOR_THICKNESS, 
                    color_front=color_front, 
                    color_back=color_back, 
                    color_side=color_side,
                    tex_front=tex_front
    )


def draw_door_protection(width=0.0, height=0.0, depth=0.0, color=(0.0, 0.0, 0.0)):
    """
    Função responsável pela construção da proteção de uma porta criada
    em draw_door.
    - width:  comprimento da proteção
    - height: altura da proteção
    - depth:  largura da proteção
    - color:  cor da proteção
    """
    glFrontFace(GL_CCW)
    glRotatef(DOOR_ANGLE, 0.0, 0.0, 1.0)
    glRotatef(-90.0, 1.0, 0.0, 0.0)

    draw_box(width=width,
             height=height,
             depth=depth,
             color_front=color,
             color_back=color,
             color_side=color)
