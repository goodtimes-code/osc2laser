import global_data
import math
import random
from utils import calculate_geometric_center


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
            
    def apply_rotation(self, rotation_speed):
        center_x, center_y = calculate_geometric_center(self.point_list)
        rotation_radians = math.radians(rotation_speed)

        for point in self.point_list:
            dx, dy = point.x - center_x, point.y - center_y
            point.x = center_x + dx * math.cos(rotation_radians) - dy * math.sin(rotation_radians)
            point.y = center_y + dx * math.sin(rotation_radians) + dy * math.cos(rotation_radians)
            
    def update(self):
        for effect in self.effects:
            if effect.name == 'ROTATION_SPEED':
                self.apply_rotation(effect.level/255)
    
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


class StaticPoint(LaserObject):
    def __init__(self, target_point,group = 0):
        self.group = group

        self.point_list = []
        self.point_list.append(target_point)

 
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
        
        self.draw_wave()

    def draw_wave(self):
        self.point_list = []
        for x in range(0, int(global_data.config['laser_output']['width']), 50):
            y = math.sin((2 * math.pi * self.frequency * x) / self.wave_length) * self.amplitude + self.vertical_shift
            laser_point = LaserPoint(int(x), int(y))
            laser_point.set_color(0, 0, 255)
            self.point_list.append(laser_point)
            
    def update(self):
        super().update()
        if 'wave_amplitude' in global_data.parameters and self.amplitude != global_data.parameters['wave_amplitude']:
            self.amplitude = global_data.parameters['wave_amplitude']
            self.draw_wave()
            
        if 'wave_length' in global_data.parameters and self.wave_length != global_data.parameters['wave_length']:
            self.wave_length = global_data.parameters['wave_length']
            self.draw_wave()
        
        """    
        if 'wave_frequency' in global_data.parameters and self.frequency != global_data.parameters['wave_frequency']:
            self.frequency = global_data.parameters['wave_frequency']
            self.draw_wave()
        """


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
        
        if 'wave_speed' in global_data.parameters and self.animation_speed != global_data.parameters['wave_speed']:
            self.animation_speed = global_data.parameters['wave_speed']

        for x in range(0, int(self.wave_length), 50):
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
            laser_point.set_color(0, 0, 255)
            self.point_list.append(laser_point)
            
        super().update()
        

class StaticStars(LaserObject):
    def __init__(self, group=0):
        super().__init__()
        self.group = group
        self.star_count = int(global_data.parameters.get('stars_amount', 8))  # Default to 50 stars if not specified
        self.generate_stars()

    def generate_stars(self):
        self.point_list = []
        for _ in range(self.star_count):
            # Add the actual star point
            x = random.randint(0, int(global_data.config['laser_output']['width']))
            y = random.randint(0, int(global_data.config['laser_output']['height']))
            # Add a blank point after each star to ensure the laser is off when moving to the next point
            blank_point = LaserPoint(x, y)
            blank_point.set_color(0, 0, 0)
            self.point_list.append(blank_point)
            
            star_point = LaserPoint(x, y)
            star_point.set_color(255, 255, 255)  # White color for stars
            self.point_list.append(star_point)

            # Add a blank point after each star to ensure the laser is off when moving to the next point
            #blank_point = LaserPoint(x, y)
            #blank_point.set_color(0, 0, 0)
            #self.point_list.append(blank_point)
            

    def update(self):
        if 'stars_amount' in global_data.parameters and self.star_count != global_data.parameters['stars_amount']:
            self.star_count = int(global_data.parameters['stars_amount'])
            self.generate_stars()
        super().update()










