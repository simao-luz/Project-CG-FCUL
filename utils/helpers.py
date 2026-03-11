"""
Módulo de apoio à aplicação.
Desenvolvido por:
    - Diogo Vasconcelos, fc61809
    - Miguel Guise, fc61822
    - Simão da Luz, fc61816
Em: 01/12/2026
"""

import math
import sys, os
from PIL import Image
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np


def arc_points(cx, cy, r, a0, a1, n):
    """
    Calcula um conjunto de n pontos igualmente espaçados ao longo de um arco.

    O arco é definido entre os ângulos a0 e a1, com centro em (cx, cy)
    e raio r. Os n pontos resultantes encontram-se distribuídos de forma uniforme
    ao longo do arco, desde a0 até a1.
    - cx: coordenada x do centro do arco.
    - cy: coordenada y do centro do arco.
    - r:  raio do arco.
    - a0: ângulo inicial, em graus.
    - a1: ângulo final, em graus.
    - n:  número de pontos a gerar.
    """
    a0 = math.radians(a0)
    a1 = math.radians(a1)
    out = []
    for i in range(n):
        t = i / (n - 1)
        ang = a0 + (a1 - a0) * t
        out.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))

    return out

def centroid_2d(poly):
    """
    Calcula o centróide de um polígono 2D.

    - poly: lista de pontos 2D no formato (x, y).
    """
    n = len(poly)
    return (sum(p[0] for p in poly) / n, sum(p[1] for p in poly) / n)

def round_outline(poly, corners, r, segments=10, concave=False):
    """
    Função responsável pelo arredondamento de vértices específicos 
    de um polígono CONVEXO 2D.
    - poly:     lista de pontos 2D, (x, y)
    - corners:  lista de vértices a serem arredondados
    - r:        raio do arco para a suavização 
    - segments: número de segmentos/sides utilizados na construção do arredondamento
    - concave:  queremos o arredondamento do vértice como concâvo?
    """
    n = len(poly)
    out = []
    for i in range(n):
        if i not in corners:
            out.append(poly[i]); continue

        # Três vértices: corner = 2 arestas que se encontram num vértice!
        p0 = poly[(i - 1) % n] 
        p1 = poly[i] 
        p2 = poly[(i + 1) % n]
        v1 = (p1[0] - p0[0], p1[1] - p0[1])
        v2 = (p2[0] - p1[0], p2[1] - p1[1])

        L1 = math.hypot(*v1)
        L2 = math.hypot(*v2)

        # Vetores normalizados
        d1 = (v1[0] / L1, v1[1] / L1)
        d2 = (v2[0] / L2, v2[1] / L2)

        dot = np.dot((-d1[0], -d1[1]), (d2[0], d2[1]))
        phi = math.acos(dot) 

        t = r / math.tan(phi/2.0)
        A = (p1[0] - d1[0] * t, p1[1] - d1[1] * t) # Vetor deslocação -> vetor + ponto = ponto
        B = (p1[0] + d2[0] * t, p1[1] + d2[1] * t)

        bx, by = (-d1[0] + d2[0], -d1[1] + d2[1]) # -d1 + d2 = bissetriz
        bl = math.hypot(bx, by)
        bx, by = bx / bl, by / bl # Normalizar vetor da bissetriz
        h = r / math.sin(phi / 2.0)

        if concave:
            bx, by = -bx, -by # para ser concâvo inverte-se direção do vetor bissetriz (C vai para "fora")

        C = (p1[0] + bx * h, p1[1] + by * h)

        angle_CA = math.atan2(A[1] - C[1], A[0] - C[0])
        angle_CB = math.atan2(B[1] - C[1], B[0] - C[0])

        cross = d1[0] * d2[1] - d1[1] * d2[0] # det vetorial

        if concave:
            cross = -cross

        if cross > 0:  # Se maior que 0 está CCW
            if angle_CB < angle_CA: angle_CB += 2 * math.pi
            pts = arc_points(C[0], C[1], r, math.degrees(angle_CA), math.degrees(angle_CB), segments)

        else: # Se não, está CW
            if angle_CA < angle_CB: angle_CA += 2 * math.pi
            pts = arc_points(C[0], C[1], r, math.degrees(angle_CA), math.degrees(angle_CB), segments)

        out.extend(pts); 
    return out

