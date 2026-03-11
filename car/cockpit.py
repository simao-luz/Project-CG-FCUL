"""
Módulo para construção de todos os objetos pertencentes
ao habitáculo de um veículo, como travão de mão, pedais...
Desenvolvido por:
    - Diogo Vasconcelos, fc61809
    - Miguel Guise, fc61822
    - Simão da Luz, fc61816
Em: 01/12/2026
"""

from utils.helpers import *
from utils.variables import *

def draw_seat(thick_front=2.0, thick_back=2.0, color=(0.7, 0.46, 0.25)):
    """
    Função responsável pela criação do assento; extrusão + coloração
    - thick_front: o quanto o assento cresce em z+
    - thick_back: o quanto o assento cresce em z-
    """
    def build_seat_outline(arc_segments=10):
        """
        Função responsável pela criação do outline 2D para a construção da
        parte de baixo do assento.
        - arc_segments: número de segmentos na área arredondada
        """
        base_poly = [(-0.3, 1.2), (0.0, 0.0), (3.0, 0.0), (3.3, 2.0), (0.3, 2.0)] # Pentágono irregular (ccw)
        corners = [2]
        r = 1.0

        return round_outline(base_poly, corners, r, arc_segments)

    def build_backseat_outline(arc_segments=10):
        """
        Função responsável pela criação do outline 2D para a construção da parte
        das costas do assento do veículo - complementa-se com a função
        que cria a parte de baixo do assento.
        - arc_segments: número de segmentos na área arredondada
        """
        base_poly = [(0.3, 2.0), (3.3, 2.0), (3.8, 6.0), (3.3, 6.0), (3.0, 2.2)]
        corners = [4]
        r = 0.4

        return round_outline(base_poly, corners, r, arc_segments)

    outline = build_backseat_outline()
    extrude_outline(outline, 0, 
                    thick_front, 
                    thick_back, 
                    
                    color_front=color, 
                    color_back=color, 
                    color_side=color)
    
    outline = build_seat_outline()
    extrude_outline(outline, 0, 
                    thick_front, 
                    thick_back, 
                    
                    color_front=color, 
                    color_back=color, 
                    color_side=color)


def draw_steering_wheel(horn_color=(0.1, 0.1, 0.1), 
                        steering_wheel_color=(0.0, 0.0, 0.0),
                        supports_color=(0.1, 0.05, 0.05)):
    """
    Função responsável pela construção de um volante.
    - horn_color:           cor do botão da buzina
    - steering_wheel_color: cor do próprio volante
    - supports_color:       cor dos suportes ao volante (pipes)
    """
    glPushMatrix()

    glRotatef(90.0, 0.0, 1.0, 0.0)

    base = 0.5
    # - BUZINA -
    draw_closed_cylinder(base=base, 
                         top=base, 
                         height=0.1, 
                         color=horn_color)

    # - CÍRCULO DO VOLANTE -
    glTranslatef(0.0, 0.0, base)
    glColor3f(*steering_wheel_color)
    glPushMatrix()
    glutSolidTorus(0.2, 1.4, 32, 64)
    glPopMatrix()

    # - SUPORTES -
    glRotatef(60.0, 1.0, 0.0, 0.0)
    glTranslatef(0.0, -0.7, -0.4)

    draw_closed_cylinder(base=base * 0.20, 
                         top=base * 0.20, 
                         height=1.6, 
                         color=supports_color, 
                         top_on=False, base_on=False)

    glRotatef(-90.0, 0.0, 1.0, 0.5)
    draw_closed_cylinder(base=base * 0.20, 
                         top=base * 0.20, 
                         height=1.6, 
                         color=supports_color, 
                         top_on=False, base_on=False)

    glRotatef(180.0, 0.0, 1.0, 0.5)
    draw_closed_cylinder(base=base * 0.20, 
                         top=base * 0.20, 
                         height=1.6, 
                         color=supports_color, 
                         top_on=False, base_on=False)

    glPopMatrix()


def draw_brakes(box_color=(0.4, 0.4, 0.4), 
                handbrake_color=(0.3, 0.3, 0.3),
                gear_stick_color=(0.3, 0.3, 0.3)):
    """
    Função responsável pela caixa que abriga o travão de mão e 
    o manete, bem como estes dois elementos referidos.
    - box_color:        cor da caixa de mudanças
    - handbrake_color:  cor do travão de mão
    - gear_stick_color: cor da alavanca de mudanças
    """
    #  - CAIXA -
    glPushMatrix()
    glTranslatef(-BRAKE_BOX_WIDTH * 0.5, CAR_FLOOR_HEIGHT * 0.5 + BRAKE_BOX_DEPTH, BRAKE_BOX_DEPTH * 0.20 + 0.05)
    glRotatef(-90.0, 1.0, 0.0, 0.0)
    draw_box(width=BRAKE_BOX_WIDTH,
             height=BRAKE_BOX_HEIGHT,
             depth=BRAKE_BOX_DEPTH,
             r=0.05,
             corners=[0, 1, 2, 3],

             color_front=box_color,
             color_back=box_color,
             color_side=box_color
    )
    glPopMatrix()

    # - TRAVÃO DE MÃO -
    glPushMatrix()
    glTranslatef(-BRAKE_BOX_WIDTH * 0.10, 2 * BRAKE_BOX_DEPTH, 0.0)
    glRotatef(90, 1.0, 0.0, 0.0)
    glRotatef(50, 0.0, 1.0, 0.0)

    # Travão de mão
    draw_closed_cylinder(base=0.1, top=0.1, height=0.8, 
                         color=handbrake_color, 
                         top_on=False)
    
    # Botão do travão de mão (+ saído!)  
    glTranslatef(0.0, 0.0, -0.05)                                                             
    draw_closed_cylinder(base=0.05, top=0.05, height=0.06, 
                         color=(0.7, 0.7, 0.7), 
                         top_on=False)
    glPopMatrix()

    glPushMatrix()

    # - MANETE -
    glTranslatef(-BRAKE_BOX_WIDTH * 0.40, CAR_FLOOR_HEIGHT * 0.5 + 2 * BRAKE_BOX_DEPTH, 0.0)
    glRotatef(90, 1.0, 0.0, 0.0)
    draw_closed_cylinder(base=0.07, top=0.03, height=0.4, 
                         color=gear_stick_color, 
                         top_on=False)
    
    glTranslatef(0.0, 0.0, -0.07)
    draw_closed_cylinder(base=0.03, top=0.07, height=0.07, 
                         color=(0.7, 0.7, 0.7), 
                         top_on=False)
    glPopMatrix()


