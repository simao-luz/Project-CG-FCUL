"""
Módulo de construção das partes pertencentes ao capô de um veículo !
Desenvolvido por:
    - Diogo Vasconcelos, fc61809
    - Miguel Guise, fc61822
    - Simão da Luz, fc61816
Em: 01/12/2026
"""

from utils.helpers import *
from utils.variables import *

# Definição de todos os pontos à construção do capô 
v0 = np.array([0.0, 0.0, 0.0])
v1 = np.array([0.0, 0.0, HOOD_MAIN_DEPTH])
v2 = np.array([HOOD_SIDE_WIDTH, HOOD_SIDE_HEIGHT, HOOD_MAIN_DEPTH])
v3 = np.array([HOOD_SIDE_WIDTH, 0.0, HOOD_MAIN_DEPTH + HOOD_SIDE_WIDTH])
v4 = np.array([HOOD_SIDE_WIDTH + HOOD_MAIN_WIDTH, 0.0, HOOD_MAIN_DEPTH + HOOD_SIDE_WIDTH])
v5 = np.array([HOOD_SIDE_WIDTH + HOOD_MAIN_WIDTH, HOOD_SIDE_HEIGHT, HOOD_MAIN_DEPTH])
v6 = np.array([HOOD_SIDE_WIDTH * 2 + HOOD_MAIN_WIDTH, 0.0, HOOD_MAIN_DEPTH])
v7 = np.array([HOOD_SIDE_WIDTH * 2 + HOOD_MAIN_WIDTH, 0.0, 0.0])
v8 = np.array([HOOD_SIDE_WIDTH + HOOD_MAIN_WIDTH, HOOD_SIDE_HEIGHT + HOOD_MAIN_HEIGHT, 0.0])
v9 = np.array([HOOD_SIDE_WIDTH, HOOD_SIDE_HEIGHT + HOOD_MAIN_HEIGHT, 0.0])


