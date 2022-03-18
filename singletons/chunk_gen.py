from array import array

from numpy import reshape, frombuffer
import arcade
import arcade.gl as gl

context: arcade.ArcadeContext
program: gl.Program
geometry: gl.Geometry
writeTexture: gl.Texture
writeBuffer: gl.Framebuffer

CHUNK_SIZE: int


def init(ctx: arcade.ArcadeContext, chunk_size):
    global context, program, geometry, writeTexture, writeBuffer, CHUNK_SIZE
    context = ctx
    CHUNK_SIZE = chunk_size

    program = ctx.load_program(vertex_shader="shaders/FullScreenVert.glsl",
                               fragment_shader="shaders/RadialChunkGenFrag.glsl")

    geometry = ctx.geometry([gl.BufferDescription(ctx.buffer(data=array('f', [-1, -1, -1, 3, 3, -1])),
                                                  '2f', ['vertPos'])], mode=gl.TRIANGLES)
    writeTexture = ctx.texture((CHUNK_SIZE, CHUNK_SIZE), components=1, dtype='f4', filter=(gl.NEAREST, gl.NEAREST))
    writeBuffer = ctx.framebuffer(color_attachments=writeTexture)
    writeBuffer.viewport = 0, 0, CHUNK_SIZE, CHUNK_SIZE


def generate_chunk(chunk_x, chunk_y, planet_data):
    window = arcade.get_window()

    # program['Data.radius'] = planet_data.radius
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

    def on_draw(self):
        program['Data.radius'] = 729
        program['Data.coreGap'] = 44
        program['Data.coreRadius'] = 22
        program['chunkPos'] = (0, 0)

        geometry.render(program)


def main():
    window = Window()
    window.run()


if __name__ == '__main__':
    main()
