#!/usr/bin/env python

from common import *

vs = '''
varying vec3 lightDir0, lightDir1, eyeVec;
varying vec3 normal, tangent, binormal;

void main()
  {
// Create the Texture Space Matrix
  normal   = normalize(gl_NormalMatrix * gl_Normal);
  tangent  = normalize(gl_NormalMatrix * (gl_Color.rgb - 0.5));
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
uniform sampler2D my_color_texture[4]; //0 = ColorMap, 1 = NormalMap, 2 = HeightMap, 3 = Glossmap
uniform int   toggletexture;  // false/true
uniform int   toggleaniso;    // false/true
uniform int   togglebump;     // false/true
uniform int   togglemodel;    // false = Phong, true = Blinn-Phong
uniform float parallaxheight;

// #define USELIGHT1 // define for 2 lights

void main()
  {
// Compute parallax displaced texture coordinates
  vec3 eye = normalize(-eyeVec);
  vec2 offsetdir = vec2( eye.x, eye.y );
  vec2 coords1 = gl_TexCoord[0].st;
  float height1 = parallaxheight * (texture2D( my_color_texture[2], coords1).r - 0.5);
  vec2 offset1  = height1 * offsetdir;
  vec2 coords2  = coords1 + offset1;
  float height2 = parallaxheight * (texture2D( my_color_texture[2], coords2).r - 0.5);
//vec2 offset2  = height2 * offsetdir;
  vec2 newCoords = coords2;
  if ( length( offset1 ) > 0.01 ) // 5.0 * abs( height1 ) > abs( height2 ) )
    newCoords = coords1 + (height2/height1) * offset1;

  vec4 texColor = vec4(texture2D(my_color_texture[0], newCoords).rgb, 1.0);
  vec3 norm     = normalize( texture2D(my_color_texture[1], newCoords).rgb - 0.5);
  vec3 gloss    = texture2D(my_color_texture[3], newCoords).rgb; // Glossmap: r=brightness, g=specular exp, b=strand-dirx

  if ( toggleaniso == 0 )
    gloss = vec3(1.0, 0.5, 0.0 ); // bright spot medium sized, isotropic
  if ( toggletexture == 0 )
    texColor = gl_FrontMaterial.ambient;
  vec3 N = (togglebump != 0) ? normalize(norm) : vec3(0.0, 0.0, 1.0 );

  vec2 straindir = (gloss.b > 0.05) ? normalize(vec2(cos(3.14159 * gloss.b),
                                                     sin(3.14159 * gloss.b))):
                                      vec2( 1.0, 0.0 );
  vec3 tplane = cross( N, vec3( straindir, 0.0 )); // normal vector of T-Plane 

  vec4 final_color = ( gl_FrontLightModelProduct.sceneColor +   // start with ambient lighting
                       gl_LightSource[0].ambient +
                       gl_LightSource[1].ambient ) * vec4(texColor.rgb,1.0);
  vec3 L0 = normalize(lightDir0);
  vec3 L1 = normalize(lightDir1);

  float lambertTerm0 = dot(N,L0);
  float lambertTerm1 = dot(N,L1);

  vec3  E = normalize(eyeVec);  // Eye Vector
  vec3  H;                      // Half Vector
  vec3  R;                      // Reflected Light
  float kspec;                  // Brightness in Eye direction  
  float kexp;                   // Phong Fall-Off Exponent  

/* LIGHT 0 */
  if ( lambertTerm0 > 0.0) // Light on the same side as the Normal
    {
    final_color += (gl_LightSource[0].diffuse * gl_FrontMaterial.diffuse * lambertTerm0) * vec4(texColor.rgb,1.0);
    }

  if ( gloss.b > 0.05 ) // && lambertTerm0 > 0.0 )  // 0=isotrop, 1..255 = strain positioned 0..180 degrees to tangent
    {
//  H = normalize( E + L0 );

    H = normalize( E + L0 - dot(E + L0,  tplane) * tplane );

    L0 = normalize( L0 - dot(L0, tplane) * tplane ); // project light to texture plane
    E  = normalize( E  - dot(E,  tplane) * tplane ); // project eye   to texture plane

    R = reflect(-L0, N);

    vec2 P = normalize(H.xy);             // Phi: H-Projection to the texture plane

    if ( togglemodel == 0 )
      {
      kspec = dot( R, E );                  // Phong
      kexp = gloss.g * gloss.g * 128.0;
      }
    else
      {
      kspec = dot( H, N );                  // Blinn-Phong
      kexp = gloss.g * gloss.g * 128.0;
      }
    }
  else // isotropic
    {
    H = normalize( E + L0 );
    R = reflect(-L0, N);
    if ( togglemodel == 0 )
      {
      kspec = dot( R, E );                  // Phong
      kexp = gloss.g * gloss.g * 128.0;
      }
    else
      {
      kspec = dot( N, H );                  // Blinn-Phong
      kexp = 3.0 * gloss.g * gloss.g * 128.0; // "3.0" approximates Brightness of Phong
      }
    }
  if ( kspec > 0.0 )
    {  
    float specular = pow( max(0.0, kspec), kexp );        // replaces gl_FrontMaterial.shininess
    final_color += gl_LightSource[0].specular * gl_FrontMaterial.specular * specular;
    }

#ifdef USELIGHT1
/* LIGHT 1 */
  if ( lambertTerm1 > 0.0) // Light on the same side as the Normal
    {
    final_color += (gl_LightSource[1].diffuse * gl_FrontMaterial.diffuse * lambertTerm1) * vec4(texColor.rgb,1.0);
    }

  if ( gloss.b > 0.05 ) // && lambertTerm1 > 0.0 )  // 0=isotrop, 1..255 = strain positioned 0..180 degrees to tangent
    {
//  H = normalize( E + L1 );

    H = normalize( E + L1 - dot(E + L1,  tplane) * tplane );

    L1 = normalize( L1 - dot(L1, tplane) * tplane ); // project light to texture plane
    E  = normalize( E  - dot(E,  tplane) * tplane ); // project eye   to texture plane

    R = reflect(-L1, N);

    vec2 P = normalize(H.xy);             // Phi: H-Projection to the texture plane

    if ( togglemodel == 0 )
      {
      kspec = dot( R, E );                  // Phong
      kexp = gloss.g * gloss.g * 128.0;
      }
    else
      {
      kspec = dot( H, N );                  // Blinn-Phong
      kexp = gloss.g * gloss.g * 128.0;
      }
    }
  else // isotropic
    {
    H = normalize( E + L1 );
    R = reflect(-L1, N);
    if ( togglemodel == 0 )
      {
      kspec = dot( R, E );                  // Phong
      kexp = gloss.g * gloss.g * 128.0;
      }
    else
      {
      kspec = dot( N, H );                  // Blinn-Phong
      kexp = 3.0 * gloss.g * gloss.g * 128.0; // "3.0" approximates Brightness of Phong
      }
    }
  if ( kspec > 0.0 )
    {  
    float specular = pow( max(0.0, kspec), kexp );        // replaces gl_FrontMaterial.shininess
    final_color += gl_LightSource[1].specular * gl_FrontMaterial.specular * specular;
    }
#endif
  gl_FragColor = final_color;
  }
'''
shader = Shader([vs], [fs])
window = make_window('textures/hair')


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
        shader.uniformi('toggleaniso', window.flags['anisotropy'])
        shader.uniformi('togglebump', window.flags['bump'])
        shader.uniformi('togglemodel', window.flags['model'])
        shader.uniformf('parallaxheight', 0.02 if window.flags['parallax'] else 0.0)
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
add_keystroke(key.A, 'anisotropy', 'Toggle anisotropy', True)
add_keystroke(key.M, 'model', 'Toggle model', False)
add_keystroke(key.F, 'figure', 'Toggle figure', False)
add_keystroke(key.T, 'texture', 'Toggle texture', True)
add_keystroke(key.P, 'parallax', 'Toggle parallax', True)
add_keystroke(key.S, 'shader', 'Toggle shader', True)
batch1, batch2 = make_batches()
pyglet.app.run()
