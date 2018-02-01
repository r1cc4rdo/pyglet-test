import pyglet

# pyglet.options['debug_gl'] = False # Disable error checking for increased performance

from pyglet.gl import *
from pyglet.window import key, mouse

win = pyglet.window.Window()
win.resources = {}


def set_vertex_array(vs):

    vertices_gl_array = (GLfloat * len(vs))(*vs)
    glVertexPointer(2, GL_FLOAT, 0, vertices_gl_array)


def on_draw_0():

    win.clear()
    win.resources['image'].blit(0, 0)
    win.resources['label'].draw()


def on_draw_1():

    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glBegin(GL_TRIANGLES)
    glVertex2f(0, 0)
    glVertex2f(win.width, 0)
    glVertex2f(win.width, win.height)
    glEnd()

    win.resources['label'].draw()


def on_draw_2():

    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()  # TODO: why are we loading a modelview identity here
    glDrawArrays(GL_TRIANGLES, 0, len(win.resources['vertices']) // 2)

    win.resources['label'].draw()


def init(music=False, sounds=False):

    win.resources['image'] = pyglet.resource.image('pyglet.png')
    win.resources['label'] = pyglet.text.Label('Hello, pyglet',
                                               font_name='Times New Roman', font_size=36,
                                               x=win.width // 2, y=win.height // 2,
                                               anchor_x='center', anchor_y='center')
    if music:
        win.resources['music'] = pyglet.resource.media('rain.mp3')
        win.resources['music'].play()

    if sounds:
        win.resources['sound'] = pyglet.resource.media('toot.wav', streaming=False)

    glEnableClientState(GL_VERTEX_ARRAY)
    win.resources['vertices'] = vs = [100, 100, 200, 100, 200, 200]
    set_vertex_array(vs)

    win.resources['on_draw_fun'] = on_draw_0
    return win


@win.event
def on_draw():

    win.resources['on_draw_fun']()


@win.event
def on_key_press(symbol, modifiers):

    if 'sound' in win.resources:
        win.resources['sound'].play()

    if symbol == key.SPACE:
        print('The SPACE key was pressed.')
        draw_x = [on_draw_0, on_draw_1, on_draw_2]
        idx = draw_x.index(win.resources['on_draw_fun'])
        win.resources['on_draw_fun'] = draw_x[(idx + 1) % len(draw_x)]
        win.resources['label'].text = win.resources['on_draw_fun'].__name__
    else:
        print('Some key was pressed. Try pressing SPACE.')


@win.event
def on_mouse_press(x, y, button, modifiers):

    if button == mouse.LEFT:
        print('The left mouse button was pressed.')


@win.event
def on_resize(width, height):
    """
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, width, 0, height, -1, 1)
    # gluPerspective(65, width / float(height), .1, 1000)
    glMatrixMode(GL_MODELVIEW)
    # return pyglet.event.EVENT_HANDLED
    """
    pass


init()
# win.push_handlers(pyglet.window.event.WindowEventLogger())
pyglet.app.run()
