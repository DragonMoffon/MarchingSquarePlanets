#version 430

layout (local_size_x = 32, local_size_y = 32) in;

layout(r32f, location=0) uniform image2D destTex;


float loner(ivec2 texelPos){
    float point = imageLoad(destTex, texelPos).r;

    float v_1 = imageLoad(destTex, texelPos+ivec2(-1, -1)).r;
    float v_2 = imageLoad(destTex, texelPos+ivec2(0, -1)).r;
    float v_3 = imageLoad(destTex, texelPos+ivec2(1, -1)).r;
    float v_4 = imageLoad(destTex, texelPos+ivec2(-1, 0)).r;
    float v_5 = imageLoad(destTex, texelPos+ivec2(1, 0)).r;
    float v_6 = imageLoad(destTex, texelPos+ivec2(-1, 1)).r;
    float v_7 = imageLoad(destTex, texelPos+ivec2(0, 1)).r;
    float v_8 = imageLoad(destTex, texelPos+ivec2(1, 1)).r;
    float total = (ceil(v_1)+ceil(v_2)+ceil(v_3)+ceil(v_4)+ceil(v_5)+ceil(v_6)+ceil(v_7)+ceil(v_8)) * 2 - 8;
    float avg = (v_1 + v_2 + v_3 + v_4 + v_5 + v_6 + v_7 + v_8) / 8;

    if ((point > 0 && total <= -8) || (point < 0 && total >= 8)){
        return avg;
    }
    return point;
}


void main() {
    ivec2 texelPos = ivec2(gl_GlobalInvocationID.xy);
    float result = loner(texelPos);

    imageStore(destTex, texelPos, vec4(result));
}
