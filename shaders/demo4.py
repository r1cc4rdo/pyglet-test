#!/usr/bin/env python

from common import *

vs = '''
varying vec3 lightDir0, lightDir1, eyeVec;
varying vec3 normal, tangent, binormal;

void main()
{
    normal = normalize(gl_NormalMatrix * gl_Normal);
    tangent = normalize(gl_NormalMatrix * (gl_Color.rgb - 0.5));
    binormal = cross(normal, tangent);
    mat3 TBNMatrix = mat3(tangent, binormal, normal);

    vec3 vVertex = vec3(gl_ModelViewMatrix * gl_Vertex);

    lightDir0 = vec3(gl_LightSource[0].position.xyz - vVertex) * TBNMatrix;
    lightDir1 = vec3(gl_LightSource[1].position.xyz - vVertex) * TBNMatrix;
    eyeVec    = -vVertex * TBNMatrix;

    gl_Position = ftransform();
    gl_TexCoord[0]  = gl_TextureMatrix[0] * gl_MultiTexCoord0;
}
'''
fs = '''
varying vec3 normal, lightDir0, lightDir1, eyeVec;
uniform sampler2D my_color_texture[2]; //0 = ColorMap, 1 = NormalMap
uniform int toggletexture; // false/true
uniform int togglebump;    // false/true

void main (void)
{
    vec4 texColor = vec4(texture2D(my_color_texture[0], gl_TexCoord[0].st).rgb, 1.0);
    vec3 norm     = normalize( texture2D(my_color_texture[1], gl_TexCoord[0].st).rgb - 0.5);

    if (toggletexture == 0) texColor = gl_FrontMaterial.ambient;
    vec4 final_color = (gl_FrontLightModelProduct.sceneColor * vec4(texColor.rgb,1.0)) +
                       (gl_LightSource[0].ambient * vec4(texColor.rgb,1.0)) +
                       (gl_LightSource[1].ambient * vec4(texColor.rgb,1.0));

    vec3 N = (togglebump != 0) ? normalize(norm) : vec3(0.0, 0.0, 1.0 );
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

window = make_window('textures/pack2')
shader = Shader([vs], [fs])


@window.event
def on_draw():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -3.5)
    glRotatef(window.rot.x, 0, 0, 1)
    glRotatef(window.rot.y, 0, 1, 0)
    glRotatef(window.rot.z, 1, 0, 0)

    glPolygonMode(GL_FRONT, GL_FILL)

    if window.flags['shader']:
        # bind our shader
        shader.bind()
        shader.uniformi('toggletexture', window.flags['texture'])
        shader.uniformi('togglebump', window.flags['bump'])
        for i in range(len(texture)):
            glActiveTexture(GL_TEXTURE0 + i)
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, texture[i].id)
            shader.uniformi('my_color_texture[' + str(i) + ']', i)
        if window.flags['figure']:
            batch1.draw()
        else:
            batch2.draw()

        for i in range(len(texture)):
            glActiveTexture(GL_TEXTURE0 + i)
            glDisable(GL_TEXTURE_2D)
        shader.unbind()
    else:
        if window.flags['figure']:
            batch1.draw()
        else:
            batch2.draw()

    show_ui(window.flags['help'])


texture = setup()
add_keystroke(key.H, 'help', 'Show this dialog', True)
add_keystroke(key.B, 'bump', 'Toggle bumpmap', True)
add_keystroke(key.F, 'figure', 'Toggle figure', False)
add_keystroke(key.T, 'texture', 'Toggle texture', True)
add_keystroke(key.S, 'shader', 'Toggle shader', True)
batch1, batch2 = make_batches()
pyglet.app.run()
