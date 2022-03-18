from array import array
from PIL import Image

import arcade
import arcade.gl as gl
import numpy as np
from pyglet.math import Vec4

from marchingSquares import gen_square
from singletons.chunk_gen import generate_chunk

CHUNK_SIZE = 32

CHUNK_PROGRAM = None


def set_chunk_program(ctx: arcade.ArcadeContext):
    global CHUNK_PROGRAM
    CHUNK_PROGRAM = ctx.load_program(vertex_shader="shaders/planet_chunk_vert.glsl",
                                     fragment_shader="shaders/planet_chunk_frag.glsl")


world_seed = 1


def set_world_seed(new_seed):
    global world_seed
    world_seed = new_seed


class PlanetData:

    def __init__(self, core_radius: int, core_gap: int, chunk_radius: int):
        self.core_radius = core_radius
        self.core_gap = core_gap
        self.chunk_radius = chunk_radius
        self.radius = (self.chunk_radius-1) * (CHUNK_SIZE-1) + CHUNK_SIZE//2


default_planet_data = PlanetData(24, 48, 24)


def chunk_geometry_shader(vertex_buffer, index_buffer, ctx: gl.Context):
    return ctx.geometry([gl.BufferDescription(vertex_buffer, '2f', ['vertPos'])],
                        index_buffer=index_buffer, index_element_size=2, mode=gl.TRIANGLES)


class Chunk:

    def __init__(self, x, y, parent_planet, start_generated=False):
        self.planet: Planet = parent_planet

        self.x = x
        self.y = y

        self.points = None

        self.shown = self.generated = False

        self.vertex_buffer = self.index_buffer = self.geometry = None

        if start_generated:
            self.reveal()

    def reveal(self):
        if self.generated:
            self.shown = True
        else:
            self.generated = True
            self.generate()
            self.shown = True

    def hide(self):
        self.shown = False

    def generate(self):
        data = self.planet.data

        c_x = (CHUNK_SIZE-1)*self.x
        c_y = (CHUNK_SIZE-1)*self.y
        self.points = generate_chunk(c_x, c_y, data)

        p = self.points
        vertices = []
        indices = []
        for p_x in range(CHUNK_SIZE-1):
            for p_y in range(CHUNK_SIZE-1):
                w_x = c_x + p_x
                w_y = c_y + p_y
                values = (p[p_x, p_y, 0], p[p_x, p_y+1, 0],
                          p[p_x+1, p_y+1, 0], p[p_x+1, p_y, 0])
                ind, vert = gen_square(values, w_x, w_y, len(vertices)//2)
                indices += ind
                vertices += vert

        if len(indices):
            ctx = gl.Context.active
            self.index_buffer = ctx.buffer(data=array('H', indices))
            self.vertex_buffer = ctx.buffer(data=array('f', vertices))
            self.geometry = chunk_geometry_shader(self.vertex_buffer, self.index_buffer, ctx)

    def render(self):
        if self.shown and self.generated and self.geometry is not None:
            self.geometry.render(CHUNK_PROGRAM)

        # for x in range(CHUNK_SIZE):
        #     for y in range(CHUNK_SIZE):
        #         w_x = self.x*15 + x
        #         w_y = self.y*15 + y
        #         p = self.points[x, y]
        #         c = [127, 127+127*p, 127*math.ceil(p)]
        #         arcade.draw_point(w_x*60, w_y*60, c, 5)


class Planet:

    def __init__(self, planet_data):
        self.data: PlanetData = planet_data
        self.chunks = np.empty([self.data.chunk_radius*2, self.data.chunk_radius*2], Planet)

        r = self.data.chunk_radius
        for x in range(-r, r):
            for y in range(-r, r):
                self.chunks[x+r, y+r] = Chunk(x, y, self)
        self.shown_chunks = []

    def find_revealed_chunks(self, matrix):
        pass
        self.shown_chunks = []
        for line in self.chunks:
            for chunk in line:
                done = False
                for x in range(0, 2):
                    for y in range(0, 2):
                        check = matrix @ Vec4((chunk.x+x)*(CHUNK_SIZE-1)*60, (chunk.y+y)*(CHUNK_SIZE-1)*60, 0, 1)
                        if -1.5 <= check.x <= 1.25 and -1.25 <= check.y <= 1.5:
                            self.shown_chunks.append(chunk)
                            chunk.reveal()
                            done = True
                            break
                    if done: break
                    else:
                        chunk.hide()

    def draw(self):
        for line in self.chunks:
            for chunk in line:
                chunk.render()
        # for chunk in self.shown_chunks:
        #    chunk.render()


default_planet = Planet(default_planet_data)