def bounding_box_for_texture(outline):
    """
    Função que recebe uma outline e cria uma bounding box 2D para
    mapear a textura (importante para o cálculo de u e v de cada vértice)!

    - outline: lista de pontos 2D.
    """
    all_x = [p[0] for p in outline]
    all_y = [p[1] for p in outline]

    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)

    dx = max_x - min_x
    dy = max_y - min_y

    return min_x, min_y, dx, dy

def draw_textured_cap(outline, z, tex_id,
                      tile_u=1.0, tile_v=1.0,
                      mode=GL_QUADS,
                      z_normal=1.0,
                      flip_winding=False,
                      color=(1.0, 1.0, 1.0)):
    """
    Desenha uma tampa texturada.
    - outline:      conjunto de vértices a aplicar a textura
    - z:            coordenada z onde a tampa será desenhada
    - tex_id:       id da textura a aplicar
    - tile_u:       fator de repetição nos x da textura
    - tile_v:       fator de repetição nos y da textura
    - mode: GL_QUADS ou GL_TRIANGLES
    - z_normal:     orientação da normal
    - flip_winding: se True inverte ordem dos vértices (cw em vez de ccw)
                    importante quando faces ficam ao contrário (principalmente,
                    após o uso de glScalef.
    - color:        cor a aplicar à textura
    """
    min_x, min_y, dx, dy = bounding_box_for_texture(outline)

    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glColor3f(*color)

    glNormal3f(0.0, 0.0, z_normal)
    pts = list(reversed(outline)) if flip_winding else outline

    if mode == GL_QUADS:
        glBegin(GL_QUADS)
        for (px, py) in pts:
            u = ((px - min_x) / dx) * tile_u
            v = ((py - min_y) / dy) * tile_v
            glTexCoord2f(u, v)
            glVertex3f(px, py, z)
        glEnd()

    elif mode == GL_TRIANGLES:
        p0 = pts[0]

        glBegin(GL_TRIANGLES)
        for i in range(1, len(pts) - 1):
            p1 = pts[i]
            p2 = pts[i + 1]

            for (px, py) in (p0, p1, p2):
                u = ((px - min_x) / dx) * tile_u
                v = ((py - min_y) / dy) * tile_v
                glTexCoord2f(u, v)
                glVertex3f(px, py, z)
        glEnd()

    glDisable(GL_TEXTURE_2D)

