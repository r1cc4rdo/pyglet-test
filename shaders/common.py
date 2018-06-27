from euclid import *

import pyglet
from pyglet import resource
from objects import *

window = None


def vec(*args): # create ctypes arrays of floats:
    return (GLfloat * len(args))(*args)


def make_batches():

    batch1 = pyglet.graphics.Batch()
    torus = Torus(1, 0.3, 80, 25, batch=batch1)

    batch2 = pyglet.graphics.Batch()
    sphere = Sphere(1.2, 50, batch=batch2)

    return batch1, batch2


def setup():

    glClearColor(1, 1, 1, 1)
    glColor4f(1.0, 0.0, 0.0, 0.5)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)

    i = 0
    texture = []
    while True:
        texturefile = 'Texturemap' + str(i) + '.jpg'
        try:
            textureSurface = pyglet.resource.texture(texturefile)
        except pyglet.resource.ResourceNotFoundException as e:
            break

        print "Loading Texture", texturefile
        tex = textureSurface.get_texture()
        glBindTexture(tex.target, tex.id)
        print "Texture ", i, " bound to ", tex.id
        texture.append(tex)

        i += 1

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Simple light setup.  On Windows GL_LIGHT0 is enabled by default,
    # but this is not the case on Linux or Mac, so remember to always
    # include it.

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)

    glLightfv(GL_LIGHT0, GL_POSITION, vec(20.0, 20.0, 20.0, 1.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, vec(0.3, 0.3, 0.3, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, vec(0.9, 0.9, 0.9, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, vec(1.0, 1.0, 1.0, 1.0))

    glLightfv(GL_LIGHT1, GL_POSITION, vec(-20.0, -20.0, 20.0, 0.0))
    glLightfv(GL_LIGHT1, GL_DIFFUSE, vec(.6, .6, .6, 1.0))
    glLightfv(GL_LIGHT1, GL_SPECULAR, vec(1.0, 1.0, 1.0, 1.0))

    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(0.8, 0.5, 0.5, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, vec(1, 1, 1, 1))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50)

    return texture


def show_ui(showdialog):

    glActiveTexture(GL_TEXTURE0)
    glEnable(GL_TEXTURE_2D)
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    if showdialog:
        glLoadIdentity()
        glTranslatef(0, -200, -450)
        window.label.draw()

    glLoadIdentity()
    glTranslatef(250, -290, -500)
    window.fps_display.draw()

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)


def on_resize(width, height):
    if height < 2:
        height = 2

    window.label.x = width // 2
    window.label.width = (width * 4) // 5
    window.label.y = height // 2
    window.label.height = (height * 4) // 5

    glViewport(0, 0, width * 2, height * 2)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60., width / float(height), .1, 1000.)
    glMatrixMode(GL_MODELVIEW)

    return pyglet.event.EVENT_HANDLED


def on_key_press(symbol, modifiers):

    if symbol in window.keys:

        flag = window.keys[symbol]['name']
        window.flags[flag] ^= True
        print "{}: {}".format(flag, window.flags[flag])

    else:

        print "Unmapped keystroke"


def add_keystroke(keystroke, name, help, initial_value=True):

    window.label.text += '{}: {}<br />'.format(chr(keystroke).upper(), help)
    window.keys[keystroke] = {"name": name, "help": help}
    window.flags[name] = initial_value


def make_window(resource_dir=None):

    global window

    try:  # Try and create a window with multisampling (antialiasing)
        config = Config(sample_buffers=1, samples=4, depth_size=16, double_buffer=True, )
        window = pyglet.window.Window(resizable=True, config=config, vsync=False)  # vsync=False to check framerate
    except pyglet.window.NoSuchConfigException:  # Fall back to no multisampling for old hardware
        window = pyglet.window.Window(resizable=True)

    window.label = pyglet.text.HTMLLabel('',
                                         width=(window.width * 4) // 5, height=(window.height * 4) // 5,
                                         multiline=True, anchor_x='center', anchor_y='center')
    window.fps_display = pyglet.clock.ClockDisplay()
    window.set_handler('on_key_press', on_key_press)
    window.set_handler('on_resize', on_resize)
    window.rot = Vector3(0, 0, 90)
    window.autorotate = True
    window.flags = {}
    window.keys = {}

    if resource_dir:
        resource.path.append(resource_dir)
        resource.reindex()

    return window


def update(dt):

    if window.autorotate:
        window.rot += Vector3(0.1, 12, 5) * dt
        window.rot.x %= 360
        window.rot.y %= 360
        window.rot.z %= 360


pyglet.clock.schedule(update)


def dismiss_dialog(dt):

    window.showdialog = False


pyglet.clock.schedule_once(dismiss_dialog, 10.0)
