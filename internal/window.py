import os
import random
import time
import sys
import math

import pygame
import numpy as np

from internal.field import rock
from internal.collision import *
from internal.driver import Driver

from internal import robot
from external import robot as robot_ex

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
        self.collider.info = {'rock': self}

def thread_fn(driver, robot_fn):
    rbt = robot_ex.Robot(driver)
    robot_fn(rbt)

class MainWindow:
    DRAW_DISABLE_ROCKS    = 0x01 # don't draw rocks
    DRAW_DISABLE_BARRIERS = 0x02 # don't draw barriers
    DRAW_DISABLE_PLAYER   = 0x04 # don't draw the player
    DRAW_DISABLE_FLIP     = 0x08 # don't update the screen

    rock_radii = (12, 16, 20)

    def __init__(self, robot_fn):
        # initialize all the pygame modules we'll need
        pygame.display.init()
        self.width  = 720
        self.height = 720

        self.screen = pygame.display.set_mode((self.width, self.height), pygame.SCALED)
        self.field_bg = pygame.image.load("internal/field/grass.png")
        self.rocks = []

        self.collision = CollisionSet()
        self.collision.add_collider(ScreenCollider(self.width, self.height))
        # add barriers here

        # bounding_boxes = [
        # #              left top right bottom
        # (0, 110, 528, 160),
        # (189, 320, 720, 375),
        # (0, 543, 529, 595)
        # ]

        self.collision.add_collider(aabb_from_corners(-360, 250,  168, 200))
        self.collision.add_collider(aabb_from_corners(-171, 40,   360, -15))
        self.collision.add_collider(aabb_from_corners(-360, -183, 169, -235))

        self.robot = robot.InternalRobot(20, 2, self)
        self.driver = Driver(self.robot, self.screen, thread_fn, (robot_fn,))

        # set start position
        robot_start_x = 0
        robot_start_y = 100
        if not self.robot.place(robot_start_x, robot_start_y):
            raise ValueError("Can't place robot at (%.3f, %.3f)" % \
                        (robot_start_x, robot_start_y))

        # temporarily add the robot collider so we don't put rocks on top of it
        # We'll remove it after we're done so the robot doesn't have problems
        # colliding with itself
        self.robot.update_bb()
        self.collision.add_collider(self.robot.bbox)
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
        self.collision.remove_collider(self.robot.bbox)

    def start(self):
        self.driver.start()

    def update(self, flags=0):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: sys.exit(0)

        self.driver.update()
        self.robot.update()
        self.screen.blit(self.field_bg, (0, 0))

        if not (flags & self.DRAW_DISABLE_ROCKS):
            for r in self.rocks:
                self.screen.blit(r.image,
                    (r.collider.l() + self.width/2, self.height/2 - r.collider.t()))
        if not (flags & self.DRAW_DISABLE_PLAYER):
            rotated = self.robot.image_rotated
            rx, ry = self.robot.get_position()
            x = self.width/2 + rx - rotated.get_width()/2
            y = self.height/2 - ry - rotated.get_height()/2
            self.screen.blit(rotated, (x, y))
        if not (flags & self.DRAW_DISABLE_BARRIERS):
            # TODO draw barriers
            self.collision.draw(self.screen, self.width/2, self.height/2)
            self.robot.bbox.draw(self.screen, self.width/2, self.height/2)
            rx, ry = self.robot.get_position()

            pygame.draw.circle(self.screen, (0x00, 0xff, 0x00),
                        (self.width/2 + rx, self.height/2 - ry), int(self.robot.pick_radius), 1)
            for rock in self.rocks:
                pygame.draw.circle(self.screen, (0x00, 0xff, 0xff),
                        (self.width/2 + rock.collider.x, self.height/2 - rock.collider.y),
                        int((rock.collider.width/2) * 1.2) , 1)

        if not (flags & self.DRAW_DISABLE_FLIP):
            pygame.display.flip()

    def get_opencv_surface(self):
        return pygame.surfarray.array2d(self.screen)

def main(robot_fn):
    win = MainWindow(robot_fn)
    win.start()

    frametime = 1 / 60
    # win.robot.forward(250)
    while True:
        t = time.perf_counter()
        win.update()

        # if win.robot.curr_move_result is not None:
        #     print(win.robot.curr_move_result)
        #     win.robot.curr_move_result = None
        #     win.robot.pick()
        elapsed = time.perf_counter() - t
        if elapsed < frametime:
            time.sleep(frametime - elapsed)

if __name__ == '__main__':
    main()
