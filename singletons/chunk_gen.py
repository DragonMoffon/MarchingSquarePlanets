from array import array

from numpy import reshape, frombuffer, set_printoptions
import arcade
import arcade.gl as gl
from sys import maxsize

set_printoptions(threshold=maxsize)


context: arcade.ArcadeContext
program: gl.Program
geometry: gl.Geometry
writeTexture: gl.Texture
writeBuffer: gl.Framebuffer

CHUNK_SIZE: int


class PlanetData:

    def __init__(self, core_radius: int, core_gap: int, chunk_radius: int):
        self.core_radius = core_radius
        self.core_gap = core_gap
        self.chunk_radius = chunk_radius
        self.radius = (self.chunk_radius-1) * (CHUNK_SIZE-1) + CHUNK_SIZE//2


default_planet_data: PlanetData


def init(ctx: arcade.ArcadeContext, chunk_size):
    global context, program, geometry, writeTexture, writeBuffer, CHUNK_SIZE, default_planet_data
    context = ctx
    CHUNK_SIZE = chunk_size
    default_planet_data = PlanetData(24, 48, 24)

    program = ctx.load_program(vertex_shader="shaders/FullScreenVert.glsl",
                               fragment_shader="shaders/RadialChunkGenFrag.glsl")

    geometry = ctx.geometry([gl.BufferDescription(ctx.buffer(data=array('f', [-1, -1, -1, 3, 3, -1])),
                                                  '2f', ['vertPos'])], mode=gl.TRIANGLES)
    writeTexture = ctx.texture((CHUNK_SIZE, CHUNK_SIZE), components=1, dtype='f4', filter=(gl.NEAREST, gl.NEAREST))
    writeBuffer = ctx.framebuffer(color_attachments=writeTexture)
    writeBuffer.viewport = 0, 0, CHUNK_SIZE, CHUNK_SIZE


def generate_chunk(chunk_x, chunk_y, planet_data):
    window = arcade.get_window()

    program['Data.radius'] = planet_data.radius
    program['Data.coreGap'] = planet_data.core_gap
    program['Data.coreRadius'] = planet_data.core_radius
    program['chunkPos'] = (chunk_x, chunk_y)

    # program['radius'] = planet_data.radius

    writeBuffer.use()
    writeBuffer.clear()
    geometry.render(program)
    window.use()

    buffer = reshape(frombuffer(writeTexture.read(), 'f4'), [CHUNK_SIZE, CHUNK_SIZE])
    print(buffer)

    return buffer


class Window(arcade.Window):

    def __init__(self):
        super().__init__(32, 32)
        init(self.ctx, 32)

        generate_chunk(0, 0, default_planet_data)

    def on_draw(self):
        program['Data.radius'] = default_planet_data.radius
        program['Data.coreGap'] = default_planet_data.core_gap
        program['Data.coreRadius'] = default_planet_data.core_radius
        program['chunkPos'] = (0, 0)

        geometry.render(program)


def main():
    window = Window()
    window.run()


if __name__ == '__main__':
    main()
