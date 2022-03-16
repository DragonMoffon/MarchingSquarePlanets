import math
import random

vectors = ((-0.70710678118, -0.70710678118), (0.70710678118, -0.70710678118),
           (-0.70710678118, 0.70710678118), (0.70710678118, 0.70710678118),
           (0, -1), (0, 1), (-1, 0), (1, 0))


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def normalise(x, y):
    length = math.sqrt(x**2 + y**2)
    length = length if length else 1
    return x/length, y/length


def mix(a, b, f):
    return a * (1 - f) + b * f


def smoother_step(f):
    return f * f * f * (f * (f * 6 - 15) + 10)


def remap_to_threshold(v, threshold=0.0):
    norm = v - threshold
    norm /= max(1 + (threshold if norm < 0 else -threshold), 0.001)
    return norm + 0.001 if norm == 0 else norm


def get_rand_vec(x, y, seed=1):
    random.seed(x*seed + y / (100*seed))
    return random.choice(vectors)


def noise_circular(percent_angle, percent_dist, radius, *, seed=1, frequency=1, rad_count=50):
    mpr = rad_count * frequency
    dist = radius * percent_dist * frequency
    floor_dist = math.floor(dist)
    fract_dist = dist - math.floor(dist)

    f_vert = smoother_step(fract_dist)

    bottom_angle = percent_angle * int(mpr * floor_dist / radius)
    floor_bottom = math.floor(bottom_angle)
    fract_bottom = bottom_angle - floor_bottom

    f_bot = smoother_step(fract_bottom)

    top_angle = percent_angle * int(mpr * (floor_dist + 1) / radius)
    floor_top = math.floor(top_angle)
    fract_top = top_angle - floor_top

    f_top = smoother_step(fract_top)

    vec_1 = get_rand_vec(floor_bottom, floor_dist, seed)
    if floor_bottom != 0:
        mod = int(mpr * floor_dist / radius)
        vec_2 = get_rand_vec((floor_bottom + 1) % mod, floor_dist, seed)
    else:
        vec_2 = get_rand_vec(floor_bottom, floor_dist, seed)
    vec_3 = get_rand_vec(floor_top, (floor_dist + 1))
    mod = int(mpr * (floor_dist+1) / radius)
    vec_4 = get_rand_vec((floor_top + 1) % mod, (floor_dist + 1), seed)

    result = mix(
        mix(dot(vec_1, normalise(fract_bottom, fract_dist)),
            dot(vec_2, normalise(fract_bottom - 1, fract_dist)), f_bot),
        mix(dot(vec_3, normalise(fract_top, fract_dist - 1)),
            dot(vec_4, normalise(fract_top - 1, fract_dist - 1)), f_top), f_vert)

    noise_circular.avg.append(result)

    if result > noise_circular.largest:
        noise_circular.largest = result
    elif result < noise_circular.smallest:
        noise_circular.smallest = result

    # print(f"avg: {sum(noise_circular.avg) / len(noise_circular.avg)}\n"
    #       f"Result: {result}, smallest: {noise_circular.smallest}, largest: {noise_circular.largest}")

    return result


noise_circular.avg = []
noise_circular.largest = 0
noise_circular.smallest = 0


def fractal_circular(percent_angle, percent_dist, radius, octaves, *, seed=1):
    tunnel_noise = 0
    cavern_noise = 0
    amplitude = 1
    frequency = 1
    for i in range(octaves):
        tunnel_noise += noise_circular(percent_angle, percent_dist, radius,
                                       frequency=frequency, seed=seed, rad_count=radius) * amplitude
        cavern_noise += noise_circular(percent_angle, percent_dist, radius//5,
                                       frequency=frequency, rad_count=radius//5*10) * amplitude
        frequency *= 2
        amplitude *= 0.5
    # tunnel_noise = remap_to_threshold(tunnel_noise, 0.7)
    # cavern_noise = remap_to_threshold(cavern_noise, 0.99)
    v_range = sum(1/(2**i) for i in range(octaves))

    tunnel_noise /= v_range
    tunnel_noise = ((tunnel_noise*0.5+0.5)**1.2)*2-1

    cavern_noise /= v_range
    cavern_noise = ((cavern_noise*0.5+0.5)**(0.25+(1-math.sqrt(percent_dist))*1.5))*2-1

    result = mix(cavern_noise, tunnel_noise, math.sqrt(percent_dist))

    fractal_circular.avg.append(tunnel_noise)

    if tunnel_noise > fractal_circular.largest:
        fractal_circular.largest = tunnel_noise
    elif tunnel_noise < fractal_circular.smallest:
        fractal_circular.smallest = tunnel_noise

    # print(f"avg: {sum(fractal_circular.avg) / len(fractal_circular.avg)}\n"
    #       f"Result: {tunnel_noise}, smallest: {fractal_circular.smallest}, largest: {fractal_circular.largest}")

    return result


fractal_circular.avg = []
fractal_circular.largest = 0
fractal_circular.smallest = 0
