#version 430

# define SQUARESIZE 60
# define INVALID vec2(1.0/0.0)

layout (local_size_x = 31, local_size_y=31) in;

layout (r32f, location=0) uniform image2D denistyTex;

layout (location=1) uniform ivec2 chunkPos;

layout(std430, binding = 0) buffer IndexBuffer
{
    int count;
    int indices[];
} indexBuffer;

layout(std430, binding = 1) buffer VertexBuffer
{
    int count;
    vec2 vertexPos[];
} vertexBuffer;


layout(std430, binding = 2) buffer marchBuffer
{
    int shape[192];
}iters;

void main() {
    ivec2 id_pos = ivec2(gl_LocalInvocationID.xy);
    vec2 pos = vec2(chunkPos + id_pos);
    float b_l = imageLoad(denistyTex, id_pos).x;
    float b_r = imageLoad(denistyTex, id_pos+ivec2(1, 0)).x;
    float t_l = imageLoad(denistyTex, id_pos+ivec2(0, 1)).x;
    float t_r = imageLoad(denistyTex, id_pos+ivec2(1, 1)).x;


    if (b_l >= 0 || b_r >= 0 || t_l >= 0 || t_r >= 0)
    {
        int vertex_count = (int(b_l >= 0) + int(t_l >= 0) + int(t_r >= 0) + int(b_r >= 0) +
                            int(b_l*t_l <= 0) + int(t_l*t_r <= 0) + int(b_r*t_r <= 0) + int(b_r*b_l <= 0));
        int vertexStart = atomicAdd(vertexBuffer.count, vertex_count);
        vertex_count = 0;
        if (b_l >= 0) { vertexBuffer.vertexPos[vertexStart+vertex_count] = pos * SQUARESIZE; vertex_count += 1; }
        if (t_l >= 0) { vertexBuffer.vertexPos[vertexStart+vertex_count] = (pos + vec2(0, 1)) * SQUARESIZE; vertex_count += 1; }
        if (t_r >= 0) { vertexBuffer.vertexPos[vertexStart+vertex_count] = (pos + vec2(1, 1)) * SQUARESIZE; vertex_count += 1; }
        if (b_r >= 0) { vertexBuffer.vertexPos[vertexStart+vertex_count] = (pos + vec2(1, 0)) * SQUARESIZE; vertex_count += 1; }
        if (b_l*t_l <= 0) { vertexBuffer.vertexPos[vertexStart+vertex_count] = (pos + vec2(0, abs(b_l) / (abs(b_l) + abs(t_l)))) * SQUARESIZE; vertex_count += 1; }
        if (t_l*t_r <= 0) { vertexBuffer.vertexPos[vertexStart+vertex_count] = (pos + vec2(abs(t_l) / (abs(t_l) + abs(t_r)), 1)) * SQUARESIZE; vertex_count += 1; }
        if (b_r*t_r <= 0) { vertexBuffer.vertexPos[vertexStart+vertex_count] = (pos + vec2(1, abs(b_r) / (abs(b_r) + abs(t_r)))) * SQUARESIZE; vertex_count += 1; }
        if (b_r*b_l <= 0) { vertexBuffer.vertexPos[vertexStart+vertex_count] = (pos + vec2(abs(b_l) / (abs(b_l) + abs(b_r), 0))) * SQUARESIZE; vertex_count += 1; }

        int indexCount = 3  + (vertex_count-3) * 3;
        int indexStart = atomicAdd(indexBuffer.count, indexCount);
        int iteration_combination = int(b_l>0) | int(t_l>0)<<1 | int(t_r>0)<<2 | int(b_r>0)<<3;
        int defaultIndicies = iteration_combination*12;
        for (int i = 0; i < indexCount; i++){
            indexBuffer.indices[indexStart+i] = vertexStart+iters.shape[defaultIndicies+i];
        }
    }
}