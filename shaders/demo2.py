#!/usr/bin/env python

from common import *

vs = '''
varying vec3 normal, lightDir0, lightDir1, eyeVec;

void main()
{
    normal = gl_NormalMatrix * gl_Normal;

    vec3 vVertex = vec3(gl_ModelViewMatrix * gl_Vertex);

    lightDir0 = vec3(gl_LightSource[0].position.xyz - vVertex);
    lightDir1 = vec3(gl_LightSource[1].position.xyz - vVertex);
    eyeVec = -vVertex;

    gl_Position = ftransform();
}
'''
fs = '''
varying vec3 normal, lightDir0, lightDir1, eyeVec;

void main (void)
{
    vec4 final_color =
    (gl_FrontLightModelProduct.sceneColor * gl_FrontMaterial.ambient) +
    (gl_LightSource[0].ambient * gl_FrontMaterial.ambient) +
    (gl_LightSource[1].ambient * gl_FrontMaterial.ambient);

    vec3 N = normalize(normal);
    vec3 L0 = normalize(lightDir0);
    vec3 L1 = normalize(lightDir1);

    float lambertTerm0 = dot(N,L0);
    float lambertTerm1 = dot(N,L1);

    if(lambertTerm0 > 0.0)
    {
        final_color += gl_LightSource[0].diffuse *
                       gl_FrontMaterial.diffuse *
                       lambertTerm0;

        vec3 E = normalize(eyeVec);
        vec3 R = reflect(-L0, N);
        float specular = pow( max(dot(R, E), 0.0),
                         gl_FrontMaterial.shininess );
        final_color += gl_LightSource[0].specular *
                       gl_FrontMaterial.specular *
                       specular;
    }
    if(lambertTerm1 > 0.0)
    {
        final_color += gl_LightSource[1].diffuse *
                       gl_FrontMaterial.diffuse *
                       lambertTerm1;

        vec3 E = normalize(eyeVec);
        vec3 R = reflect(-L1, N);
        float specular = pow( max(dot(R, E), 0.0),
                         gl_FrontMaterial.shininess );
        final_color += gl_LightSource[1].specular *
                       gl_FrontMaterial.specular *
                       specular;
    }
    gl_FragColor = final_color;
}
'''

window = make_window()
shader = Shader([vs], [fs])


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

    if window.flags['shader']:
        shader.bind()

    if window.flags['figure']:
        batch1.draw()
    else:
        batch2.draw()

    if window.flags['shader']:
        shader.unbind()

    glPolygonMode(GL_FRONT, GL_FILL)
    show_ui(window.flags['help'])


setup()
add_keystroke(key.H, 'help', 'Show this dialog', True)
add_keystroke(key.F, 'figure', 'Toggle figure', False)
add_keystroke(key.T, 'wireframe', 'Toggle wireframe', False)
add_keystroke(key.S, 'shader', 'Toggle shader', True)
batch1, batch2 = make_batches()
pyglet.app.run()
