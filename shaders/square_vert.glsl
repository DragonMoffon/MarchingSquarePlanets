#version 420

uniform mat3 projection_matrix;

in vec2 in_pos;

void main() {
    gl_Position = vec4(projection_matrix*vec3(in_pos, 1), 1);
}
