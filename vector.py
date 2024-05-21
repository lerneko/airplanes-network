import math
import pyray as pr

class Vec2d:
    def __repr__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"
    
    def __format__(self, format_spec):
        return f"({self.x:{format_spec}}, {self.y:{format_spec}})"

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, point):
        return Vec2d(self.x + point.x, self.y + point.y)

    def __sub__(self, point):
        return Vec2d(self.x - point.x, self.y - point.y)

    def __mul__(self, num):
        return Vec2d(num * self.x, num * self.y)

    def __rmul__(self, num):
        return self.__mul__(num)
    
    def __neg__(self):
        return Vec2d(-self.x, -self.y)

    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)
    def normalize(self):
        length = self.length()
        if length == 0:
            return Vec2d(0, 0)  # Return a zero vector if the length is 0
        else:
            return Vec2d(self.x / length, self.y / length)
        
    def Vector2(self):
        return pr.Vector2(self.x, self.y)