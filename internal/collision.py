# brain-dead axis-aligned collision thing

from math import *
import pygame

class Collider:
    def __init__(self):
        self.info = {}
        self.parent = None

    def get_info(self):
        return info.copy()

    def test(self, other):
        """Test against an axis-aligned bounding box. Should return the actual
        collider that is intersecting ('self' for a single collider), or None
        if no colliders are intersecting.
        """
        return None

    def draw(self, surf, x0, y0):
        pass

class AABB(Collider):
    def __init__(self, w, h, x=0, y=0):
        super().__init__()
        self.width = w
        self.height = h
        self.x = x
        self.y = y
        self.info = {}

    def t(self):
        return self.y + self.height/2

    def b(self):
        return self.y - self.height/2

    def l(self):
        return self.x - self.width/2

    def r(self):
        return self.x + self.width/2

    def w(self):
        return self.width

    def h(self):
        return self.height

    def radius(self):
        return sqrt(self.width * self.width + self.height * self.height) / 2

    def test(self, other):
        if      self.r() > other.l() \
            and self.l() < other.r() \
            and self.t() > other.b() \
            and self.b() < other.t():
            return self
        return None

    def draw(self, surf, x0, y0):
        rect = pygame.Rect(x0 + self.l(), y0 - self.t(), self.width, self.height)
        pygame.draw.rect(surf, (0xff, 0x00, 0x00), rect, 1)

def aabb_from_corners(l, t, r, b):
    return AABB(r-l, t-b, (r+l)/2, (t+b)/2)

class ScreenCollider(Collider):
    def __init__(self, screen_width, screen_height):
        super().__init__()
        self.w = screen_width
        self.h = screen_height

    def test(self, other):
        # Test against an AABB specifically
        if     other.r() >  self.w/2 \
            or other.l() < -self.w/2 \
            or other.t() >  self.h/2 \
            or other.b() < -self.h/2:
            return self
        return None


class CollisionSet(Collider):
    def __init__(self):
        super().__init__()
        self.colliders = []

    def add_collider(self, collider):
        # technically colliders can have multiple parents
        # Please don't do this, though
        collider.parent = self
        self.colliders.append(collider)

    def remove_collider(self, collider):
        if collider in self.colliders:
            collider.parent = None
            self.colliders.remove(collider)

    def test(self, aabb):
        # could be optimized using quadtrees but I don't really care at this point
        for collider in self.colliders:
            colliding = collider.test(aabb)
            if colliding is not None:
                return colliding
        return None

    def draw(self, surf, x0, y0):
        for collider in self.colliders:
            collider.draw(surf, x0, y0)
