import numpy as np

solids = {
    "tetrahedron": {
        "values": [1 / np.sqrt(2)],
        "iverts": [[-1, 0, -2], [1, 0, -2], [0, -1, 2], [0, 1, 2]],
        "faces": [[0, 1, 2], [0, 2, 3], [0, 3, 1], [1, 3, 2]]},
    "hexahedron": {  # aka a cube ;)
        "values": [],
        "iverts": [[-1, -1, -1], [-1, -1, 1], [-1, 1, -1], [1, -1, -1], [-1, 1, 1], [1, -1, 1], [1, 1, -1], [1, 1, 1]],
        "faces": [[0, 1, 4, 2], [0, 2, 6, 3], [0, 3, 5, 1], [1, 5, 7, 4], [2, 4, 7, 6], [3, 6, 7, 5]]},
    "octahedron": {
        "values": [],
        "iverts": [[0, 0, 1], [1, 0, 0], [0, 1, 0], [-1, 0, 0], [0, -1, 0], [0, 0, -1]],
        "faces": [[0, 1, 2], [0, 2, 3], [0, 3, 4], [0, 4, 1], [1, 4, 5], [1, 5, 2], [2, 5, 3], [3, 5, 4]]},
    "icosahedron": {
        "values": [(1 + np.sqrt(5)) / 2],
        "iverts": [[0, +1, +2], [-2, 0, +1], [0, -1, +2], [+2, 0, +1], [+1, +2, 0], [-1, +2, 0],
                   [-1, -2, 0], [-2, 0, -1], [+1, -2, 0], [+2, 0, -1], [0, +1, -2], [0, -1, -2]],
        "faces": [[0, 1, 2], [0, 2, 3], [0, 3, 4], [0, 4, 5], [0, 5, 1], [1, 5, 7], [1, 7, 6],
                  [1, 6, 2], [2, 6, 8], [2, 8, 3], [3, 8, 9], [3, 9, 4], [4, 9, 10], [4, 10, 5],
                  [5, 10, 7], [6, 7, 11], [6, 11, 8], [7, 10, 11], [8, 11, 9], [9, 11, 10]]}}


def iverts_to_verts(values, indexed_vertices):
    """
    For when coordinates are made up from a discrete number of values.
    """
    values = np.array([0, 1] + values)
    verts = np.sign(indexed_vertices) * values[np.absolute(indexed_vertices)]
    return verts / np.linalg.norm(verts[0])


def faces_to_edges(faces):
    edges = []
    for face in faces:
        edges.extend([(i, j) for i, j in zip(face, face[1:] + [face[0]])])
    edges = [(min(i, j), max(i, j)) for i, j in edges]  # normalize tuples
    return list(sorted(set(edges)))  # dedupe and sort


def faces_to_triangles(faces):
    return [[face[0], v1, v2] for face in faces for v1, v2 in zip(face[1:-1], face[2:])]


def subdivide(verts, triangles, subdivisions=1):

    def normalized_midpoint(verts, i, j):
        mp = (verts[i] + verts[j]) / 2
        return mp / np.linalg.norm(mp)

    for it in range(subdivisions):

        # A new vertex is added at the midpoint of every edge (because triangles)

        edges = faces_to_edges(triangles)
        new_verts = [normalized_midpoint(verts, i, j) for i, j in edges]
        new_verts = np.concatenate([verts] + [np.atleast_2d(v) for v in new_verts])

        # Map from edge (expressed a tuple of vertexes' indexes) to the index of the midpoint in verts

        edge_to_index = {e: index + len(verts) for index, e in enumerate(edges)}
        edge_to_index.update({(vj, vi): index for (vi, vj), index in edge_to_index.iteritems()})

        # Subdivide faces

        new_triangles = []
        for a, b, c in triangles:
            ab, bc, ac = map(lambda e: edge_to_index[e], ((a, b), (b, c), (a, c)))
            new_triangles.extend([[a, ab, ac], [b, bc, ab], [c, ac, bc], [ac, ab, bc]])

        verts, triangles = new_verts, new_triangles  # assignment does not affect caller variables

    return verts, triangles


# --- Pyglet code below --- --- --- --- ---

import pyglet

# pyglet.options['debug_gl'] = False  # Disable error checking for increased performance

from pyglet.gl import *
from pyglet.window import key

window = pyglet.window.Window(resizable=True)


def make_batch():

    solid = solids[solids.keys()[window.solid]]

    verts = iverts_to_verts(solid['values'], solid['iverts'])
    triangles = faces_to_triangles(solid['faces'])
    verts, triangles = subdivide(verts, triangles, subdivisions=window.subdivisions)
    edges = faces_to_edges(triangles)

    vertices = [v for xyz in verts for v in xyz]
    edges = [index for ij in edges for index in ij]
    triangles = [i for f in triangles for i in f]
    cols = np.random.random(len(vertices))

    batch = pyglet.graphics.Batch()
    if window.wireframe:
        batch.add_indexed(len(vertices) / 3, pyglet.gl.GL_LINES, None,
                          edges, ('v3f', vertices), ('c3f', cols))
    else:
        batch.add_indexed(len(vertices) / 3, pyglet.gl.GL_TRIANGLES, None,
                          triangles, ('v3f', vertices), ('c3f', cols))

    window.label.text = '{}: {}'.format(solids.keys()[window.solid], window.subdivisions)
    return batch


@window.event
def on_resize(width, height):

    rfix = 2  # mac OSX retina fix. Should be addressed by pyglet v1.4+
    glViewport(0, 0, width * rfix, height * rfix)
    window.aspect = width / float(height)
    return pyglet.event.EVENT_HANDLED


def draw_2D():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, window.width * 2, 0, window.height * 2, -1, 1)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def draw_3D():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(50., window.aspect, .1, 1000.)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0, 0, -3)
    glRotatef(window.rz, 0, 0, 1)
    glRotatef(window.ry, 0, 1, 0)
    glRotatef(window.rx, 1, 0, 0)


@window.event
def on_draw():

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    draw_3D()
    window.batch.draw()

    draw_2D()
    window.label.draw()
    window.help.draw()


@window.event
def on_key_press(symbol, modifiers):

    if symbol == key.T:
        window.solid += 1
        window.solid %= len(solids)
        window.batch = make_batch()

    if symbol == key.S:
        window.subdivisions += 1 if modifiers & key.MOD_SHIFT else -1
        window.subdivisions = max(0, window.subdivisions)
        window.batch = make_batch()

    if symbol == key.W:
        window.wireframe ^= True
        window.batch = make_batch()

    if symbol == key.R:
        window.rotate ^= True


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
    window.subdivisions = 0
    window.wireframe = False
    window.solid = 0
    window.help_str = 'T: cycle solids | s/S: subdivisions | W: wireframe | R: rotation'
    window.help = pyglet.text.Label(window.help_str, font_name='Courier New', font_size=24,
                                    x=15, y=window.height*2 - 15*2, color=(0, 0, 0, 255))
    window.label = pyglet.text.Label('', font_name='Courier New', font_size=24, x=15, y=15, color=(1, 0, 0, 255))
    window.batch = make_batch()

    pyglet.clock.schedule(update)


init()
pyglet.app.run()



#boids
#tetraballs (cube tetra)

"""
from matplotlib import pyplot as plot
from mpl_toolkits.mplot3d import Axes3D

fig = plot.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(new_verts[:, 0], new_verts[:, 1], new_verts[:, 2])
"""
