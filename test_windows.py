import math
from array import array
from PIL import Image

import random

import arcade
import arcade.gl as gl

import perlin.noise_1d as noise_1d
import perlin.noise_2d as noise_2d
from planet_gen import default_planet_data

import marchingSquares


def gen_points(x, y, seed):
    random.seed(x*seed+y/(100*seed))
    v1 = random.uniform(-1, 1)
    random.seed(x*seed+(y+1)/(100*seed))
    v2 = random.uniform(-1, 1)
    random.seed((x+1)*seed+(y+1)/(100*seed))
    v3 = random.uniform(-1, 1)
    random.seed((x+1)*seed+y/(100*seed))
    v4 = random.uniform(-1, 1)
    return v1, v2, v3, v4


class MarchingWindow(arcade.Window):

    def __init__(self):
        super().__init__(800, 600, "Marching Cube Window")
        self.indices = []
        self.vertices = []

        self.zoom = 1
        self.matrix = [1/(40*self.zoom), 0,    0,
                       0,    1/(30*self.zoom), 0,
                       -40/(40*self.zoom),   -30/(30*self.zoom),   1]

        for x in range(80):
            for y in range(60):
                points = gen_points(x, y, 1)
                indices, vertices = marchingSquares.gen_square(points, x, y, len(self.vertices)//2)
                self.vertices += vertices
                self.indices += indices

        self.vertex_buffer = self.ctx.buffer(data=array('f', self.vertices))
        self.index_buffer = self.ctx.buffer(data=array('H', self.indices))

        self.geometry = self.ctx.geometry([gl.BufferDescription(self.vertex_buffer, '2f', ['in_pos'])],
                                          index_buffer=self.index_buffer, index_element_size=2, mode=gl.TRIANGLES)

        self.program = self.ctx.load_program(
            vertex_shader="shaders/square_vert.glsl",
            fragment_shader="shaders/square_frag.glsl"
        )
        self.program['projection_matrix'] = self.matrix

    def on_draw(self):
        self.clear()
        self.geometry.render(self.program)

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        self.zoom += -scroll_y/100
        self.matrix = [1/(40*self.zoom), 0,    0,
                       0,    1/(30*self.zoom), 0,
                       -40/(40*self.zoom),   -30/(30*self.zoom),   1]
        self.program['projection_matrix'] = self.matrix


class Noise1DWindow(arcade.Window):

    def __init__(self):
        super().__init__(800, 800, "1d noise window")
        self.octaves = 1

    def on_draw(self):
        self.clear()
        for n in range(0, 720):
            percent = n / 10
            value = noise_1d.fractal_noise(percent, (-10, 10), self.octaves, wrap=72)
            radians = math.radians(percent*5)
            x = math.cos(radians)
            y = math.sin(radians)
            arcade.draw_point(400 + x * (300 + value), 400 + y * (300 + value), arcade.color.RADICAL_RED, 1)

    def on_key_press(self, symbol: int, modifiers: int):
        self.octaves = max((self.octaves + 1) % 10, 1)


class CircleTestWindw(arcade.Window):

    def __init__(self):
        super().__init__(800, 800, "circle_test_window")

    def on_draw(self):
        self.clear()
        for x in range(-49, 50):
            for y in range(-49, 50):
                angle = math.atan2(y, x) / (2 * math.pi)
                angle += 1 if angle < 0 else 0
                dist = math.sqrt(x ** 2 + y ** 2) / 50

                if dist <= 1:
                    noise = noise_2d.noise_circular(angle, dist, 35, rad_count=35)
                    c = 127 + int(noise*255)
                    arcade.draw_point(400 + x*5, 400 + y*5, (c, c, c), 5)


class RandomWindow(arcade.Window):

    def __init__(self):
        super().__init__()
        self.program = self.ctx.load_program(vertex_shader="perlin/FullScreenVert.glsl",
                                             fragment_shader="perlin/RadialChunkGenFrag.glsl")
        self.program['Data.radius'] = default_planet_data.radius
        try:
            self.program['Data.coreGap'] = default_planet_data.core_gap
            self.program['Data.coreRadius'] = default_planet_data.core_radius
            self.program['chunkPos'] = (0, 0)
        except:
            pass

        self.to_texture = self.ctx.texture((32, 32), components=4, filter=(gl.NEAREST, gl.NEAREST))
        self.frame_buffer = self.ctx.framebuffer(color_attachments=self.to_texture)

        self.geometry = self.ctx.geometry([gl.BufferDescription(self.ctx.buffer(data=array('f',
                                                                                           (-1, -1, -1, 3, 3, -1))),
                                                                '2f', ['vertPos'])], mode=gl.TRIANGLES)
        self.frame_buffer.clear()
        self.frame_buffer.use()
        arcade.set_viewport(0, 32, 0, 32)
        self.geometry.render(self.program)
        self.use()
        self.clear()
        arcade.set_viewport(0, 800, 0, 600)

        self.image = Image.frombytes("RGBA", self.to_texture.size, bytes(self.to_texture.read()))
        self.image.save("test6.png")


def main():
    # window = MarchingWindow()
    # window = Noise1DWindow()
    # window = CircleTestWindw()
    window = RandomWindow()
    window.run()


if __name__ == '__main__':
    main()
