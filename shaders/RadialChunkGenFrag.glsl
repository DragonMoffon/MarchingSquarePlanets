#version 430

#define Pi 3.141692

in vec4 gl_FragCoord;

out vec4 fragColor;

uniform struct PlanetData {
    int coreRadius, coreGap, radius;
} Data;

uniform vec2 chunkPos;

float smootherstep(float f){
    return f * f * f * (f * (f * 6 - 15) + 10);
}

// Less Uniform Random
float hash12(vec2 p)
{
	vec3 p3  = fract(vec3(p.xyx) * .1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

float random2(vec2 p, float key)
{
    return hash12(gl_FragCoord.xy*.304 + key*1500 + 50);
}

float random2(vec2 p)
{
    return hash12(gl_FragCoord.xy*.304 + 1500 + 50);
}


// Cool High Quality Hash Random
uint hash( uint x ) {
    x += ( x << 10u );
    x ^= ( x >>  6u );
    x += ( x <<  3u );
    x ^= ( x >> 11u );
    x += ( x << 15u );
    return x;
}

uint hash( uvec2 v ) { return hash( v.x ^ hash(v.y)                         ); }
uint hash( uvec3 v ) { return hash( v.x ^ hash(v.y) ^ hash(v.z)             ); }
uint hash( uvec4 v ) { return hash( v.x ^ hash(v.y) ^ hash(v.z) ^ hash(v.w) ); }

float floatConstruct( uint m ) {
    const uint ieeeMantissa = 0x007FFFFFu; // binary32 mantissa bitmask
    const uint ieeeOne      = 0x3F800000u; // 1.0 in IEEE binary32

    m &= ieeeMantissa;                     // Keep only mantissa bits (fractional part)
    m |= ieeeOne;                          // Add fractional part to 1.0

    float  f = uintBitsToFloat( m );       // Range [1:2]
    return f - 1.0;                        // Range [0:1]
}

// Pseudo-random value in half-open range [0:1].
float random( float x ) { return floatConstruct(hash(floatBitsToUint(x))); }
float random( vec2  v ) { return floatConstruct(hash(floatBitsToUint(v))); }
float random( vec3  v ) { return floatConstruct(hash(floatBitsToUint(v))); }
float random( vec4  v ) { return floatConstruct(hash(floatBitsToUint(v))); }


// Perlin Noise Stuff

const vec2[8] vectorChoices = {vec2(1, 0), vec2(-1, 0), vec2(0, 1), vec2(0, -1),
vec2(0.70710678118, 0.70710678118), vec2(-0.70710678118, 0.70710678118),
vec2(0.70710678118, -0.70710678118), vec2(-0.70710678118, -0.70710678118)};


vec2 pickVec(vec2 pos) {
    int index = min(int(random(pos)*8), 7);
    return vectorChoices[index];
}


float perlinNoise(float percent_dist, float percent_angle, int radius, int rad_count, int frequency){
    int mpr = rad_count*frequency;
    float dist = percent_dist * radius * frequency;
    float d_floor = floor(dist);
    float d_fract = fract(dist);

    float f_dist = smootherstep(d_fract);

    int b_mod = int(mpr * d_floor / radius);
    float angle_b = percent_angle * b_mod;
    float b_floor = floor(angle_b);
    float b_fract = fract(angle_b);

    float f_bot = smootherstep(b_fract);

    int t_mod = int(mpr * (d_floor+1) / radius);
    float angle_t = percent_angle * t_mod;
    float t_floor = floor(angle_t);
    float t_fract = fract(angle_t);

    float f_top = smootherstep(t_fract);

    vec2 b_l = pickVec(vec2(b_floor, d_floor));
    vec2 b_r;

    if (d_floor == 0) b_r = b_l;
    else if (b_floor + 1 >= b_mod) b_r = pickVec(vec2(0, d_floor));
    else b_r = pickVec(vec2(b_floor+1, d_floor));

    vec2 t_l = pickVec(vec2(t_floor, d_floor+1));
    vec2 t_r = (t_floor + 1 >= t_mod)? pickVec(vec2(0, d_floor+1)) : pickVec(vec2(t_floor+1, d_floor+1));

    float result = mix(
    mix(dot(b_l, normalize(vec2(b_fract, d_fract))),
        dot(b_r, normalize(vec2(b_fract, d_fract)-vec2(1, 0))), f_bot),
    mix(dot(t_l, normalize(vec2(t_fract, d_fract)-vec2(0, 1))),
        dot(t_r, normalize(vec2(t_fract, d_fract)-vec2(1))), f_top),
        f_dist);


    return result;
}


float fractalNoise(float dist, float angle){
    float tunnel_noise = 0, cavern_noise = 0, amplitude = 1;
    int frequency = 1;
    for (int i = 0; i < 5; i++){
        tunnel_noise += perlinNoise(dist, angle, 35, 35, frequency) * amplitude;
        cavern_noise += perlinNoise(dist, angle, 7, 70, frequency) * amplitude;
        frequency *= 2;
        amplitude *- 0.5;
    }
    const float v_range = 1.9375; // 1 + 0.5 + 0.25 + 0.125 + 0.0625
    const float dist_sqrt = sqrt(dist);

    tunnel_noise = pow((tunnel_noise/v_range * 0.5 + 0.5), 1.2)*2-1;
    cavern_noise = pow((cavern_noise/v_range * 0.5 + 0.5), 0.25+(1-dist_sqrt)*1.5)*2-1;

    return mix(cavern_noise, tunnel_noise, dist_sqrt);
}


void main() {
    vec2 pos = chunkPos + gl_FragCoord.xy;
    float angle = atan(pos.y, pos.x) / (2 * Pi);
    angle += (angle < 0? 1: 0);
    float dist = length(pos);

    float noise_val = -1;
    if (dist <= Data.coreGap){
        if (dist <= Data.coreRadius+2){
            noise_val = clamp(Data.coreRadius - dist, -1, 1);

        }
        else{
            noise_val = clamp(dist - Data.coreGap, -1, 1);
        }
    }
    else{
        if (dist <= Data.radius){
            noise_val = fractalNoise(dist/Data.radius, angle);
            if (dist >= Data.radius-1 && noise_val>0){
                noise_val = clamp(Data.radius - dist, -1, 1);
            }
        }
        else{
            noise_val = clamp(Data.radius - dist, -1, 1);
        }
    }
    noise_val += noise_val == 0.0? 0.001 : 0;
    // noise_val = isnan(noise_val)? 0: noise_val;
    fragColor = vec4(noise_val); // vec4(vec3(noise_val), 1); // vec4(noise_val*0.5+0.5, angle, dist/Data.radius, 1);
}

