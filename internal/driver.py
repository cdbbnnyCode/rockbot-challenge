from threading import Thread
from queue import Queue
from pygame import surfarray
import time

from internal.collision import *

class Driver:
    def __init__(self, robot, screen, thread_fn, args=()):
        self.robot = robot
        self.cmd_queue = Queue(2)
        self.resp_queue = Queue(2)
        self.busy = False
        self.screenshot_req = False
        self.screenshot = None
        self.screen = screen
        self.drive_thread = Thread(target=thread_fn, args=(self,) + tuple(args), daemon=True)

    def start(self):
        self.drive_thread.start()

    def send_command(self, cmd, params):
        self.cmd_queue.put((cmd, params))

    def get_response(self, wait=False):
        if not self.resp_queue.empty() or wait:
            return self.resp_queue.get()
        return None

    def request_screenshot(self):
        self.screenshot = None
        self.screenshot_req = True
        while self.screenshot is None:
            time.sleep(0.01)
        return self.screenshot

    def update(self):
        self.busy = self.robot.curr_move is not None
        if not self.cmd_queue.empty():
            cmd, payload = self.cmd_queue.get()
            if cmd == 'fwd':
                s = self.robot.forward(payload['dist'])
                if not s:
                    self.resp_queue.put(('fwd', {'s': False, 'e': 'Already moving'}))
            elif cmd == 'turn':
                s = self.robot.turn(payload['angle'])
                if not s:
                    self.resp_queue.put(('turn', {'s': False, 'e': 'Already moving'}))
            elif cmd == 'pick':
                n = self.robot.pick()
                self.resp_queue.put(('pick', {'n': n}))
            else:
                raise ValueError("Invalid command: %s" % cmd)
        if self.robot.curr_move_result is not None:
            result = self.robot.curr_move_result
            self.robot.curr_move_result = None
            resp = None
            if result['type'] == 'forward':
                resp = {'s': result['success'], 'd': result['moved']}
                if 'error' in result:
                    resp['e'] = result['error']
                if 'collider' in result:
                    if 'rock' in result['collider'].info:
                        resp['c'] = 'rock'
                    elif isinstance(result['collider'], ScreenCollider):
                        resp['c'] = 'edge'
                    else:
                        resp['c'] = 'barrier'
                resp = ('fwd', resp) # bad code
            elif result['type'] == 'turn':
                resp = ('turn', {'s': result['success'], 'd': result['moved']})
            else:
                raise ValueError("Unknown response type: %s" % result['type'])
            self.resp_queue.put(resp)

        if self.screenshot_req:
            self.screenshot = pygame.surfarray.array3d(self.screen)
