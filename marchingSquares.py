from math import ceil, floor

BOX_SIZE = 60

INDICES = {(1, -1, -1, -1): (0, 4, 7), (-1, 1, -1, -1): (1,  5, 4),
            (-1, -1, 1, -1): (2, 6, 5), (-1, -1, -1, 1): (3, 7, 6),
            (1, 1, 1, -1): (1, 7, 0, 1, 6, 7, 1, 2, 6),
            (1, 1, -1, 1): (0, 1, 5, 0, 5, 6, 0, 6, 3),
            (1, -1, 1, 1): (3, 0, 4, 3, 4, 5, 3, 5, 2),
            (-1, 1, 1, 1): (2, 4, 1, 2, 7, 4, 2, 3, 7),
            (1, 1, -1, -1): (0, 1, 5, 0, 5, 7),
            (-1, -1, 1, 1): (7, 5, 2, 7, 2, 3),
            (-1, 1, 1, -1): (4, 1, 2, 4, 2, 6),
            (1, -1, -1, 1): (0, 4, 6, 0, 6, 3),
            (1, -1, 1, -1): (0, 4, 7, 4, 5, 6, 4, 6, 7, 5, 2, 6),
            (-1, 1, -1, 1): (1, 5, 4, 4, 5, 6, 4, 6, 7, 6, 3, 7),
            (1, 1, 1, 1): (0, 1, 2, 0, 2, 3),
            (-1, -1, -1, -1): ()}

EDGE_VALUES = {(1, -1, -1, -1): (1.0, 0.0, 0.0, 1.0), (-1, 1, -1, -1): (1.0, 1.0, 0.0, 0.0),
               (-1, -1, 1, -1): (0.0, 1.0, 1.0, 0.0), (-1, -1, -1, 1): (0.0, 0.0, 1.0, 1.0),
               (1, 1, 1, -1): (0.0, 0.0, 1.0, 1.0), (1, 1, -1, 1): (0.0, 1.0, 1.0, 0.0),
               (1, -1, 1, 1): (1.0, 1.0, 0.0, 0.0), (-1, 1, 1, 1): (1.0, 0.0, 0.0, 1.0),
               (1, 1, -1, -1): (0.0, 1.0, 0.0, 1.0), (-1, -1, 1, 1): (0.0, 1.0, 0.0, 1.0),
               (-1, 1, 1, -1): (1.0, 0.0, 1.0, 0.0), (1, -1, -1, 1): (1.0, 0.0, 1.0, 0.0),
               (1, -1, 1, -1): (1.0, 1.0, 1.0, 1.0), (-1, 1, -1, 1): (1.0, 1.0, 1.0, 1.0),
               (1, 1, 1, 1): (0.0, 0.0, 0.0, 0.0), (-1, -1, -1, -1): (0.0, 0.0, 0.0, 0.0)}


def roof(x):
    return ceil(x) if x > 0 else floor(x)


def get_indices(values):
    """
    Returns the index list for the necessary marching Square combination.
     Indices 0-3 are the major points 4-7 are the half points starting from the bottom left.
    """
    check = tuple(roof(n) for n in values)
    return INDICES.get(check, ())


def find_mid_point(a, b, base_x, base_y, edge):
    """
    Using the values of the two major point which are between (-1 and 1) find where the midpoint should lie
    """
    if base_x <= 16 and base_y <= 16:
        shift = abs(a) / (abs(a)+abs(b))
    else:
        shift = 0.15 + abs(a) / (abs(a)+abs(b)) * 0.7
    if edge == 0: return base_x * BOX_SIZE, (base_y + shift) * BOX_SIZE
    elif edge == 1: return (base_x + shift) * BOX_SIZE, (base_y + 1) * BOX_SIZE
    elif edge == 2: return (base_x + 1) * BOX_SIZE, (base_y + shift) * BOX_SIZE
    elif edge == 3: return (base_x + shift) * BOX_SIZE, base_y * BOX_SIZE


def gen_vertices(values, base_x, base_y):
    """
    create the vertex data for each vertex. This includes data which may not be used. As such it needs to be cleaned
    """
    v_0, v_1, v_2, v_3 = ((base_x * BOX_SIZE, base_y * BOX_SIZE),
                          (base_x * BOX_SIZE, (base_y+1) * BOX_SIZE),
                          ((base_x+1) * BOX_SIZE, (base_y+1) * BOX_SIZE),
                          ((base_x+1) * BOX_SIZE, base_y * BOX_SIZE))

    v_4 = find_mid_point(values[0], values[1], base_x, base_y, 0)
    v_5 = find_mid_point(values[1], values[2], base_x, base_y, 1)
    v_6 = find_mid_point(values[3], values[2], base_x, base_y, 2)
    v_7 = find_mid_point(values[0], values[3], base_x, base_y, 3)

    return v_0, v_1, v_2, v_3, v_4, v_5, v_6, v_7


def clean_data(indices, vertices, index_start):
    """
    Since gen_vertices() calculates all vertices but not all of them will be used so it discards the unused vertices and
    adjusts the index. (it also flattens the vertices since those are return as a tuple of tuples).
    """
    index_check = sorted(set(indices))
    index_shift = {x: index_check.index(x)+index_start for x in index_check}
    new_indices = tuple(index_shift[n] for n in indices)
    new_vertices = tuple(n for v in vertices if vertices.index(v) in index_shift for n in v)

    return new_indices, new_vertices


def gen_square(values, base_x, base_y, index_start):
    return clean_data(get_indices(values), gen_vertices(values, base_x, base_y), index_start)
