import global_data
import math
import random


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


class LaserObject():    
    point_list = []
    effects = []
    group = 0

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
        self.point_list = []
        self.group = group

        blank_point = LaserPoint(0, 0)
        blank_point.set_color(0, 0, 0)
        self.point_list.append(blank_point)


class StaticLine(LaserObject):

    def __init__(self, from_point, to_point, group = 0):
        self.point_list = []
        self.group = group

        self.point_list.append(from_point)
        self.point_list.append(to_point)

        self.effects = []

class StaticPoint(LaserObject):
    def __init__(self, target_point,group = 0):
        self.group = group

        self.point_list = []
        self.point_list.append(target_point)

        self.effects = []
 
class StaticCircle(LaserObject):
    def __init__(self, center_x, center_y, radius, r, g, b, group=0):
        super().__init__()

        self.point_list = []
        self.group = group

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
        self.point_list = []
        self.group = group
        
        # Set up wave properties
        self.wave_length = int(global_data.config['laser_output']['width'])
        self.amplitude = 500
        self.frequency = 3
        self.vertical_shift = int(global_data.config['laser_output']['height']) / 2

        for x in range(0, int(global_data.config['laser_output']['width']), 50):
            y = math.sin((2 * math.pi * self.frequency * x) / self.wave_length) * self.amplitude + self.vertical_shift
            laser_point = LaserPoint(int(x), int(y))
            laser_point.set_color(0, 0, 150)
            self.point_list.append(laser_point)


class AnimatedWave(StaticWave):
    def __init__(self, group=0, animation_speed=0.5, amplitude_mod=0, frequency_mod=0, noise_intensity=0):
        super().__init__(group)
        
        self.point_list = []
        self.group = group
        
        self.animation_progress = 0
        self.animation_speed = animation_speed
        self.amplitude_mod = amplitude_mod
        self.frequency_mod = frequency_mod
        self.noise_intensity = noise_intensity

    def update(self):
        self.animation_progress += self.animation_speed

        self.point_list = []

        for x in range(0, self.wave_length, 50):
            # Varying amplitude and frequency with new parameters
            varied_amplitude = self.amplitude + math.sin(x / 100.0) * self.amplitude_mod
            varied_frequency = self.frequency + math.sin(x / 200.0) * self.frequency_mod

            # Base sine wave
            y = math.sin((2 * math.pi * varied_frequency * (x - self.animation_progress)) / self.wave_length) * varied_amplitude

            # Additional wave for complexity (only if modulation is applied)
            if self.amplitude_mod != 0 or self.frequency_mod != 0:
                y += math.sin((4 * math.pi * varied_frequency * (x - self.animation_progress)) / self.wave_length) * (varied_amplitude / 3)

            # Noise addition (only if noise intensity is not zero)
            if self.noise_intensity != 0:
                y += random.uniform(-self.noise_intensity, self.noise_intensity)

            # Applying vertical shift
            y += self.vertical_shift

            laser_point = LaserPoint(int(x), int(y))
            laser_point.set_color(0, 0, 100)
            self.point_list.append(laser_point)







