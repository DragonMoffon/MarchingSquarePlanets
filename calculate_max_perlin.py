from math import sqrt
vectors = ((-0.70710678118, -0.70710678118), (0.70710678118, -0.70710678118),
           (-0.70710678118, 0.70710678118), (0.70710678118, 0.70710678118),
           (0, -1), (0, 1), (-1, 0), (1, 0))


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def mix(a, b, f):
    return a * (1 - f) + b * f


def normalise(a):
    length = sqrt(a[0]**2 + a[1]**2)
    return a[0]/length, a[1]/length


def calculate():
    i = 0
    data = ""
    max_corner = 0
    max_mid = 0
    for _0 in range(8):
        for _1 in range(8):
            for _2 in range(8):
                for _3 in range(8):
                    i += 1
                    vec_0 = vectors[_0]
                    vec_1 = vectors[_1]
                    vec_2 = vectors[_2]
                    vec_3 = vectors[_3]

                    c_0 = dot(vec_0, (0.70710678118, 0.70710678118))
                    c_1 = dot(vec_1, (-0.70710678118, 0.70710678118))
                    c_2 = dot(vec_2, (0.70710678118, -0.70710678118))
                    c_3 = dot(vec_3, (-0.70710678118, -0.70710678118))
                    largest = sorted([c_0, c_1, c_2, c_3])[-1]

                    if largest > max_corner:
                        max_corner = largest

                    mid = mix(
                        mix(dot(vec_0, (0.70710678118, 0.70710678118)), dot(vec_1, (-0.70710678118, 0.70710678118)), 0.5),
                        mix(dot(vec_2, (0.70710678118, -0.70710678118)), dot(vec_3, (-0.70710678118, -0.70710678118)), 0.5),
                        0.5)
                    if mid > max_mid:
                        max_mid = mid
                    data += f"mid: {mid}, b_l: {c_0}, b_r: {c_1}, t_l: {c_2}, t_r: {c_3}\n"
    data += f"largest_mid: {max_mid}, largest_corner: {max_corner}"
    with open("tests/test_2.txt", 'w') as file:
        file.write(data)


def test():
    calculate()


if __name__ == '__main__':
    test()

