#!/usr/bin/env python

from common import *
from ctypes import byref

vs = '''
#version 110
varying vec3 lightVec, eyeVec;
varying mat3 TBNMatrix;

void main()
  {
  gl_Position = ftransform();
  gl_TexCoord[0]  = gl_TextureMatrix[0] * gl_MultiTexCoord0;

// Create the Texture Space Matrix
  vec3 normal  = normalize(gl_NormalMatrix * gl_Normal);
  vec3 tangent = normalize(gl_NormalMatrix * (gl_Color.rgb - 0.5));
  vec3 binormal = cross(normal, tangent);
  TBNMatrix = mat3(tangent, binormal, normal);

  vec3 position = vec3(gl_ModelViewMatrix * gl_Vertex);

// Compute the Eye Vector
  eyeVec  = (vec3(0.0) - position);
  eyeVec *= TBNMatrix;

// Compute the Light Vector
  lightVec  = gl_LightSource[0].position.xyz - position;
  lightVec *= TBNMatrix;
  }
'''
fs = '''
#version 110
varying vec3 lightVec, eyeVec;
uniform sampler2D my_color_texture[2];
uniform samplerCube my_cube_texture;

uniform int togglebump; // false/true
uniform int textureon; // false/true
uniform float normalweight;

varying mat3 TBNMatrix;

void main (void)
  {
  vec4 ambient  = vec4(0.0, 0.0, 0.0, 1.0); // all components neatly initialized
  vec4 diffuse  = vec4(0.0, 0.0, 0.0, 1.0);
  vec4 specular = vec4(0.0, 0.0, 0.0, 1.0);
  vec4 reflex   = vec4(0.0, 0.0, 0.0, 1.0);

// Compute parallax displaced texture coordinates
  vec3 eye = normalize(eyeVec);
  vec2 offsetdir = vec2( eye.x, eye.y );
  vec2 coords1 = gl_TexCoord[0].st;
  float dist = length(lightVec);
  vec3 light = normalize(lightVec);
  float attenuation = 1.0 / (gl_LightSource[0].constantAttenuation
                      + gl_LightSource[0].linearAttenuation * dist
                      + gl_LightSource[0].quadraticAttenuation * dist * dist);

// Query the Maps
  vec3 color = texture2D(my_color_texture[0], coords1).rgb;
  vec3 norm = vec3( 0.0, 0.0, 1.0 );
  if ( togglebump > 0 )
    {
    norm = normalize( texture2D(my_color_texture[1], coords1).rgb - 0.5);
    norm = vec3( norm.x * normalweight, norm.y * normalweight, norm.z );
    if ( length( norm.z ) < 0.001 )
      norm.z = 0.001;
    }
  vec3 refl = reflect(norm, eye);  // in tangent space !

  vec3 reflw = vec3( 1.0, -1.0, 1.0) * (TBNMatrix * refl);
  reflex = textureCube(my_cube_texture, reflw);

  if ( textureon > 0 )
    gl_FragColor = mix( reflex, vec4(color, 1.0), smoothstep( 0.7, 1.5, length(color)) );
  else
    gl_FragColor = reflex;
  }
'''
shader = Shader([vs], [fs])
window = make_window('textures/pack4')


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
        shader.uniformf('normalweight', 0.5 if window.flags['normal'] else 0.1)
        shader.uniformi('textureon', window.flags['texture'])
        shader.uniformi('togglebump', window.flags['bump'])

        for i in range(len(texture)):
            glActiveTexture(GL_TEXTURE0+i)
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, texture[i].id)
            shader.uniformi('my_color_texture[' + str(i) + ']',i )

        glActiveTexture(GL_TEXTURE0 + len(texture))
        glEnable(GL_TEXTURE_CUBE_MAP)
        glBindTexture(GL_TEXTURE_CUBE_MAP, cubemap)
        shader.uniformi('my_cube_texture', len(texture))

        if window.flags['figure']:
            batch1.draw()
        else:
            batch2.draw()

        for i in range(len(texture)):
            glActiveTexture(GL_TEXTURE0+i)
            glDisable(GL_TEXTURE_2D)
        glActiveTexture(GL_TEXTURE0 + len(texture))
        glDisable(GL_TEXTURE_CUBE_MAP)
        shader.unbind()
    else:
        if window.flags['figure']:
            batch1.draw()
        else:
            batch2.draw()

    show_ui(window.flags['help'])


def setup_cubemap():

    global cubemap

    glEnable(GL_TEXTURE_CUBE_MAP)
    cubemap = GLuint()
    glGenTextures( 1, byref(cubemap))
    cubemap = cubemap.value
    print "CubeTexture is bound to", cubemap
    glBindTexture(GL_TEXTURE_CUBE_MAP, cubemap)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)  # GL_NEAREST)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)  # GL_NEAREST)

    cubename = ['cube_map_positive_x.jpg', 'cube_map_negative_x.jpg',
                'cube_map_negative_y.jpg', 'cube_map_positive_y.jpg',
                'cube_map_negative_z.jpg', 'cube_map_positive_z.jpg']

    for i in range (6):
        cubefile = cubename[i]
        print "Loading Cube Texture", cubefile
        cube = resource.texture(cubefile) # instance of class AbstractImage
        data = cube.get_image_data().get_data('RGBA', cube.width * 4)

        glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0,
                 GL_RGBA8, # texture.format, # 0,   # format
                 cube.width,
                 cube.height,
                 0,
                 GL_RGBA, GL_UNSIGNED_BYTE,
                 data)
    glDisable(GL_TEXTURE_CUBE_MAP)


texture = setup()
setup_cubemap()
add_keystroke(key.H, 'help', 'Show this dialog', True)
add_keystroke(key.B, 'bump', 'Toggle bumpmap', True)
add_keystroke(key.F, 'figure', 'Toggle figure', False)
add_keystroke(key.T, 'texture', 'Toggle texture', True)
add_keystroke(key.N, 'normal', 'Toggle normal weight', True)
add_keystroke(key.S, 'shader', 'Toggle shader', True)
batch1, batch2 = make_batches()
pyglet.app.run()
