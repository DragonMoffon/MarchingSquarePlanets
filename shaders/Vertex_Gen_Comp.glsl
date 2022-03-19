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
    int shape[16][12];
}iters;

void main() {
    ivec2 id_pos = ivec2(gl_LocalInvocationID.xy);
    vec2 pos = vec2(chunkPos + id_pos);
    float b_l = imageLoad(denistyTex, id_pos).x;
    float b_r = imageLoad(denistyTex, id_pos+ivec2(1, 0)).x;
    float t_l = imageLoad(denistyTex, id_pos+ivec2(0, 1)).x;
    float t_r = imageLoad(denistyTex, id_pos+ivec2(1, 1)).x;

    int iteration_combination = int(ceil(b_l)) | int(ceil(t_l))<<1 | int(ceil(t_r))<<2 | int(ceil(b_r))<<3;

    int vertex_count = 0;

    vec2 v_0 = b_l <= 0? INVALID: pos * SQUARESIZE;
    vec2 v_1 = t_l <= 0? INVALID: (pos + vec2(0, 1)) * SQUARESIZE;
    vec2 v_2 = t_r <= 0? INVALID: (pos + vec2(1, 1)) * SQUARESIZE;
    vec2 v_3 = b_r <= 0? INVALID: (pos + vec2(1, 0)) * SQUARESIZE;

    vertex_count += int(!isinf(v_0.x)) + int(!isinf(v_1.x)) + int(!isinf(v_2.x)) + int(!isinf(v_3.x));

    if (vertex_count != 0)
    {
        vec2 v_4 = b_l*t_l > 0? INVALID: (pos + vec2(0, abs(b_l) / (abs(b_l) + abs(t_l)))) * SQUARESIZE;
        vec2 v_5 = t_l*t_r > 0? INVALID: (pos + vec2(abs(t_l) / (abs(t_l) + abs(t_r)), 1)) * SQUARESIZE;
        vec2 v_6 = b_r*t_r > 0? INVALID: (pos + vec2(1, abs(b_r) / (abs(b_r) + abs(t_r)))) * SQUARESIZE;
        vec2 v_7 = b_l*b_r > 0? INVALID: (pos + vec2(abs(b_l) / (abs(b_l) + abs(b_r), 0))) * SQUARESIZE;

        vertex_count += int(!isinf(v_4.x)) + int(!isinf(v_5.x)) + int(!isinf(v_6.x)) + int(!isinf(v_7.x));


        int vertexStart = atomicAdd(vertexBuffer.count, vertex_count);
        vertex_count = 0;
        if (!isinf(v_0.x)) { vertexBuffer.vertexPos[vertexStart+vertex_count] = v_0; vertex_count += 1; }
        if (!isinf(v_1.x)) { vertexBuffer.vertexPos[vertexStart+vertex_count] = v_1; vertex_count += 1; }
        if (!isinf(v_2.x)) { vertexBuffer.vertexPos[vertexStart+vertex_count] = v_2; vertex_count += 1; }
        if (!isinf(v_3.x)) { vertexBuffer.vertexPos[vertexStart+vertex_count] = v_3; vertex_count += 1; }
        if (!isinf(v_4.x)) { vertexBuffer.vertexPos[vertexStart+vertex_count] = v_4; vertex_count += 1; }
        if (!isinf(v_5.x)) { vertexBuffer.vertexPos[vertexStart+vertex_count] = v_5; vertex_count += 1; }
        if (!isinf(v_6.x)) { vertexBuffer.vertexPos[vertexStart+vertex_count] = v_6; vertex_count += 1; }
        if (!isinf(v_7.x)) { vertexBuffer.vertexPos[vertexStart+vertex_count] = v_7; vertex_count += 1; }

        int indexCount = 3  + (vertex_count-3) * 3;
        int indexStart = atomicAdd(indexBuffer.count, indexCount);
        int defaultIndicies[12] = iters.shape[iteration_combination];
        for (int i = 0; i < 12; i++){
            if (defaultIndicies[i] != -1)
            {
                indexBuffer.indices[indexStart+i] = vertexStart + defaultIndicies[i];
            }
        }
    }
}