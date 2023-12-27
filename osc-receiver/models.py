import global_data
import math


class Effect():

    def __init__(self, name, level):
        self.name = name
        self.level = level


class LaserPoint():

    def __init__(self, x, y):
        self.x = x
        self.y = y
        
        self.r = 0
        self.g = 100
        self.b = 0

    def set_color(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def is_blank(self):
        if self.r == 0 and self.g == 0 and self.b == 0:
            return True
        else:
            return False

    def __str__(self):
        return ('X:' + str(self.x) + ', Y:' + str(self.y) + ', R:' + str(self.r) + ', G:' + str(self.g) + ', B:' + str(self.b) + ', Blank: ' + str(self.is_blank()))


# TODO: make it an interface
class LaserObject():
    # every interface implementation must provide these attributes:
    # - group
    # - point_list
    # - effects

    def has_effect(self, effect_name) -> bool:
        for effect in self.effects:
            if effect.name == effect_name:
                return True
            
    def update(self):
        pass
    
    def __str__(self):
        return('LaserObject, type: ' + str(type(self)) + ', group:' + str(self.group) + ', effects:' + str(self.effects))



class Blank(LaserObject):

    def __init__(self, group = 0):
        self.group = group

        self.point_list = []
        blank_point = LaserPoint(0, 0)
        blank_point.set_color(0, 0, 0)
        self.point_list.append(blank_point)
        
        self.effects = []


class StaticLine(LaserObject):

    def __init__(self, from_point, to_point, group = 0):
        self.group = group

        self.point_list = []
        self.point_list.append(from_point)
        self.point_list.append(to_point)

        self.effects = []

 
class StaticCircle(LaserObject):
    def __init__(self, center_x, center_y, radius, r, g, b, group=0):
        super().__init__()

        self.group = group
        self.point_list = []
        self.effects = []

        # Number of points to create the circle
        points_count = 100  # This can be adjusted for smoother circles

        # Calculate the angle step size
        step_size = 2 * math.pi / points_count

        # Create points
        for i in range(points_count + 1):  # +1 to close the circle
            t = step_size * i
            x = int(round(radius * math.cos(t) + center_x, 0))
            y = int(round(radius * math.sin(t) + center_y, 0))
            laser_point = LaserPoint(x, y)
            laser_point.set_color(r, g, b)
            self.point_list.append(laser_point)

        # Ensure the last point is the same as the first to close the circle
        self.point_list.append(self.point_list[0])


class StaticWave(LaserObject):
    from models import LaserPoint

    def __init__(self, group = 0):
        import math

        self.group = group
        self.effects = []

        # Set up wave properties
        self.wave_length = int(global_data.config['laser_output']['width'])
        self.amplitude = 500
        self.frequency = 3
        self.vertical_shift = int(global_data.config['laser_output']['height']) / 2

        self.point_list = []
        for x in range(0, int(global_data.config['laser_output']['width']), 50):
            y = math.sin((2 * math.pi * self.frequency * x) / self.wave_length) * self.amplitude + self.vertical_shift
            laser_point = LaserPoint(int(x), int(y))
            laser_point.set_color(0, 0, 150)
            self.point_list.append(laser_point)
            

class AnimatedWave(StaticWave):
    def __init__(self, group=0, animation_speed=0.5):
        super().__init__(group)
        self.animation_progress = 0
        self.animation_speed = animation_speed
        
        self.group = group
        self.effects = []

    def update(self):
        # Increment the animation progress
        self.animation_progress += self.animation_speed

        # Clear the point list
        self.point_list = []

        # Add points to the point list
        for x in range(0, self.wave_length, 50):
            # Update the y value based on the current animation progress
            # Subtracting animation_progress from x to shift in the opposite direction
            y = math.sin((2 * math.pi * self.frequency * (x - self.animation_progress)) / self.wave_length) * self.amplitude + self.vertical_shift

            # Create a new laser point at this position
            laser_point = LaserPoint(int(x), int(y))

            # Set the color of the laser point
            laser_point.set_color(0, 0, 100)

            # Add the laser point to the point list
            self.point_list.append(laser_point)





