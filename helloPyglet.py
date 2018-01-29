import pyglet
from pyglet.window import key, mouse

window = pyglet.window.Window()

# sound = pyglet.resource.media('toot.wav', streaming=False)
music = pyglet.resource.media('rain.mp3')
music.play()

image = pyglet.resource.image('pyglet.png')
label = pyglet.text.Label('Hello, pyglet',
                          font_name='Times New Roman',
                          font_size=36,
                          x=window.width//2, y=window.height//2,
                          anchor_x='center', anchor_y='center')


@window.event
def on_draw():
    window.clear()
    image.blit(0, 0)
    label.draw()


@window.event
def on_key_press(symbol, modifiers):
    # sound.play()
    if symbol == key.A:
        print('The "A" key was pressed.')
    elif symbol == key.LEFT:
        print('The left arrow key was pressed.')
    elif symbol == key.ENTER:
        print('The enter key was pressed.')


@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == mouse.LEFT:
        print('The left mouse button was pressed.')

# window.push_handlers(pyglet.window.event.WindowEventLogger())
pyglet.app.run()


# --- --- --- --- ---

# print "{:b}".format(32)
#
# bits = 1
# while True:
#
#     for n in xrange(2**bits):
#

# --- --- --- --- ---

# import math
# import numpy as np
#
# phi = (1 + math.sqrt(5)) / 2
# vert = np.array([[0, x, y] for x in (-1, +1) for y in (phi, -phi)])  # [(0, 1, 3, 2), :]
# vert = np.concatenate([np.roll(vert, shl) for shl in (0, -1, -2)])
#
# faces = (( 0,  0,  0), ( 0,  0,  0), ( 0,  0,  0), ( 0,  0,  0), ( 0,  0,  0),
#          ( 0,  0,  0), ( 0,  0,  0), ( 0,  0,  0), ( 0,  0,  0), ( 0,  0,  0),
#          ( 0,  0,  0), ( 0,  0,  0), ( 0,  0,  0), ( 0,  0,  0), ( 0,  0,  0),
#          ( 0,  0,  0), ( 0,  0,  0), ( 0,  0,  0), ( 0,  0,  0), ( 0,  0,  0))
#
# print vert

# numpy.roll(a, shift, axis=None)[source]

#   0  +-1  +-p
# +-1  +-p    0
# +-p    0  +-1
#
