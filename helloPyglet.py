import pyglet

# pyglet.options['debug_gl'] = False # Disable error checking for increased performance

from pyglet.gl import *
from pyglet.window import key, mouse

resources = {}


def set_vertex_array(vs):

    vertices_gl_array = (GLfloat * len(vs))(*vs)
    glVertexPointer(2, GL_FLOAT, 0, vertices_gl_array)


def on_draw_0():

    resources['window'].clear()
    resources['image'].blit(0, 0)
    resources['label'].draw()


def on_draw_1():

    # TODO: label here

    w = resources['window']
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glBegin(GL_TRIANGLES)
    glVertex2f(0, 0)
    glVertex2f(w.width, 0)
    glVertex2f(w.width, w.height)
    glEnd()


def on_draw_2():

    # TODO: label here

    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()  # TODO: why are we loading a modelview identity here
    glDrawArrays(GL_TRIANGLES, 0, len(resources['vertices']) // 2)


def init(music=False, sounds=False):

    resources['window'] = win = pyglet.window.Window()
    resources['image'] = pyglet.resource.image('pyglet.png')
    resources['label'] = pyglet.text.Label('Hello, pyglet',
                                           font_name='Times New Roman', font_size=36,
                                           x=win.width // 2, y=win.height // 2,
                                           anchor_x='center', anchor_y='center')
    if music:
        resources['music'] = pyglet.resource.media('rain.mp3')
        resources['music'].play()

    if sounds:
        resources['sound'] = pyglet.resource.media('toot.wav', streaming=False)

    glEnableClientState(GL_VERTEX_ARRAY)
    resources['vertices'] = vs =  [0, 0, win.width, 0, win.width, win.height]
    set_vertex_array(vs)

    resources['on_draw_fun'] = on_draw_0
    return win


@window.event
def on_draw():
    resources['on_draw_fun']()


@window.event
def on_key_press(symbol, modifiers):

    if 'sound' in resources:
        resources['sound'].play()

    if symbol == key.SPACE:
        print('The SPACE key was pressed.')
        draw_x = [on_draw_0, on_draw_1, on_draw_2]
        idx = draw_x.index(resources['on_draw_fun'])
        resources['on_draw_fun'] = draw_x[(idx + 1) % len(draw_x)]

    print('Some key was pressed.')


@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == mouse.LEFT:
        print('The left mouse button was pressed.')


@window.event
def on_resize(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, width, 0, height, -1, 1)
    # gluPerspective(65, width / float(height), .1, 1000)
    glMatrixMode(GL_MODELVIEW)
    # return pyglet.event.EVENT_HANDLED

init()
# window.push_handlers(pyglet.window.event.WindowEventLogger())
pyglet.app.run()
