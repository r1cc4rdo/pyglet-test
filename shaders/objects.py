from pyglet.gl import *
from math import pi, sin, cos, sqrt


class Torus(object):
    list = None

    def __init__(self, radius, inner_radius, slices, inner_slices,
                 batch, group=None):
        # Create the vertex and normal arrays.
        vertices = []
        normals = []
        textureuvw = []
        tangents = []

        u_step = 2 * pi / (slices - 1)
        v_step = 2 * pi / (inner_slices - 1)
        u = 0.
        for i in range(slices):
            cos_u = cos(u)
            sin_u = sin(u)
            v = 0.
            for j in range(inner_slices):
                cos_v = cos(v)
                sin_v = sin(v)

                d = (radius + inner_radius * cos_v)
                x = d * cos_u
                y = inner_radius * sin_v
                z = -d * sin_u

                nx = cos_u * cos_v
                ny = sin_v
                nz = -sin_u * cos_v

                n = sqrt(nx * nx + ny * ny + nz * nz)
                if n < 0.99 or n > 1.01:
                    nx = nx / n
                    ny = ny / n
                    nz = nz / n
                    print "Torus: N normalized"

                tx = -sin_u
                ty = 0
                tz = -cos_u

                a = sqrt(tx * tx + ty * ty + tz * tz)
                if a > 0.001:
                    tx = tx / a
                    ty = ty / a
                    tz = tz / a

                vertices.extend([x, y, z])
                normals.extend([nx, ny, nz])
                textureuvw.extend([u / (2.0 * pi), v / (2.0 * pi), 0.0])
                tangents.extend([int(round(255 * (0.5 - 0.5 * tx))),
                                 int(round(255 * (0.5 - 0.5 * ty))),
                                 int(round(255 * (0.5 - 0.5 * tz)))])
                v += v_step
            u += u_step

        # Create a list of triangle indices.
        indices = []
        for i in range(slices - 1):
            for j in range(inner_slices - 1):
                p = i * inner_slices + j
                indices.extend([p, p + inner_slices, p + inner_slices + 1])
                indices.extend([p, p + inner_slices + 1, p + 1])

        self.vertex_list = batch.add_indexed(len(vertices) // 3,
                                             GL_TRIANGLES,
                                             group,
                                             indices,
                                             ('v3f/static', vertices),
                                             ('n3f/static', normals),
                                             ('t3f/static', textureuvw),
                                             ('c3B/static', tangents))

    def delete(self):
        self.vertex_list.delete()


class Sphere(object):
    list = None

    def __init__(self, radius, slices, batch, group=None):
        # Create the vertex and normal arrays.
        vertices = []
        normals = []
        textureuvw = []
        tangents = []

        u_step = 2 * pi / (slices - 1)
        v_step = pi / (slices - 1)
        u = 0.
        for i in range(slices):
            cos_u = cos(u)
            sin_u = sin(u)
            v = 0.
            for j in range(slices):
                cos_v = cos(v)
                sin_v = sin(v)

                nx = sin_v * cos_u
                ny = -cos_v
                nz = -sin_v * sin_u

                n = sqrt(nx * nx + ny * ny + nz * nz)
                if n < 0.99 or n > 1.01:
                    nx = nx / n
                    ny = ny / n
                    nz = nz / n
                    print "Sphere: N normalized"

                tx = nz
                ty = 0
                tz = -nx

                a = sqrt(tx * tx + ty * ty + tz * tz)
                if a > 0.001:
                    tx = tx / a
                    ty = ty / a
                    tz = tz / a

                x = radius * nx
                y = radius * ny
                z = radius * nz

                vertices.extend([x, y, z])
                normals.extend([nx, ny, nz])
                textureuvw.extend([u / (2 * pi), v / (pi), 0.0])
                tangents.extend([int(round(255 * (0.5 - 0.5 * tx))),
                                 int(round(255 * (0.5 - 0.5 * ty))),
                                 int(round(255 * (0.5 - 0.5 * tz)))])
                v += v_step
            u += u_step

        # Create a list of triangle indices.
        indices = []
        for i in range(slices - 1):
            for j in range(slices - 1):
                p = i * slices + j
                indices.extend([p, p + slices, p + slices + 1])
                indices.extend([p, p + slices + 1, p + 1])

        self.vertex_list = batch.add_indexed(len(vertices) // 3,
                                             GL_TRIANGLES,
                                             group,
                                             indices,
                                             ('v3f/static', vertices),
                                             ('n3f/static', normals),
                                             ('t3f/static', textureuvw),
                                             ('c3B/static', tangents))

    def delete(self):
        self.vertex_list.delete()
