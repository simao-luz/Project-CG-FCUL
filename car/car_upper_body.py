"""
Módulo de construção das partes superiores de um veículo !
Desenvolvido por:
    - Diogo Vasconcelos, fc61809
    - Miguel Guise, fc61822
    - Simão da Luz, fc61816
Em: 01/12/2026
"""

from utils.helpers import *
from utils.variables import *

def draw_windshield(color_front=(0.3, 1, 1), color_side=(0.1, 1, 1), color_back=(0.3, 1, 1), alpha=0.2):
    """
    Função responsável pela construção de um parabrisas.
    - color_front: cor da frente do parabrisas
    - color_side:  cor dos lados do parabrisas
    - color_back:  cor da parte traseira do parabrisas
    - alpha:       opacidade das cores do parabrisas (tendencialmente <1 para dar aspeto transparente)
    """
    glDepthMask(GL_FALSE) # Permite ver as coisas por detrás do vidro!
    glRotatef(WINDSHIELD_ANGLE, 1.0, 0.0, 0.0)

    draw_box(width=WINDSHIELD_WIDTH - 2 * PIPE_WIDTH,
            height=WINDSHIELD_HEIGHT, 
            depth=WINDSHIELD_DEPTH,
            corners=[0, 1],
            r=0.2,

            color_front=color_front, 
            color_side=color_side, 
            color_back=color_back, 
            alpha=alpha)
    glDepthMask(GL_TRUE) # Restabelece default