def extrude_outline(outline, z_center, 
                    thick_front, thick_back,
                    color_front=(1.0, 1.0, 1.0), color_back=(1.0, 1.0, 1.0), color_side=(1.0, 1.0, 1.0), alpha=1.0,
                    caps=True, closed=True, skip_sides=None,
                    tex_front=None, tex_back=None, tex_side=None,
                    tile_u_front=1.0, tile_v_front=1.0, 
                    tile_u_back=1.0, tile_v_back=1.0,
                    tile_u_side=1.0, tile_v_side=1.0):
    """
    Função principal do programa - É esta função que vai permitir dar
    profundidade a um conjunto de pontos definidos pelo utilizador, bem como,
    definir a cor da frente do poliedro, de trás e dos lados. Esta função permite também
    definir se se pretende fechar ou não a frente e trás do poliedro, que lados deste devem
    ficar abertos e se o último side é fechado ou não. Por fim, permite adicionar uma textura
    para a frente, trás e lados que podem ser diferentes de conteúdo e em bounding!
    - outline:     lista de pontos 2D a extrudir
    - z_center:    coordenada z onde ocorrerá a extrusão
    - thick_front: a profundidade em direção ao z+
    - thick_back:  a profundidade em direção a z-
    - color_front: cor para o lado frontal  (definido por z+)
    - color_back:  cor para o lado traseiro (definido por z-)
    - color_side:  cor para todos os restantes lados
    - alpha:       transparência da cor
    - caps:        quer-se a parte frontal e traseira abertas?
    - closed:      quer-se o side final fechado?
    - skip_side:   conjunto de sides a não fechar
    - tex_front:   textura a aplicar ao lado frontal
    - tex_back:    textura a aplicar ao lado traseiro
    - tex_side:    textura a aplicar aos restantes lados
    - tile_u_*:    fator de repetição nos x da textura
    - tile_v_*:    fator de repetição nos y da textura
    """
    zf = z_center + thick_front
    zb = z_center - thick_back

    cx, cy = centroid_2d(outline)
    n = len(outline)

    # Se vamos utilizar todos os sides, então skip_sides=None;
    if skip_sides is None:
        skip_sides = set()

    # -------- CAPS (FRENTE E ATRÁS) --------
    # Queremos caps?
    if caps:

        # - FRENTE -
        # Queremos texture e a outline representa um polígono de 4 lados
        if tex_front is not None and len(outline) == 4:
            draw_textured_cap(outline, zf, tex_front, 
                              tile_u_front, tile_v_front,
                              GL_QUADS,
                              color=color_front) 
        
        elif tex_front is not None:
            draw_textured_cap(outline, zf, tex_front, 
                              tile_u_front, tile_v_front,
                              GL_TRIANGLES,
                              color=color_front)

        # Não há textura na front!
        else:
            glColor4f(color_front[0], color_front[1], color_front[2], alpha)
            glNormal3f(0.0, 0.0, 1.0)

            glBegin(GL_TRIANGLE_FAN)
            glVertex3f(cx, cy, zf)
            for (px, py) in outline:
                glVertex3f(px, py, zf)
            glVertex3f(outline[0][0], outline[0][1], zf)
            glEnd()

        # - ATRÁS -
        if tex_back is not None and len(outline) == 4:
            draw_textured_cap(outline, zb, tex_back,
                              tile_u_back, tile_v_back,
                              GL_QUADS, z_normal=-1.0, flip_winding=True,
                              color=color_back)


        elif tex_back is not None:
            draw_textured_cap(outline, zb, tex_back,
                              tile_u_back, tile_v_back,
                              GL_TRIANGLES, z_normal=-1.0, flip_winding=True,
                              color=color_back)
            
        else:
            glColor4f(color_back[0], color_back[1], color_back[2], alpha)
            glNormal3f(0.0, 0.0, -1.0)

            glBegin(GL_TRIANGLE_FAN)
            glVertex3f(cx, cy, zb)
            for (px, py) in reversed(outline):
                glVertex3f(px, py, zb)
            glVertex3f(outline[-1][0], outline[-1][1], zb)
            glEnd()

    # -------- LADOS (COM ou SEM textura) --------
    if tex_side is not None:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tex_side)
        glColor4f(*color_side, alpha)
    else:
        glColor4f(color_side[0], color_side[1], color_side[2], alpha)

    glBegin(GL_QUADS)

    limit = n if closed else n - 1
    for i in range(limit):
        if i in skip_sides:
            continue

        x1, y1 = outline[i]
        if closed:
            x2, y2 = outline[(i + 1) % n]
        else:
            x2, y2 = outline[i + 1]

        ex = x2 - x1
        ey = y2 - y1
        L = math.hypot(ex, ey)
        if L < 1e-4:
            continue

        nx = ey / L
        ny = -ex / L
        glNormal3f(nx, ny, 0.0)

        if tex_side is not None:
            glTexCoord2f(0.0, tile_v_side)
            glVertex3f(x1, y1, zf)

            glTexCoord2f(0.0, 0.0)
            glVertex3f(x1, y1, zb)

            glTexCoord2f(tile_u_side, 0.0)
            glVertex3f(x2, y2, zb)

            glTexCoord2f(tile_u_side, tile_v_side)
            glVertex3f(x2, y2, zf)

        else:
            glVertex3f(x1, y1, zf)
            glVertex3f(x1, y1, zb)
            glVertex3f(x2, y2, zb)
            glVertex3f(x2, y2, zf)

    glEnd()

    # Impedir que propague para restantes objetos vindouros
    if tex_side is not None:
        glDisable(GL_TEXTURE_2D)

