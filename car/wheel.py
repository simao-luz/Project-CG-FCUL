"""
Módulo para a construção das rodas de um veículo.
Desenvolvido por:
    - Diogo Vasconcelos, fc61809
    - Miguel Guise, fc61822
    - Simão da Luz, fc61816
Em: 01/12/2026
"""

from utils.helpers import *
from utils.variables import *

def draw_wheel(color_disk=(0.35, 0.35, 0.35), color_spoke=(0.7, 0.7, 0.7), color_tire=(0.1, 0.1, 0.1), front=False):
    """
    Função responsável pela construção de uma roda (pneu + jante (com roda de raios)).
    - color_disk:    cor da jante
    - color_spoke:   cor da roda de raios
    - color_tire:    cor do pneu
    - front:         é pneu da frente?
    """
    
    def build_spoke_outline(arc_segments=10):
        """
        Função responsável pela criação de um raio de roda!
        Uma roda poderá conterá vários raios de roda (neste caso, temos 5).
        - arc_segments: número de segmentos na área arredondada
        """
        x0 = 0.0
        x1 = 1.5
        y_top = 1.0
        y_center = 0.75
        y_bot = 0.5

        base_poly = [(x0, y_top),
                    (x0, y_bot),
                    (x0 + 0.01, y_center),
                    (x1, y_bot),
                    (x1, y_top)]
                    
        corners = [2]
        r = 0.2

        return round_outline(base_poly, corners, r, arc_segments, concave=True)

    def extrude_spoke_outline(z=0, thick_front=0.01, thick_back=0.0):
        """
        Função responsável por extrusar um raio de roda.
        - z:           posição central onde ocorrerá a extrusão em z+ e z-
        - thick_front: unidades a extrusar em z+
        - thick_back:  unidades a extrusar em z-
        """
        outline = build_spoke_outline()
        glPushMatrix()
        glTranslatef(0.0, 0.0, z)

        extrude_outline(outline, 0.0, 
                        thick_front, 
                        thick_back, 
                        color_front=(0.9, 0.9, 0.9), 
                        color_side=(0.8, 0.8, 0.8), 
                        color_back=(0.9, 0.9, 0.9))

        glPopMatrix()

    quadric = gluNewQuadric()
    
    # Dependendo da roda, os tamanhos serão diferentes !
    if front:
        base = FRONT_WHEEL_R
        inner = FRONT_WHEEL_DEPTH
    else:
        base = REAR_WHEEL_R
        inner = REAR_WHEEL_DEPTH

    glPushMatrix()

    # -------- JANTE (DISCO DE UM LADO E DE OUTRO) --------
    glColor3f(*color_disk)
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.2, 0.2, 0.2, 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (0.7, 0.7, 0.7, 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.3, 0.3, 0.3, 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, 128)

    # - DISCOS -
    glPushMatrix()
    glRotatef(180.0, 0.0, 1.0, 0.0)
    gluDisk(quadric, 0.0, base, 32, 1)
    glPopMatrix()

    glPushMatrix()
    glTranslated(0.0, 0.0, inner - 0.1)
    gluDisk(quadric, 0.0, base, 32, 1)
    glPopMatrix()

    # - RODA DE RAIOS -
    glColor3f(*color_spoke)

    glPushMatrix()
    glTranslated(0.33, -0.7, 0.0)
    extrude_spoke_outline(z=inner - 0.09)
    extrude_spoke_outline(z=-0.02)
    glPopMatrix()

    glPushMatrix()
    glRotatef(72, 0, 0, 1)
    glTranslated(0.37, -0.73, 0.0)
    extrude_spoke_outline(z=inner - 0.09)
    extrude_spoke_outline(z=-0.02)

    glRotatef(72, 0, 0, 1)
    glTranslated(0.93, -0.23, 0.0)
    extrude_spoke_outline(z=inner - 0.09)
    extrude_spoke_outline(z=-0.02)

    glRotatef(72, 0, 0, 1)
    glTranslated(0.93, -0.23, 0.0)
    extrude_spoke_outline(z=inner - 0.09)
    extrude_spoke_outline(z=-0.01)

    glRotatef(72, 0, 0, 1)
    glTranslated(0.95, -0.20, 0.0)
    extrude_spoke_outline(z=inner - 0.09)
    extrude_spoke_outline(z=-0.02)

    glPopMatrix()

    # -------- PNEU --------
    glPushMatrix()
    glColor3f(*color_tire)
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (*color_tire, 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (*color_tire, 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (*color_tire, 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, 0)

    glTranslatef(0.0, 0.0, inner * 0.5)
    glutSolidTorus(inner - 0.2, base, 32, 64)
    glPopMatrix()

    glPopMatrix()
    gluDeleteQuadric(quadric)