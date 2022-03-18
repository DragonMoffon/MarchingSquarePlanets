from math import cos, sin, atan2, pi
import time

import arcade
from pyglet.math import Mat4, Vec2, Vec3, Vec4

import planet_gen
from singletons.chunk_gen import init

SCREEN_RESOLUTION = arcade.get_display_size()


class PlanetWindow(arcade.Window):

    def __init__(self):
        super().__init__(fullscreen=True)
        planet_gen.set_chunk_program(self.ctx)
        init(self.ctx, planet_gen.CHUNK_SIZE)

        self.shown_chunks = [planet_gen.Chunk(a, b, planet_gen.default_planet, True)
                             for a in range(-4, 4) for b in range(-4, 4)]

        self.target_pos = Vec2(800, 0)
        self.target_coords = 800, 0
        self.proj_matrix = Mat4().orthogonal_projection(*self.ctx.projection_2d, -100, 100)
        self.planet_matrix = None

        self.scale = 1

        planet_gen.set_world_seed(time.time() % 10)

        self.update_planet_matrix()

        self.p_velocity = [0, 0]

    def update_planet_matrix(self):
        view_matrix = Mat4().rotate(-atan2(self.target_pos.y, self.target_pos.x) + pi/2, Vec3(0, 0, 1))

        rotated_pos = view_matrix @ Vec4(self.target_pos.x, self.target_pos.y, 0, 1)
        translation_matrix = Mat4().translate([SCREEN_RESOLUTION[0]/2 - rotated_pos.x,
                                               SCREEN_RESOLUTION[1]/2 - rotated_pos.y, 0])

        scale = 1/self.scale
        scale_matrix = Mat4().scale([scale, scale, scale])

        self.planet_matrix = view_matrix @ translation_matrix @ self.proj_matrix @ scale_matrix

        self.ctx.projection_2d_matrix = self.planet_matrix

        planet_gen.default_planet.find_revealed_chunks(self.planet_matrix)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            self.close()
        elif symbol == arcade.key.D:
            self.p_velocity[1] -= 1
        elif symbol == arcade.key.A:
            self.p_velocity[1] += 1
        elif symbol == arcade.key.W:
            self.p_velocity[0] += 1
        elif symbol == arcade.key.S:
            self.p_velocity[0] -= 1

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.D:
            self.p_velocity[1] += 1
        elif symbol == arcade.key.A:
            self.p_velocity[1] -= 1
        elif symbol == arcade.key.W:
            self.p_velocity[0] -= 1
        elif symbol == arcade.key.S:
            self.p_velocity[0] += 1

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        self.scale = max(min(self.scale - scroll_y/10, 100), 1)
        self.update_planet_matrix()

    def on_update(self, delta_time: float):
        if self.p_velocity[0] or self.p_velocity[1]:
            self.target_coords = self.target_coords + Vec2(self.p_velocity[0]*350*delta_time,
                                                           self.p_velocity[1]*100*pi/self.target_coords[0]*delta_time)
            self.target_pos = Vec2(cos(self.target_coords[1])*self.target_coords[0],
                                   sin(self.target_coords[1])*self.target_coords[0])
            self.update_planet_matrix()

    def on_draw(self):
        self.clear()

        planet_gen.default_planet.draw()

        arcade.draw_point(self.target_pos.x, self.target_pos.y, arcade.color.RADICAL_RED, 10)


def main():
    window = PlanetWindow()
    window.run()
