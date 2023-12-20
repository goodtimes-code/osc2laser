import configparser
import logging
import numpy as np
from models import LaserPoint
from copy import copy
import global_data
import time

def get_optimized_point_list():
    optimized_point_list = []
    
    for visible_laser_object in global_data.visible_laser_objects:
        visible_laser_object.update()

        rgb_intensity = 0
        y_shift = 0
        x_shift = 0

        for effect in visible_laser_object.effects:
            if effect.name == 'RGB_INTENSITY':
                rgb_intensity = effect.level
            if effect.name == 'X_POS':
                x_shift = effect.level
            elif effect.name == 'Y_POS':
                y_shift = effect.level

        blank_point_frames = int(global_data.config['laser_output']['blank_point_frames'])
        blank_point = LaserPoint(visible_laser_object.point_list[0].x + x_shift, visible_laser_object.point_list[0].y + y_shift)
        blank_point.set_color(0, 0, 0)
        optimized_point_list.extend([copy(blank_point)] * blank_point_frames)

        previously_optimized_laser_point = None
        for laser_point in visible_laser_object.point_list:
            optimized_laser_point = copy(laser_point)
            optimized_laser_point.x += x_shift
            optimized_laser_point.y += y_shift

            for color in ['r', 'g', 'b']:
                if rgb_intensity > 0:
                    setattr(optimized_laser_point, color, getattr(optimized_laser_point, color) / 255 * rgb_intensity)
                else:
                    setattr(optimized_laser_point, color, 0)

            if previously_optimized_laser_point and len(visible_laser_object.point_list) < int(global_data.config['laser_output']['interpolated_points']):
                interpolated_x_coords = np.linspace(previously_optimized_laser_point.x, optimized_laser_point.x, num=int(global_data.config['laser_output']['interpolated_points']))
                interpolated_y_coords = np.linspace(previously_optimized_laser_point.y, optimized_laser_point.y, num=int(global_data.config['laser_output']['interpolated_points']))

                for x, y in zip(interpolated_x_coords, interpolated_y_coords):
                    interpolated_point = copy(optimized_laser_point)
                    interpolated_point.x = x
                    interpolated_point.y = y
                    optimized_point_list.append(interpolated_point)
            else:
                optimized_point_list.append(optimized_laser_point)

            previously_optimized_laser_point = optimized_laser_point

        blank_point_end = copy(blank_point)
        optimized_point_list.append(blank_point_end)

        screen_width = int(global_data.config['laser_output']['width'])
        screen_height = int(global_data.config['laser_output']['height'])
        
        # New logic for handling points out of screen
        new_optimized_point_list = []
        for pt in optimized_point_list:
            if 0 <= pt.x <= screen_width and 0 <= pt.y <= screen_height:
                new_optimized_point_list.append(pt)
            else:
                # Add a blank point near the border instead of removing the point
                border_point = copy(blank_point)
                border_point.x = max(0, min(pt.x, screen_width))
                border_point.y = max(0, min(pt.y, screen_height))
                new_optimized_point_list.append(border_point)

        optimized_point_list = new_optimized_point_list

    return optimized_point_list

