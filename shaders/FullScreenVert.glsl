#version 430

in vec2 vertPos;

void main() {
    gl_Position = vec4(vertPos, 0, 1);
}
