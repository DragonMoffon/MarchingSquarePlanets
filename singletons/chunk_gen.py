from array import array
import struct

from numpy import reshape, frombuffer, set_printoptions
import arcade
import arcade.gl as gl
from sys import maxsize

set_printoptions(threshold=maxsize, linewidth=maxsize)

context: arcade.ArcadeContext
program: gl.Program
cleanup_shader: None
mesh_gen_shader: None
geometry: gl.Geometry
writeTexture: gl.Texture
writeBuffer: gl.Framebuffer

index_data_ssbo: gl.Buffer

CHUNK_SIZE: int

INDEX_DATA = array("i", (
    -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  # 0000 - vertex count: 0 - len: 0
    0, 1, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1,  # 0001 - vertex count: 3 - len: 3
    0, 1, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1,  # 0010 - vertex count: 3 - len: 3
    0, 1, 2, 0, 2, 3, -1, -1, -1, -1, -1, -1,  # 0011 - vertex count: 4 - len: 6
    0, 2, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  # 0100 - vertex count: 3 - len: 3
    0, 2, 5, 2, 3, 4, 2, 4, 5, 1, 4, 3,  # 0101 - vertex count: 6 - len: 12
    0, 1, 3, 0, 3, 2, -1, -1, -1, -1, -1, -1,  # 0110 - vertex count: 4 - len: 6
    1, 2, 3, 1, 3, 4, 1, 4, 0, -1, -1, -1,  # 0111 - vertex count: 5 - len: 9
    0, 1, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1,  # 1000 - vertex count: 3 - len: 3
    0, 2, 3, 0, 3, 1, -1, -1, -1, -1, -1, -1,  # 1001 - vertex count: 4 - len: 6
    0, 3, 2, 2, 3, 4, 2, 4, 5, 1, 5, 4,  # 1010 - vertex count: 6 - len: 12
    0, 2, 3, 0, 3, 4, 0, 4, 2, -1, -1, -1,  # 1011 - vertex count: 5 - len: 9
    0, 1, 3, 0, 3, 2, -1, -1, -1, -1, -1, -1,  # 1100 - vertex count: 4 - len: 6
    2, 0, 3, 2, 3, 4, 2, 4, 1, -1, -1, -1,  # 1101 - vertex count: 5 - len: 9
    1, 2, 4, 1, 4, 3, 1, 3, 0, -1, -1, -1,  # 1110 - vertex count: 5 - len: 9
    0, 1, 2, 0, 2, 3, -1, -1, -1, -1, -1, -1,  # 1111 - vertex count: 4 - len: 6
))

MAX_VERTEX_COUNT = 5766
MAX_INDEX_COUNT = 11532


def init(ctx: arcade.ArcadeContext, chunk_size):
    global context, program, cleanup_shader, mesh_gen_shader, geometry, writeTexture, \
            writeBuffer, CHUNK_SIZE, index_data_ssbo
    context = ctx
    CHUNK_SIZE = chunk_size

    program = ctx.load_program(vertex_shader="shaders/FullScreenVert.glsl",
                               fragment_shader="shaders/RadialChunkGenFrag.glsl")
    cleanup_shader = ctx.load_compute_shader("shaders/Cleanup_Compute_shader.glsl")
    mesh_gen_shader = ctx.load_compute_shader("shaders/Vertex_Gen_Comp.glsl")

    geometry = ctx.geometry([gl.BufferDescription(ctx.buffer(data=array('f', [-1, -1, -1, 3, 3, -1])),
                                                  '2f', ['vertPos'])], mode=gl.TRIANGLES)
    writeTexture = ctx.texture((CHUNK_SIZE, CHUNK_SIZE), components=1, dtype='f4', filter=(gl.NEAREST, gl.NEAREST),
                               wrap_x=gl.CLAMP_TO_EDGE, wrap_y=gl.CLAMP_TO_EDGE)
    writeBuffer = ctx.framebuffer(color_attachments=writeTexture)
    writeBuffer.viewport = 0, 0, CHUNK_SIZE, CHUNK_SIZE

    index_data_ssbo = ctx.buffer(data=INDEX_DATA)


def generate_chunk(chunk_x, chunk_y, planet_data, debug):
    window = arcade.get_window()

    # program['Data.radius'] = planet_data.radius
    # program['Data.coreGap'] = planet_data.core_gap
    # program['Data.coreRadius'] = planet_data.core_radius
    # program['chunkPos'] = (chunk_x, chunk_y)

    context.disable(context.BLEND)
    writeBuffer.use()
    writeBuffer.clear()
    geometry.render(program)
    writeTexture.bind_to_image(0)
    cleanup_shader.run(group_x=1, group_y=1, group_z=1)
    window.use()

    vertex_ssbo = window.ctx.buffer(reserve=MAX_VERTEX_COUNT*8+4)
    # 4 bytes per 32-bit float, 2 floats per vertex, plus 4 for 32-bit count integer
    index_ssbo = window.ctx.buffer(reserve=MAX_INDEX_COUNT*4+4)
    # 4 bytes per 32-bit integer, 1 int per index, plus 4 for 32-bit count integer

    writeTexture.bind_to_image(0, read=True, write=False)
    mesh_gen_shader['chunkPos'] = chunk_x, chunk_y

    index_ssbo.bind_to_storage_buffer(binding=0)
    vertex_ssbo.bind_to_storage_buffer(binding=1)
    index_data_ssbo.bind_to_storage_buffer(binding=2)

    mesh_gen_shader.run(group_x=1, group_y=1, group_z=1)

    index_count = int.from_bytes(index_ssbo.read(4), "little")*4
    index_buffer = window.ctx.buffer(data=index_ssbo.read(index_count, 4)) if index_count else None

    vertex_count = int.from_bytes(vertex_ssbo.read(4), 'little')*8
    vertex_buffer = window.ctx.buffer(data=vertex_ssbo.read(vertex_count, 8)) if vertex_count else None

    density_map = reshape(frombuffer(writeTexture.read(), 'f'), [CHUNK_SIZE, CHUNK_SIZE]).transpose()

    if debug:
        print(density_map)
        if index_buffer is not None:
            print(frombuffer(index_buffer.read(), 'i'))
        if vertex_buffer is not None:
            print(frombuffer(vertex_buffer.read(), 'f'))
        for i in range(int.from_bytes(index_ssbo.read(4), "little")):
            index = int.from_bytes(index_ssbo.read(4, 4+i*4), 'little')
            print(index)
            vertex = struct.unpack('2f', vertex_ssbo.read(8, 8+index*8))
            print(f"{index} : {vertex}")

        print(index_count, vertex_count)

    # print(chunk_x, chunk_y, f"\n{buffer}")
    return density_map, vertex_buffer, index_buffer