def draw_roll_cage(color=(0.0, 0.0, 0.0)):
    """
    Função responsável pela criação da roll cage do veículo (conjunto
    de pipes/cilindros)
    """

    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.5, 0.5, 0.5, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, 100)

    # - SIDE 1 PROTECTION TO WINDSHIELD -
    glPushMatrix()
    glTranslatef(-CABIN_FLOOR_WIDTH * 0.5, 
                 DOOR_TOP_FRONT_HEIGHT - CAR_FLOOR_HEIGHT * 0.5, 
                 CAR_FLOOR_DEPTH * 0.5 - WALL_THICKNESS + PIPE_WIDTH)
    glRotatef(90.0, 0.0, 1.0, 0.0)
    glRotatef(-WINDSHIELD_ANGLE - 10, 1.0, 0.0, 0.0)

    draw_closed_cylinder(base=PIPE_WIDTH,
                         top=PIPE_WIDTH,
                         height=WINDSHIELD_HEIGHT,

                         color=color)
    glPopMatrix()

    # - SIDE 2 PROTECTION TO WINDSHIELD -
    glPushMatrix()
    glTranslatef(-CABIN_FLOOR_WIDTH * 0.5, 
                DOOR_TOP_FRONT_HEIGHT - CAR_FLOOR_HEIGHT * 0.5, 
                -CAR_FLOOR_DEPTH * 0.5 + WALL_THICKNESS - PIPE_WIDTH)
    glRotatef(90.0, 0.0, 1.0, 0.0)
    glRotatef(-WINDSHIELD_ANGLE - 10, 1.0, 0.0, 0.0)
    draw_closed_cylinder(base=PIPE_WIDTH,
                         top=PIPE_WIDTH,
                         height=WINDSHIELD_HEIGHT,

                         color=color)
    glPopMatrix()

    # - TOP PROTECTION TO WINDSHIELD -
    glPushMatrix()
    glTranslatef(-CABIN_FLOOR_WIDTH * 0.5 + 2 * TABLE_WIDTH - 0.141, 
                DOOR_TOP_FRONT_HEIGHT - CAR_FLOOR_HEIGHT * 0.5 + WINDSHIELD_HEIGHT * 0.75, 
                -CAR_FLOOR_DEPTH * 0.5 + WALL_THICKNESS - PIPE_WIDTH * 2)
    draw_closed_cylinder(base=PIPE_WIDTH,
                         top=PIPE_WIDTH,
                         height=WINDSHIELD_WIDTH,

                         color=color)
    glPopMatrix()

    # - SIDE 1 TOP PIPE -
    glPushMatrix()
    glTranslatef(-CABIN_FLOOR_WIDTH * 0.5 + 2 * TABLE_WIDTH - 0.141, 
                DOOR_TOP_FRONT_HEIGHT - CAR_FLOOR_HEIGHT * 0.5 + WINDSHIELD_HEIGHT * 0.75, 
                CAR_FLOOR_DEPTH * 0.5 - WALL_THICKNESS + PIPE_WIDTH)
    glRotatef(90, 0.0, 1.0, 0.0)
    glRotatef(-DOOR_ANGLE, 1.0, 0.0, 0.0)
    draw_closed_cylinder(base=PIPE_WIDTH,
                         top=PIPE_WIDTH,
                         height=DOOR_WIDTH,

                         color=color)
    glPopMatrix()

    # - SIDE 2 TOP PIPE -
    glPushMatrix()
    glTranslatef(-CABIN_FLOOR_WIDTH * 0.5 + 2 * TABLE_WIDTH - 0.141,  
                DOOR_TOP_FRONT_HEIGHT - CAR_FLOOR_HEIGHT * 0.5 + WINDSHIELD_HEIGHT * 0.75, 
                -CAR_FLOOR_DEPTH * 0.5 + WALL_THICKNESS - PIPE_WIDTH)
    glRotatef(90, 0.0, 1.0, 0.0)
    glRotatef(-DOOR_ANGLE, 1.0, 0.0, 0.0)
    draw_closed_cylinder(base=PIPE_WIDTH,
                         top=PIPE_WIDTH,
                         height=DOOR_WIDTH,

                         color=color)
    glPopMatrix()

    # - SIDE 1 BACK PIPE -
    glPushMatrix()
    glTranslatef(-CABIN_FLOOR_WIDTH * 0.5 + 2 * TABLE_WIDTH - 0.141 + DOOR_WIDTH - PIPE_WIDTH, 
                DOOR_TOP_FRONT_HEIGHT - CAR_FLOOR_HEIGHT * 0.5 + WINDSHIELD_HEIGHT * 0.75 + 2 * PIPE_WIDTH + 
                DOOR_WIDTH * math.tan(DOOR_ANGLE) - WINDSHIELD_HEIGHT, 

                CAR_FLOOR_DEPTH * 0.5 - WALL_THICKNESS + PIPE_WIDTH)
    glRotatef(90, 1.0, 0.0, 0.0)
    draw_closed_cylinder(base=PIPE_WIDTH,
                         top=PIPE_WIDTH,
                         height=WINDSHIELD_HEIGHT,

                         color=color)
    glPopMatrix()

    # - SIDE 2 BACK PIPE -
    glPushMatrix()
    glTranslatef(-CABIN_FLOOR_WIDTH * 0.5 + 2 * TABLE_WIDTH - 0.141 + DOOR_WIDTH - PIPE_WIDTH, 
                DOOR_TOP_FRONT_HEIGHT - CAR_FLOOR_HEIGHT * 0.5 + WINDSHIELD_HEIGHT * 0.75 + 2 * PIPE_WIDTH + 
                DOOR_WIDTH * math.tan(DOOR_ANGLE) - WINDSHIELD_HEIGHT, 

                -CAR_FLOOR_DEPTH * 0.5 + WALL_THICKNESS - PIPE_WIDTH)
    glRotatef(90, 1.0, 0.0, 0.0)
    draw_closed_cylinder(base=PIPE_WIDTH,
                         top=PIPE_WIDTH,
                         height=WINDSHIELD_HEIGHT,

                         color=color)
    glPopMatrix()

    # - BACK TOP PIPE -
    glPushMatrix()
    glTranslatef(-CABIN_FLOOR_WIDTH * 0.5 + 2 * TABLE_WIDTH - 0.141 + DOOR_WIDTH - PIPE_WIDTH, 
                DOOR_TOP_FRONT_HEIGHT - CAR_FLOOR_HEIGHT * 0.5 + WINDSHIELD_HEIGHT * 0.75 + 2 * PIPE_WIDTH + 
                DOOR_WIDTH * math.tan(DOOR_ANGLE) - WINDSHIELD_HEIGHT - PIPE_WIDTH, 

                -CAR_FLOOR_DEPTH * 0.5 + WALL_THICKNESS - PIPE_WIDTH)
    draw_closed_cylinder(base=PIPE_WIDTH,
                         top=PIPE_WIDTH,
                         height=WINDSHIELD_WIDTH - 2 * PIPE_WIDTH,

                         color=color)
    glPopMatrix()

    # - BACK TOP-DOWN PIPE -
    glPushMatrix()
    glTranslatef(-CABIN_FLOOR_WIDTH * 0.5 + 2 * TABLE_WIDTH - 0.141 + DOOR_WIDTH - PIPE_WIDTH, 
                DOOR_TOP_FRONT_HEIGHT - CAR_FLOOR_HEIGHT * 0.5 + WINDSHIELD_HEIGHT * 0.75 + 2 * PIPE_WIDTH + 
                DOOR_WIDTH * math.tan(DOOR_ANGLE) - WINDSHIELD_HEIGHT - 0.5, 

                -CAR_FLOOR_DEPTH * 0.5 + WALL_THICKNESS - PIPE_WIDTH)
    draw_closed_cylinder(base=PIPE_WIDTH,
                         top=PIPE_WIDTH,
                         height=WINDSHIELD_WIDTH - 2 * PIPE_WIDTH,

                         color=color)
    glPopMatrix()
    
    glMaterialfv(GL_FRONT, GL_SPECULAR, (0.0, 0.0, 0.0, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, 0)

def draw_lat_rearview_mirror(color=(0.2, 0.2, 0.2)):
    """
    Função responsável pela criação de um retrovisor lateral; extrusão + coloração
    - color: cor do retrovisor lateral e do seu suporte
    """
        
    def build_lat_rearview_mirror_outline(arc_segments=10):
        """
        Função responsável pela criação outline 2D dos retrovisores laterais do veículo, 
        elegível para extrusão
        - arc_segments: número de segmentos na área arredondada
        """
        base_poly = [(0.0, 0.7), (0.0, 0.0), (1.0, 0.0), (1.0, 0.7)]
        corners = [0, 1, 2, 3]
        r = 0.35

        return round_outline(base_poly, corners, r, arc_segments)

    glRotatef(90, 0.0, 1.0, 0.0)
    outline = build_lat_rearview_mirror_outline()

    extrude_outline(outline, 0, 
                    thick_front=0.0, 
                    thick_back=0.15,

                    color_front=(2.0, 2.0, 2.0), # Branco super vivo
                    color_back=color,
                    color_side=color)
    
    # - ESPELHO DO RETROVISOR -
    glTranslatef(0.0, 0.0, 0.05) # Permite que o espelho esteja ligeiramente saído !
    
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (2.0, 2.0, 2.0, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, 128.0) # Muito brilhante
    glDepthMask(GL_FALSE)

    extrude_outline(outline, 0, 
                    thick_front=0.0, 
                    thick_back=0.05,

                    color_front=(0.3, 1, 1), 
                    color_side=(0.1, 1, 1), 
                    color_back=(0.3, 1, 1), 
                    alpha=0.2)
    
    # Restabelece defaults.
    glDepthMask(GL_TRUE)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.0, 0.0, 0.0, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, 0.0)


    glRotatef(90, 0.0, 1.0, 0.0)
    # - SUPORTE DO RETROVISOR -
    glTranslatef(0.15, 0.2, 0.9)
    glRotatef(20, 1.0, 0.0, 0.0)
    
    draw_closed_cylinder(top=0.05, 
                         base=0.05, 
                         height=0.5, 
                         top_on=False, base_on=False, 
                         color=color)


