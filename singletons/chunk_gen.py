from array import array
from PIL import Image
import struct

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


def generate_chunk(chunk_x, chunk_y, planet_data):
    window = arcade.get_window()
    view_port = context.viewport

    program['Data.radius'] = planet_data.radius
    program['Data.coreGap'] = planet_data.core_gap
    program['Data.coreRadius'] = planet_data.core_radius
    program['chunkPos'] = (chunk_x, chunk_y)

    writeBuffer.use()
    writeBuffer.clear((0.0, 0.0, 0.0, 0.0), normalized=True)
    geometry.render(program)
    window.use()

    data = writeTexture.read()
    stu = struct.unpack('1024f', data)
    print(stu)
    # print(len(data), data)

    test = reshape(frombuffer(writeTexture.read(), 'f4'), [CHUNK_SIZE, CHUNK_SIZE])
    # print(f"{chunk_x}, {chunk_y}:\n{test}")

    return None
