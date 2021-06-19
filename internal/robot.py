from math import *
from internal.collision import *

class InternalRobot:
    def __init__(self, bbox_radius, speed, collider):
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
        self.collider = collider

        self.curr_move = None
        self.curr_move_result = None
        self.tick = 0

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
            'speed' : self.speed / (2 * pi * self.bbox_radius)
        }
        self.last_turn_x, self.last_turn_y = self.get_position()
        return True

    def collides(self, x, y):
        target_bb = AABB(2*self.bbox_radius, 2*self.bbox_radius, x, y)
        return self.collider.test(target_bb)

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
                collision = self.collides(*self.get_position())
                if collision is not None:
                    # oop, that's bad; jump back
                    self.dist = old_dist
                    self.curr_move = None
                    self.curr_move_result = {
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
                        'success': True,
                        'moved': self.dist - d0
                    }
            elif self.curr_move['type'] == 'turn':
                # turns always succeed
                t0 = self.curr_move['t0']
                h0 = self.curr_move['start']
                tgt = self.curr_move['target']
                spd = self.curr_move['speed']

                dir = 1 if h0 >= tgt else -1

                t = self.tick - t0
                self.heading = h0 + spd * t

                if    (dir ==  1 and self.heading >= tgt) \
                   or (dir == -1 and self.heading <= tgt):
                    self.heading = tgt
                    self.curr_move = None
                    self.curr_move_result = {
                        'success': True,
                        'moved': self.heading - h0
                    }