def draw_hood(color_tex=(0.2, 0.2, 0.2), color_others=(0.0, 0.0, 0.0), color_rad=(0.4, 0.4, 0.4), tex_hood=None, tex_rad=None):
    """
    Função responsável pela construção de um capô.
    - color: cor a aplicar ao capô
    - tex:   textura a aplicar ao capô (condiciona 'color' em algumas áreas)
    """
    # -------- HOOD MAIN --------
    if tex_hood is not None:
        glColor3f(*color_tex)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tex_hood)
    else:
        glColor3f(*color_tex)  # Se não há textura, deixa a cor original passada como arg

    # - QUADRADO PRINCIPAL DO HOOD + HOOD NOS SIDES (ESQ, DIR e FRENTE) -
    glBegin(GL_TRIANGLES)
    
    # O set_normal será uma função recorrente a ser chamada nesta função;
    # Por conta de algumas superfícies serem inclinadas é necessário
    # calcular corretamente a normal destas, através do produto vetorial
    # de dois vetores definidos pelos vértices (vi, vj, vk)
    set_normal(v0, v1, v9) 
    glTexCoord2f(0.0, 0.0); glVertex3f(*v0)
    glTexCoord2f(0.0, 1.0); glVertex3f(*v1)
    glTexCoord2f(1.0, 1.0); glVertex3f(*v9)

    set_normal(v1, v2, v9)
    glTexCoord2f(0.0, 0.0); glVertex3f(*v1)
    glTexCoord2f(0.0, 1.0); glVertex3f(*v2)
    glTexCoord2f(1.0, 1.0); glVertex3f(*v9)

    set_normal(v8, v5, v6)
    glTexCoord2f(0.0, 0.0); glVertex3f(*v8)
    glTexCoord2f(0.0, 1.0); glVertex3f(*v5)
    glTexCoord2f(1.0, 1.0); glVertex3f(*v6)

    set_normal(v8, v6, v7)
    glTexCoord2f(0.0, 0.0); glVertex3f(*v8)
    glTexCoord2f(0.0, 1.0); glVertex3f(*v6)
    glTexCoord2f(1.0, 1.0); glVertex3f(*v7)

    set_normal(v9, v2, v5)
    glTexCoord2f(0.0, 0.0); glVertex3f(*v9)
    glTexCoord2f(0.0, 1.0); glVertex3f(*v2)
    glTexCoord2f(1.0, 1.0); glVertex3f(*v5)

    set_normal(v9, v5, v8)
    glTexCoord2f(0.0, 0.0); glVertex3f(*v9)
    glTexCoord2f(0.0, 1.0); glVertex3f(*v5)
    glTexCoord2f(1.0, 1.0); glVertex3f(*v8)
    glEnd()

    # Não queremos textura na parte frontal do capô principal, 
    # nem nos cilindros e nem no radiador !
    if tex_hood is not None:
        glDisable(GL_TEXTURE_2D) 
    
    # - PARTE FRONTAL AO QUADRADO PRINCIPAL DO HOOD -
    glBegin(GL_TRIANGLES)
    glColor3f(*color_others)
    
    set_normal(v2, v3, v4)
    glVertex3f(*v2)
    glVertex3f(*v3)
    glVertex3f(*v4)

    set_normal(v2, v4, v5)
    glVertex3f(*v2)
    glVertex3f(*v4)
    glVertex3f(*v5)
    glEnd()

    # -------- 1/4 DE CONES (LUGAR DOS FARÓIS) --------
    # - SIDE 1 -
    glPushMatrix()
    glTranslatef(v5[0], v5[1] - HOOD_SIDE_HEIGHT, v5[2])
    glRotatef(-90, 1.0, 0.0, 0.0)
    draw_quarter_closed_cylinder(HOOD_SIDE_WIDTH, 
                                 0.0, 
                                 HOOD_SIDE_HEIGHT, 
                                 color_others)
    glPopMatrix()

    # - SIDE 2 -
    glPushMatrix()
    glTranslatef(v2[0], v2[1] - HOOD_SIDE_HEIGHT, v2[2])
    glRotatef(-90, 1.0, 0.0, 0.0)
    glRotatef(-90, 0.0, 0.0, 1.0)
    draw_quarter_closed_cylinder(HOOD_SIDE_WIDTH, 
                                 0.0, 
                                 HOOD_SIDE_HEIGHT, 
                                 color_others)
    glPopMatrix()
    
    # Reativar textura para as laterais do capô !
    if tex_hood is not None:
        glColor3f(*color_tex)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tex_hood)
    else:
        glColor3f(*color_tex)
        
    # -------- LATERAIS DO CAPÔ --------

    # Estas variáveis são as variáveis, v0, v1, v6 e v7
    # decrementadas em HOOD_LAT_HEIGHT em y
    v0l = (v0[0], v0[1] - HOOD_LAT_HEIGHT, v0[2])
    v1l = (v1[0], v1[1] - HOOD_LAT_HEIGHT, v1[2])
    v6l = (v6[0], v6[1] - HOOD_LAT_HEIGHT, v6[2])
    v7l = (v7[0], v7[1] - HOOD_LAT_HEIGHT, v7[2])

    glBegin(GL_TRIANGLES)
    # - SIDE 1 -
    set_normal(v6, v6l, v7l)
    glTexCoord2f(0.0, 0.0); glVertex3f(*v6)
    glTexCoord2f(0.0, 1.0); glVertex3f(*v6l)
    glTexCoord2f(1.0, 1.0); glVertex3f(*v7l)

    set_normal(v6, v7l, v7)
    glTexCoord2f(0.0, 0.0); glVertex3f(*v6)
    glTexCoord2f(0.0, 1.0); glVertex3f(*v7l)
    glTexCoord2f(1.0, 1.0); glVertex3f(*v7)

    # - SIDE 2 -
    set_normal(v0, v0l, v1l)
    glTexCoord2f(0.0, 0.0); glVertex3f(*v0)
    glTexCoord2f(0.0, 1.0); glVertex3f(*v0l)
    glTexCoord2f(1.0, 1.0); glVertex3f(*v1l)

    set_normal(v0, v1l, v1)
    glTexCoord2f(0.0, 0.0); glVertex3f(*v0)
    glTexCoord2f(0.0, 1.0); glVertex3f(*v1l)
    glTexCoord2f(1.0, 1.0); glVertex3f(*v1)

    glEnd()

    # Voltar a desabilitar (agora para 'defender' os cilindros & radiador)
    if tex_hood is not None:
        glDisable(GL_TEXTURE_2D)

    # -------- CILINDROS DO CAPÔ --------
    # - SIDE 1 -
    glPushMatrix()
    glTranslatef(v5[0], v5[1] - HOOD_SIDE_HEIGHT - HOOD_LAT_HEIGHT, v5[2])
    glRotatef(-90, 1.0, 0.0, 0.0)
    draw_quarter_closed_cylinder(HOOD_SIDE_WIDTH, 
                                 HOOD_SIDE_WIDTH, 
                                 HOOD_LAT_HEIGHT,
                                 color_others)
    glPopMatrix()

    # - SIDE 2 -
    glPushMatrix()
    glTranslatef(v2[0], v2[1] - HOOD_SIDE_HEIGHT - HOOD_LAT_HEIGHT, v2[2])
    glRotatef(-90, 1.0, 0.0, 0.0)
    glRotatef(-90, 0.0, 0.0, 1.0) # z como novo y
    draw_quarter_closed_cylinder(HOOD_SIDE_WIDTH, 
                                 HOOD_SIDE_WIDTH, 
                                 HOOD_LAT_HEIGHT,
                                 color_others)
    glPopMatrix()

    # -------- RADIADOR DO CAPÔ --------
    if tex_rad is not None:
        glColor3f(*color_rad)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tex_rad)
    else:
        glColor3f(*color_rad)

    v3l = (v3[0],  v3[1] - HOOD_LAT_HEIGHT, v3[2])
    v4l = (v4[0],  v4[1] - HOOD_LAT_HEIGHT, v4[2])

    glBegin(GL_QUADS)

    set_normal(v3, v3l, v4l)
    glTexCoord2f(0.0, 0.0); glVertex3f(*v3)
    glTexCoord2f(0.0, 1.0); glVertex3f(*v3l)
    glTexCoord2f(1.0, 1.0); glVertex3f(*v4l)
    glTexCoord2f(1.0, 0.0); glVertex3f(*v4)

    glEnd()

    if tex_rad is not None:
        glDisable(GL_TEXTURE_2D)


