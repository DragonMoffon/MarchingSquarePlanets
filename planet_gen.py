from array import array
from time import time

import arcade
import arcade.gl as gl
import numpy as np

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
                        index_buffer=index_buffer, index_element_size=4, mode=gl.TRIANGLES)


def vertex_geometry_shader(vertex_buffer, ctx: gl.Context):
    return ctx.geometry([gl.BufferDescription(vertex_buffer, '2f', ['vertPos'])],
                        mode=gl.POINTS)


class Chunk:

    def __init__(self, x, y, parent_planet, start_generated=False):
        self.planet: Planet = parent_planet
        self.x = x
        self.y = y

        self.points = None

        self.shown = self.generated = False

        self.vertex_buffer = self.index_buffer = self.geometry = self.geometryTest = None

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
        self.points, self.vertex_buffer, self.index_buffer = generate_chunk(c_x, c_y, data, (self.x==0 and self.y==0))
        if self.vertex_buffer is not None and self.index_buffer is not None:
            ctx = gl.Context.active
            self.geometry = chunk_geometry_shader(self.vertex_buffer, self.index_buffer, ctx)
            self.geometryTest = vertex_geometry_shader(self.vertex_buffer, ctx)

    def render(self):
        if self.shown and self.generated and self.geometry is not None:
            arcade.get_window().ctx.point_size = 15
            self.geometry.render(CHUNK_PROGRAM)
            # self.geometryTest.render(CHUNK_PROGRAM)


class Planet:

    def __init__(self, planet_data):
        self.data: PlanetData = planet_data
        self.chunks = np.empty([self.data.chunk_radius*2, self.data.chunk_radius*2], Planet)
        r = self.data.chunk_radius
        for x in range(-r, r):
            for y in range(-r, r):
                self.chunks[x+r, y+r] = Chunk(x, y, self)
        self.shown_chunks = []

    def find_revealed_chunks(self, p_chunk_x, p_chunk_y, scale):
        for chunk in self.shown_chunks:
            chunk.hide()

        shift = 1
        while shift * int(CHUNK_SIZE//2 * 60 * scale)+1 < 1049:
            shift += 1

        self.shown_chunks = []
        core_pos = p_chunk_x+self.data.chunk_radius, p_chunk_y+self.data.chunk_radius
        for x in range(-shift, shift+1):
            for y in range(-shift, shift+1):
                c_x = core_pos[0]+x
                c_y = core_pos[1]+y

                if 0 <= c_x < self.data.chunk_radius*2 and 0 <= c_y < self.data.chunk_radius*2:
                    chunk = self.chunks[core_pos[0]+x, core_pos[1]+y]
                    chunk.reveal()
                    self.shown_chunks.append(chunk)

    def draw(self):
        for chunk in self.shown_chunks:
            chunk.render()
        # for chunk in self.shown_chunks:
        #    chunk.render()


default_planet = Planet(default_planet_data)
