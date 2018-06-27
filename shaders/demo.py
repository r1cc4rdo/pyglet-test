#!/usr/bin/env python

from common import *

window = make_window()


@window.event
def on_draw():

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -3.5)
    glRotatef(window.rot.x, 0, 0, 1)
    glRotatef(window.rot.y, 0, 1, 0)
    glRotatef(window.rot.z, 1, 0, 0)

    if window.flags['wireframe']:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    if window.flags['figure']:
        batch1.draw()
    else:
        batch2.draw()

    glPolygonMode(GL_FRONT, GL_FILL)
    show_ui(window.flags['help'])


setup()
add_keystroke(key.H, 'help', 'Show this dialog', True)
add_keystroke(key.F, 'figure', 'Toggle figure', False)
add_keystroke(key.T, 'wireframe', 'Toggle wireframe', False)
batch1, batch2 = make_batches()
pyglet.app.run()