def draw_headlight(pos, light_id=None):
    """
    Função responsável pela construção do farol de um veículo.
    - pos: posição onde será inserido o farol
    """ 
    quadric = gluNewQuadric()
    base = 0.05
    headlight_size = 0.25

    glPushMatrix()
    glTranslatef(pos[0], pos[1] + 0.2, pos[2]) # Leva a origem até à base do farol
    glRotatef(90.0, 1.0, 0.0, 0.0)

    # Troço cilíndrico de ligação do capô às luzes 
    draw_closed_cylinder(base, base, height=0.3,
                         color=(0.2, 0.2, 0.2))
    glPushMatrix()

    glRotatef(-90.0, 0.0, 0.0, 1.0) # Restabelece sistema de orientação
    glTranslatef(-0.20, 0.0, 0.0)
    glRotatef(90, 0.0, 1, 0.0)
    
    # Construção do farol
    draw_closed_cylinder(base=headlight_size, top=0.0, height=0.25,
                         color=(0.2, 0.2, 0.2), 
                         base_on=False) # Sem base para colocar disco emissor

    # Material emissor AMARELO !
    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (1.0, 1.0, 0.0, 1.0))
    glRotatef(180, 1, 0, 0)
    gluDisk(quadric, 0.0, headlight_size, 32, 1) 

    # Resetar a emissão para preto (zero) !!
    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (0.0, 0.0, 0.0, 1.0))

    # Definir posição da Luz (light_id)
    if light_id is not None:
        glLightfv(light_id, GL_POSITION, (0.0, 0.0, 0.0, 1.0))
        glLightfv(light_id, GL_SPOT_DIRECTION, (0.0, 0.0, 1.0))

    glPopMatrix()
    glPopMatrix()

    gluDeleteQuadric(quadric)