def draw_pedals(thick_front=0.01, thick_back=0.0, color=(0.2, 0.2, 0.2)):
    """
    Função responsável dos 3 pedais do veículo!
    - thick_front: extrusão em z+
    - thick_back:  extrusão em z-
    - color:       cor dos pedais
    """
    def build_pedal_1_outline(arc_segments=10):
        """
        Função responsável por criar o outline 2D necessário à criação do pedal
        do acelerador.
        - arc_segments: número de segmentos na área arredondada
        """
        base_poly = [(0.0, 0.4), (0.0, 0.1), (-0.05, 0.0), (0.2, 0.0), (0.2, 0.4)]
        corners = [0, 1, 3, 4]
        r = 0.05

        return round_outline(base_poly, corners, r, arc_segments)

    def build_pedal_2_outline(arc_segments=10):
        """
        Função responsável por criar o outline 2D necessário à criação do pedal
        do travão.
        - arc_segments: número de segmentos na área arredondada
        """
        base_poly = [(0.0, 0.2), (0.0, 0.0), (0.15, 0.0), (0.2, 0.1), (0.2, 0.2)]
        corners = [0, 1, 2, 3, 4]
        r = 0.05

        return round_outline(base_poly, corners, r, arc_segments)

    def build_pedal_3_outline(arc_segments=10):
        """
        Função responsável por criar o outline 2D necessário à criação do pedal
        da embraiagem.
        - arc_segments: número de segmentos na área arredondada
        """
        base_poly = [(0.0, 0.25), (0.0, 0.1), (0.03, 0.0), (0.17, 0.0), (0.2, 0.1), (0.2, 0.25)]
        corners = [0, 1, 2, 3, 4, 5, 6]
        r = 0.05

        return round_outline(base_poly, corners, r, arc_segments)
    
    # - PEDAL DO ACELERADOR -
    glPushMatrix()
    outline = build_pedal_1_outline()
    glRotatef(-50, 1.0, 0.0, 0.0)
    extrude_outline(outline, 0, 
                    thick_front, thick_back, 
                    color_front=color, 
                    color_back=color, 
                    color_side=color)

    # - PEDAL DO TRAVÃO -
    glTranslatef(-0.3, 0.2, 0)
    outline = build_pedal_2_outline()
    extrude_outline(outline, 0, 
                    thick_front, thick_back, 

                    color_front=color, 
                    color_back=color, 
                    color_side=color)

    # - PEDAL DA EMBRAIAGEM -
    glTranslatef(-0.3, -0.05, 0)
    outline = build_pedal_3_outline()
    extrude_outline(outline, 0, thick_front, thick_back, 
                    
                    color_front=color, 
                    color_back=color, 
                    color_side=color)

    # - CABOS DOS PEDAIS -
    glRotatef(90, 1.0, 0.0, 0.0)

    glTranslatef(0.1, 0.0, -0.5)
    draw_closed_cylinder(base=0.01, top=0.01, height=0.4, 
                         color=color, 
                         top_on=False, base_on=False)
    glTranslatef(0.3, 0.0, 0.0)
    draw_closed_cylinder(base=0.01, top=0.01, height=0.4, 
                         color=color, 
                         top_on=False, base_on=False)
    glTranslatef(0.3, 0.0, 0.0)
    draw_closed_cylinder(base=0.01, top=0.01, height=0.4, 
                         color=color, 
                         top_on=False, base_on=False)
    glPopMatrix()


def draw_dashboard(color_front=(0.4, 0.4, 0.4), color_back=(0.4, 0.4, 0.4), color_side=(0.4, 0.4, 0.4)):
    """
    Função responsável pela criação do tablier/painel; extrusão + coloração
    - color_front: cor da frente do painel
    - color_back:  cor de trás do painel
    - color_side:  cor dos lados do painel
    """
    def build_table_outline(arc_segments=10):
        """
        Função responsável pela criação outline 2D do tablier do veículo, 
        elegível para extrusão.
        - arc_segments: número de segmentos na área arredondada
        """
        base_poly = [(0.0, TABLE_HEIGHT), (0.0, 0.0), (TABLE_WIDTH * 0.7, 0.0), (TABLE_WIDTH, TABLE_HEIGHT)]
        corners = [2, 3]
        r = 0.05

        return round_outline(base_poly, corners, r, arc_segments)

    outline = build_table_outline()
    extrude_outline(outline, 0, 
                    thick_front=0.0, 
                    thick_back=CAR_FLOOR_DEPTH - 2 * WALL_THICKNESS, 

                    color_front=color_front, 
                    color_back=color_back, 
                    color_side=color_side)