def build_box_outline(width=1.0, height=1.0, r=None, corners=None, arc_segments=10):
    """
    Função que cria a outline de uma caixa.
    - width: largura da caixa
    - height: altura da caixa
    - r: arredondamento dos cantos
    - corners: cantos arredondados 
    - arc_segments: número de segmentos do arredondamento
    """
    if corners is None:
        corners = []   # sem arredondar por default

    x0, y0 = 0.0, 0.0
    x1, y1 = x0 + width, y0 + height

    base_poly = [(x0, y1), (x0, y0), (x1, y0), (x1, y1)] # ccw

    if r is None:
        r = 0.5 * min(width, height)

    if corners:
        rounded = round_outline(base_poly, corners, r, arc_segments)
    else:
        rounded = base_poly

    return rounded

def draw_box(width=1.0,
             height=1.0,
             depth=1.0,
             r=None,
             corners=None,
             color_front=(0.0, 0.0, 0.0),
             color_back=(0.0, 0.0, 0.0),
             color_side=(0.0, 0.0, 0.0),
             alpha=1.0,
             caps=True,
             tex_f=None,
             tex_b=None,
             tex_s=None,
             tile_u_front=1.0, tile_v_front=1.0, 
             tile_u_back=1.0, tile_v_back=1.0,
             tile_u_side=1.0, tile_v_side=1.0):
    """
    Função que cria uma caixa com build_box_outline e extrude_outline.
    Para informação sobre os primeiros 4 argumentos consultar build_box_outline e o resto extrude_outline.
    """
    outline = build_box_outline(width, height, r, corners)

    extrude_outline(outline,
                    z_center=0.0,
                    thick_front=0.0,
                    thick_back=depth,
                    color_front=color_front,
                    color_back=color_back,
                    color_side=color_side,
                    alpha=alpha,
                    caps=caps,
                    closed=True,
                    tex_front=tex_f,
                    tex_back=tex_b,
                    tex_side=tex_s,
                    tile_u_front=tile_u_front, tile_v_front=tile_v_front, 
                    tile_u_back=tile_u_back, tile_v_back=tile_v_back,
                    tile_u_side=tile_u_side, tile_v_side=tile_v_side)

def ensure_ccw(poly):
    """
    Garante que o polígono 'poly' (lista de (x, y)) está em CCW
    quando visto de +Z. Se estiver em CW inverte a ordem!!
    """
    det_sum = 0.0
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        det_sum += x1 * y2 - x2 * y1

    if det_sum < 0.0:
        poly = list(reversed(poly))
    return poly

def build_round_outline_for_corner(width=2.0, height=2.0, r=1.0, corner=0, dx=2.0):
    """
    Função que constrói a outline necessária para gerar uma extrusão arredondada num dos
    cantos de uma BOX ! A função produz dois conjuntos de pontos: a região
    interior arredondada e a região exterior deslocada que juntas fazem uma outline completa.

    O canto a arredondar é especificado por 'corner' (0 a 3).

    - width: largura da box base
    - height: altura da box base
    - r: raio do arredondamento
    - corner: índice do canto a suavizar
    - dx: deslocamento horizontal aplicado à parte exterior (outer) da outline !!
    """

    box_outline = build_box_outline(width, height, r, corners=[corner])

    if corner == 0:
        cx, cy = r, height - r
        def inside(x, y): return x < cx and y > cy

    elif corner == 1:
        cx, cy = width - r, height - r
        def inside(x, y): return x > cx and y > cy

    elif corner == 2:
        cx, cy = width - r, r
        def inside(x, y): return x > cx and y < cy

    elif corner == 3:
        cx, cy = r, r
        def inside(x, y): return x < cx and y < cy

    inner = []
    for x, y in box_outline:
        if inside(x, y):
            inner.append((x - cx, y - cy))   # shift para perto do (0,0)

    # ordenar por y (de baixo para cima)
    inner.sort(key=lambda p: p[1])

    outer = [(x + dx, y) for (x, y) in inner]

    outline = inner + list(reversed(outer))

    outline = ensure_ccw(outline)

    n_inner = len(inner)
    n_total = len(outline)

    # índices dos sides a saltar
    skip_sides = set()
    skip_sides.update(range(0, n_inner - 1))
    skip_sides.update(range(n_inner, n_total - 1))

    return outline, skip_sides


