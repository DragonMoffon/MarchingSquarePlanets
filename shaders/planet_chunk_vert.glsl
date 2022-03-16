#version 420

layout (binding = 0) uniform Projection {
    mat4 matrix;
} proj;

in vec2 vertPos;

// zoom between (16, 10) to (64, 40) or maybe (128, 80)

void main() {
    gl_Position = proj.matrix * vec4(vertPos, 0, 1);
}