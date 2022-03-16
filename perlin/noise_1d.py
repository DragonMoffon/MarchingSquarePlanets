import math
import random


def func_maker(height_range, seed):
    random.seed(seed)
    height = random.uniform(*height_range)
    gradient = random.uniform(-1, 1)

    def func(x):
        return gradient * x + height

    return func


def generate_noise(x, height_range, *, seed=1.0, wrap=0):
    floor_x = int(math.floor(x))
    fract_x = x - floor_x

    lower_func = func_maker(height_range, floor_x * seed)
    upper_func = func_maker(height_range, (floor_x + 1) % wrap * seed) if wrap else \
        func_maker(height_range, (floor_x + 1) * seed)

    f = fract_x * fract_x * fract_x * (fract_x * (fract_x * 6 - 15) + 10)

    return lower_func(fract_x) * (1 - f) + upper_func(1 - fract_x) * f


def fractal_noise(initial_x, height_range, octaves, *, seed=1, wrap=0):
    base_noise = 0
    amplitude = 0.5
    frequency = 1
    for i in range(0, octaves):
        base_noise += generate_noise(initial_x * frequency, height_range, seed=seed * amplitude, wrap=wrap) * amplitude
        amplitude *= 0.5
        frequency *= 2
    return base_noise
