from math import *
from internal.collision import *

import pygame

class InternalRobot:
    def __init__(self, bbox_radius, speed, window):
        # position where the robot turned last (or was placed initially)
        self.last_turn_x = 0
        self.last_turn_y = 0
        # distance moved from previous turn point
        self.dist = 0
        # robot heading
        self.heading = 0
        # robot default speed (units per tick)
        self.speed = speed

        self.bbox_radius = bbox_radius
        self.pick_radius = bbox_radius * 1.7
        self.window = window
        self.collider = window.collision
        self.bbox = AABB(2*self.bbox_radius, 2*self.bbox_radius, 0, 0)

        self.curr_move = None
        self.curr_move_result = None
        self.tick = 0

        self.image = pygame.image.load("internal/field/robot.png")
        self.image_rotated = self.image # until it rotates

    def get_position(self):
        return (self.last_turn_x + self.dist * cos(self.heading),
                self.last_turn_y + self.dist * sin(self.heading))

    def forward(self, distance):
        if self.curr_move is not None:
            return False

        self.curr_move = {
            't0'    : self.tick,
            'type'  : 'forward',
            'start' : self.dist,
            'target': self.dist + distance,
            'speed' : self.speed # in case we want this variable or something
        }
        return True

    def turn(self, angle):
        if self.curr_move is not None:
            return False

        self.curr_move = {
            't0'    : self.tick,
            'type'  : 'turn',
            'start' : self.heading,
            'target': self.heading + angle,
            # ensure that the outer edge of the robot moves at the same speed as
            # when the robot moves forward
            'speed' : self.speed / (pi * self.bbox_radius)
        }
        self.last_turn_x, self.last_turn_y = self.get_position()
        self.dist = 0
        return True

    def pick(self):
        if self.curr_move is not None:
            return 0

        x, y = self.get_position()
        to_remove = []
        for rock in self.window.rocks:
            rock_rad = (rock.collider.width / 2) * 1.2
            dist = sqrt((x - rock.collider.x) ** 2 + (y - rock.collider.y) ** 2)
            if dist < self.pick_radius + rock_rad:
                to_remove.append(rock)

        for rock in to_remove:
            self.window.collision.remove_collider(rock.collider)
            self.window.rocks.remove(rock)
        return len(to_remove)

    def update_bb(self):
        self.bbox.x, self.bbox.y = self.get_position()

    def collides(self):
        self.update_bb()
        return self.collider.test(self.bbox)

    def place(self, x, y):
        prev_dist = self.dist
        prev_x = self.last_turn_x
        prev_y = self.last_turn_y

        self.dist = 0
        self.last_turn_x = x
        self.last_turn_y = y
        if self.collides():
            self.dist = prev_dist
            self.last_turn_x = prev_x
            self.last_turn_y = prev_y
            return False
        else:
            return True

    def update(self):
        if self.curr_move is not None:
            # Actually do something!
            if self.curr_move['type'] == 'forward':
                t0 = self.curr_move['t0']
                d0 = self.curr_move['start']
                tgt = self.curr_move['target']
                spd = self.curr_move['speed']

                dir = 1 if tgt >= d0 else -1

                t = self.tick - t0
                old_dist = self.dist

                self.dist = d0 + spd * t
                collision = self.collides()
                if collision is not None:
                    # oop, that's bad; jump back
                    self.dist = old_dist
                    self.curr_move = None
                    self.curr_move_result = {
                        'type': 'forward',
                        'success': False,
                        'error': 'collision',
                        'collider': collision,
                        'moved': self.dist - d0
                    }
                elif   (dir ==  1 and self.dist >= tgt) \
                    or (dir == -1 and self.dist <= tgt):
                    self.dist = tgt
                    self.curr_move = None
                    self.curr_move_result = {
                        'type': 'forward',
                        'success': True,
                        'moved': self.dist - d0
                    }
            elif self.curr_move['type'] == 'turn':
                # turns always succeed
                t0 = self.curr_move['t0']
                h0 = self.curr_move['start']
                tgt = self.curr_move['target']
                spd = self.curr_move['speed']
                # print("turn t0=%d h0=%.3f tgt=%.3f spd=%.3f t=%d" % (t0, h0, tgt, spd, self.tick))

                dir = 1 if tgt >= h0 else -1

                t = self.tick - t0
                self.heading = h0 + spd * t

                if    (dir ==  1 and self.heading >= tgt) \
                   or (dir == -1 and self.heading <= tgt):
                    self.heading = tgt
                    self.curr_move = None
                    self.curr_move_result = {
                        'type': 'turn',
                        'success': True,
                        'moved': self.heading - h0
                    }
                self.image_rotated = pygame.transform.rotate(self.image, degrees(self.heading))
            self.tick += 1
