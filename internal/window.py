import os
import random
import time
import sys

import pygame
import numpy as np

from internal.field import rock
from internal.collision import *

from internal import robot

from PIL import Image


def load_pil_image(img):
    size = img.size
    mode = img.mode
    data = img.tobytes()
    return pygame.image.fromstring(data, size, "RGBA").convert_alpha()

class InternalRock:
    def __init__(self, rock):
        self.image = load_pil_image(rock.image)
        self.collider = AABB(2*rock.radius, 2*rock.radius, 0, 0)

class MainWindow:
    DRAW_DISABLE_ROCKS    = 0x01 # don't draw rocks
    DRAW_DISABLE_BARRIERS = 0x02 # don't draw barriers
    DRAW_DISABLE_PLAYER   = 0x04 # don't draw the player
    DRAW_DISABLE_FLIP     = 0x08 # don't update the screen

    rock_radii = (12, 18, 24)

    def __init__(self):
        # initialize all the pygame modules we'll need
        pygame.display.init()
        self.width  = 720
        self.height = 720

        self.screen = pygame.display.set_mode((self.width, self.height), pygame.SCALED)
        self.field_bg = pygame.image.load("internal/field/grass.png")
        self.rocks = []

        self.collision = CollisionSet()
        self.collision.add_collider(ScreenCollider(self.width, self.height))
        # add barriers

        self.robot = robot.InternalRobot(12, 1, self.collision)
        self.rocks = []
        rock_tex = Image.open("internal/field/rock_texture.png")
        for i in range(24):
            rad = self.rock_radii[int(random.random() * len(self.rock_radii))]
            r = rock.Rock(rad, 15, rad/2, rock_tex)
            ir = InternalRock(r)

            # place the rock
            while True:
                ir.collider.x = int(random.random() * self.width - self.width/2)
                ir.collider.y = int(random.random() * self.height - self.height/2)
                collide = self.collision.test(ir.collider)
                if collide is None:
                    break
                else:
                    print("collides with %s" % collide)
            self.rocks.append(ir)
            self.collision.add_collider(ir.collider)

    def update(self, flags=0):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: sys.exit(0)

        self.screen.blit(self.field_bg, (0, 0))

        if not (flags & self.DRAW_DISABLE_ROCKS):
            for r in self.rocks:
                self.screen.blit(r.image,
                    (r.collider.l() + self.width/2, self.height/2 - r.collider.t()))
            pass
        if not (flags & self.DRAW_DISABLE_BARRIERS):
            # TODO draw barriers
            pass
        if not (flags & self.DRAW_DISABLE_PLAYER):
            # TODO draw the player
            pass

        if not (flags & self.DRAW_DISABLE_FLIP):
            pygame.display.flip()

    def get_opencv_surface(self):
        return pygame.surfarray.array2d(self.screen)

def main():
    win = MainWindow()

    frametime = 1 / 60
    while True:
        t = time.perf_counter()
        win.update()
        elapsed = time.perf_counter() - t
        if elapsed < frametime:
            time.sleep(frametime - elapsed)

if __name__ == '__main__':
    main()