def draw_rounded_panel(width=1.0, 
                       height=1.0,
                       depth=1.0,
                       r=None, 
                       corner=0, 
                       dx=1.0,
                       color_front=(0.0, 0.0, 0.0),
                       color_back=(0.0, 0.0, 0.0),
                       color_side=(0.0, 0.0, 0.0),
                       caps=True,
                       closed=True):
    """
    Desenha um painel 3D extrudido com um canto arredondado.

    A outline arredondada é construída por build_round_outline_for_corner
    e extrudida por extrude_outline.
    """
    if r is None:
        r = min(width, height) * 0.5

    outline, _ = build_round_outline_for_corner(width=width, height=height, r=r, corner=corner, dx=dx)
    glFrontFace(GL_CW)
    extrude_outline(outline,
                    z_center=0.0,
                    thick_front=0.0,
                    thick_back=depth,
                    color_front=color_front,
                    color_back=color_back,
                    color_side=color_side,
                    caps=caps,
                    closed=closed)
    glFrontFace(GL_CCW)


def draw_quarter_closed_cylinder(base, top, height, color=(0.0, 0.0, 0.0)):
    """
    Função que devolve um quarto de um cilindro fechado
    - base:   tamanho da base
    - top:    tamanho do topo
    - height: altura do cilindro
    - color:  cor do cilindro
    """
    plane_x = (1.0, 0.0, 0.0, 0.0)
    plane_y = (0.0, -1.0, 0.0, 0.0)

    glClipPlane(GL_CLIP_PLANE0, plane_x)
    glEnable(GL_CLIP_PLANE0)

    glClipPlane(GL_CLIP_PLANE1, plane_y)
    glEnable(GL_CLIP_PLANE1)

    # desenhar cilindro normalmente
    draw_closed_cylinder(base, top, height, color)

    glDisable(GL_CLIP_PLANE0)
    glDisable(GL_CLIP_PLANE1)

def set_normal(v1, v2, v3):
    """
    Calcula a normal a partir de 3 pontos em CCW
    e faz o glNormal3f() nessa direção.
    """
    u = v2 - v1
    v = v3 - v1
    n = np.cross(u, v)
    length = np.linalg.norm(n)

    n = n / length
    glNormal3f(n[0], n[1], n[2])

    return n

def load_texture(path, repeat=True):
    """
    Função fornecida pelos professores
    """
    if not os.path.isfile(path):
        print("Texture not found:", path); sys.exit(1)

    img = Image.open(path).convert("RGBA")
    w, h = img.size
    data = img.tobytes("raw", "RGBA", 0, -1)

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)

    # filtros  e  mipmaps
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT if repeat else GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT if repeat else GL_CLAMP_TO_EDGE)

    # Criação de mipmaps com o GLU
    gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, w, h, GL_RGBA, GL_UNSIGNED_BYTE, data)

    #devolve o ID de cada textura carregada que será usado quando os objectos forem desenhados
    return tex_id

quadric = None
def init_quadrics():
    """
    Função que inicializa quadric !
    """
    global quadric

    quadric = gluNewQuadric()
    gluQuadricNormals(quadric, GLU_SMOOTH)
    gluQuadricTexture(quadric, GL_FALSE)

def draw_closed_cylinder(base, top, height, 
                         color=(0.0, 0.0, 0.0), 
                         base_on=True, top_on=True, 
                         slices=32, stacks=1):
    """
    Função que cria um cilindro fechado
    - base: tamanho da base
    - top: tamanho do topo
    - height: altura do cilindro
    - color: cor do cilindro
    - base_on: parametro que decide se desenha a base
    - top_on: parametro que decide se desenha o topo
    - slices: número de subdivisões à volta do eixo z
    - stacks: número de subdivisões ao longo do eixo z
    """
    global quadric 

    glColor3f(*color)
    glPushMatrix()
    gluCylinder(quadric, base, top, height, slices, stacks)
    glPopMatrix()

    if base_on:
        glPushMatrix()
        glRotate(180, 1, 0, 0)
        gluDisk(quadric, 0.0, base, slices, 1)
        glPopMatrix()

    if top_on:
        glPushMatrix()
        glTranslatef(0.0, 0.0, height)
        gluDisk(quadric, 0.0, top, slices, 1)
        glPopMatrix()

def del_quadrics():
    """
    Função que apaga quadric !
    """
    global quadric

    gluDeleteQuadric(quadric)