def draw_central_rearview_mirror(color=(0.4, 0.4, 0.4)):
    """
    Função responsável pela criação de um retrovisor central; extrusão + coloração
    - color: cor do retrovisor central e do seu suporte
    """
        
    def build_center_rearview_outline(arc_segments=10):
        """
        Função responsável pela criação outline 2D do retrovisor central do veículo, 
        elegível para extrusão.
        - arc_segments: número de segmentos na área arredondada
        """
        base_poly = [(0.0, 0.4), (0.0, 0.0), (1.0, 0.0), (1.0, 0.4)]
        corners = [0, 1, 2, 3]
        r = 0.2

        return round_outline(base_poly, corners, r, arc_segments)
    
    outline = build_center_rearview_outline()

    extrude_outline(outline, 0, 
                    thick_front=0.0, 
                    thick_back=0.07,

                    color_front=(2,2,2),
                    color_back=color,
                    color_side=color)
    
    glTranslatef(0.0, 0.0, 0.05) 

    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (2.0, 2.0, 2.0, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, 128)
    glDepthMask(GL_FALSE)

    # - ESPELHO DO RETROVISOR -
    extrude_outline(outline, 0, 
                    thick_front=0.0, 
                    thick_back=0.03,

                    color_front=(0.3, 1, 1), 
                    color_side=(0.1, 1, 1), 
                    color_back=(0.3, 1, 1), 
                    alpha=0.2)
    
    glDepthMask(GL_TRUE)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.0, 0.0, 0.0, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, 0)

    # Transladar o suporte do retrovisor
    glTranslatef(0.5, 0.7, -0.07)
    glRotatef(90, 1.0, 0.0, 0.0)
    # - SUPORTE DO RETROVISOR -
    draw_closed_cylinder(top=0.03, 
                         base=0.03, 
                         height=0.3, 
                         top_on=False,
                         color=color)
    

def draw_protection(width=1.0,
                    height=1.0,
                    depth=1.0,
                    r=None,
                    corners=None,
                    color=(0.0, 0.0, 0.0),
                    alpha=1.0,
                    caps=True,
                    tex_f=None,
                    texture_b=None,
                    tex_s=None,
                    tile_u_front=1.0, tile_v_front=1.0, 
                    tile_u_back=1.0, tile_v_back=1.0,
                    tile_u_side=1.0, tile_v_side=1.0):
    """
    Função responsável pela criação de uma proteção (a paredes)
    Para ver o significa cada argumento é aconselhado ver a função extrude_outline.
    """

    glFrontFace(GL_CCW)
    draw_box(width=width,
             height=height,
             depth=depth,
             r=r,
             corners=corners,
             color_front=color,
             color_back=color,
             color_side=color,
             alpha=alpha,
             caps=caps,
             tex_f=tex_f,
             tex_b=texture_b,
             tex_s=tex_s,
             tile_u_front=tile_u_front, tile_v_front=tile_v_front, 
             tile_u_back=tile_u_back, tile_v_back=tile_v_back,
             tile_u_side=tile_u_side, tile_v_side=tile_v_side)