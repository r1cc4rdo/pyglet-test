"""
glPolygonMode( GL_FRONT_AND_BACK, GL_LINE );
...
glPolygonMode( GL_FRONT_AND_BACK, GL_FILL );

[0, 1, 2, 4]
[0, 1, 4, 7]
[0, 2, 3, 4]
[1, 2, 4, 5]
[1, 4, 7, 5]
[1, 6, 5, 7]
"""

import numpy as np

template = [[1, 3, 2], [0, 2, 3], [0, 3, 1], [0, 1, 2]]  # template[k] is missing vertex k
tetras = [[0, 1, 2, 4], [0, 1, 4, 7], [0, 2, 3, 4], [1, 2, 4, 5], [1, 4, 7, 5], [1, 6, 5, 7]]


def make_cube(origin, side):
    (ox, oy, oz), s = origin, side
    return np.array([[x * (-1 if iz % 2 else 1), y * (-1 if ix % 2 else 1), z]
                     for iz, z in enumerate([oz, oz+s]) for ix, x in enumerate([ox, ox+s]) for y in [oy, oy+s]])


def surface_from_tetra(vertexes, values, threshold):

    outside = [index for index, val in enumerate(values) if val > threshold]
    inside = list(set(range(4)) - set(outside))

    if len(outside) in (0, 4):  # nothing to do, the isosurface does not intersect the tetra
        return []

    def interp(i, j):
        t = (threshold - values[i]) / (values[j] - values[i])
        return t * vertexes[i] + (1 - t) * vertexes[j]

    if len(outside) in (1, 3):  # the isosurface split vertexes in a 3/1 fashion, output a single triangle

        base_is_out = len(outside) == 3
        top_index = inside[0] if base_is_out else outside[0]
        base_indexes = template[top_index] if base_is_out else template[top_index][::-1]
        return [interp(top_index, base_index) for base_index in base_indexes]

    #  if here, count == 2. Split is 2/2, need to output two triangles

    indexes = template[outside[0]]
    while indexes[1] != outside[1]:
        indexes = indexes[1:] + [indexes[0]]
    indexes = indexes + [outside[0]]

    quad = [interp(sidx, eidx) for sidx, eidx in zip(indexes, indexes[1:] + [indexes[0]])]
    return [quad[idx] for idx in (0, 2, 1, 0, 3, 2)]  # triangles


def surface_from_cube(origin, side, values, threshold):

    verts = make_cube(origin, side)
    triangles = []
    for tetra in tetras:
        triangles.extend(surface_from_tetra(verts[tetra], [values[index] for index in tetra], threshold))
    return triangles


# --- Pyglet code below --- --- --- --- ---

import pyglet

# pyglet.options['debug_gl'] = False  # Disable error checking for increased performance

from pyglet.gl import *
from pyglet.window import key

window = pyglet.window.Window(resizable=True)


@window.event
def on_resize(width, height):

    rfix = 2  # mac OSX retina fix. Should be addressed by pyglet v1.4+
    glViewport(0, 0, width * rfix, height * rfix)
    window.aspect = width / float(height)
    return pyglet.event.EVENT_HANDLED


def enter_draw_2D():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, window.width * 2, 0, window.height * 2, -1, 1)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def enter_draw_3D():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(50., window.aspect, .1, 1000.)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0, 0, -3)
    glRotatef(window.rz, 0, 0, 1)
    glRotatef(window.ry, 0, 1, 0)
    glRotatef(window.rx, 1, 0, 0)


def draw_tetras(origin, side):

    verts = make_cube(origin, side)
    flat_verts = [v for xyz in verts for v in xyz]
    inflated_tetras = [[tetra[i] for triangle in template for i in triangle] for tetra in tetras]
    for index, should_draw in enumerate(window.flags):
        if should_draw:
            pyglet.graphics.draw_indexed(8, pyglet.gl.GL_TRIANGLES, inflated_tetras[index], ('v3f', flat_verts),
                                         ('c3f', [x for io in window.inout for x in ((1, 0, 0) if io else (0, 0, 0))]))


def draw_wireframe_cube(origin, side):

    verts = make_cube(origin, side)
    faces3 = [[0, 1, 2, 3], [0, 1, 6, 7], [0, 3, 4, 7]]
    indexes = [(i,j) for face3 in faces3 for face in [face3, list(set(range(8)) - set(face3))] for i, j in zip(face, face[1:] + [face[0]])]
    flattened_coords = [xyz for i, j in indexes for vert in [verts[i], verts[j]] for xyz in vert]
    pyglet.graphics.draw(len(flattened_coords) // 3, pyglet.gl.GL_LINES, ('v3f', flattened_coords), ('c3f', np.zeros_like(flattened_coords)))


def test_triangle():

    pyglet.gl.glColor4f(1,1,1,1)
    coords = [0.8,0.7,0.7,0.7,0.8,0.7,0.7,0.7,0.8]
    pyglet.graphics.draw(3, pyglet.gl.GL_TRIANGLES, ('v3f', coords), ('c3f', [1,0,0,0,1,0,0,0,1]))
    pyglet.graphics.draw(3, pyglet.gl.GL_TRIANGLES, ('v3f', coords[::-1]), ('c3f', [1,0,0,0,1,0,0,0,1]))


@window.event
def on_draw():

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    enter_draw_3D()

    oos3 = 1 / np.sqrt(3)
    draw_tetras((-oos3,) * 3, 2 * oos3)
    draw_wireframe_cube((-oos3,) * 3, 2 * oos3)
    tris = surface_from_cube((-oos3,) * 3, 2 * oos3, [float(io) for io in window.inout], 0.5)
    pyglet.graphics.draw(len(tris), pyglet.gl.GL_TRIANGLES, ('v3f', [v for xyz in tris for v in xyz]), ('c3f', [0, 1, 0] * len(tris)))
    pyglet.graphics.draw(len(tris), pyglet.gl.GL_TRIANGLES, ('v3f', [v for xyz in tris[::-1] for v in xyz]), ('c3f', [0, 0, 0] * len(tris)))


@window.event
def on_key_press(symbol, modifiers):

    numbers = (key._1, key._2, key._3, key._4, key._5, key._6)
    if symbol in numbers:
        index = numbers.index(symbol)
        window.flags[index] ^= True

    qwerasdf = (key.Q, key.W, key.E, key.R, key.A, key.S, key.D, key.F)
    if symbol in qwerasdf:
        index = qwerasdf.index(symbol)
        window.inout[index] ^= True


def update(dt):

    if window.rotate:
        window.rx, window.ry, window.rz = ((angle + dt * speed) % 360
                                           for angle, speed in zip((window.rx, window.ry, window.rz), (1, 80, 30)))


def init():

    glClearColor(1, 1, 1, 1)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)

    window.rotate = True
    window.rx = window.ry = window.rz = 0
    window.flags = [True] * 6
    window.inout = [True] * 8
    window.wireframe = False

    pyglet.clock.schedule(update)


init()
pyglet.app.run()
