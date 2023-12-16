import configparser
import logging
import numpy as np
from models import LaserPoint
from copy import copy
import global_data

# Efficiently optimize point list with effects and blank points
def get_optimized_point_list():
    optimized_point_list = []

    for visible_laser_object in global_data.visible_laser_objects:
        # Update laser objects (e.g., for moving elements)
        visible_laser_object.update()

        # Prepare effects (shifts)
        x_shift = sum(effect.level for effect in visible_laser_object.effects if effect.name == 'X_POS')
        y_shift = sum(effect.level for effect in visible_laser_object.effects if effect.name == 'Y_POS')

        # Add a blank point before every laser object
        blank_point_frames = int(global_data.config['laser_output']['blank_point_frames'])
        blank_point = LaserPoint(visible_laser_object.point_list[0].x + x_shift, visible_laser_object.point_list[0].y + y_shift)
        blank_point.set_color(0, 0, 0)
        optimized_point_list.extend([copy(blank_point)] * blank_point_frames)

        # Process each point in the laser object
        previously_optimized_laser_point = None
        for laser_point in visible_laser_object.point_list:
            optimized_laser_point = copy(laser_point)
            optimized_laser_point.x += x_shift
            optimized_laser_point.y += y_shift

            # Interpolate points for objects with small number of points
            if previously_optimized_laser_point and len(visible_laser_object.point_list) < 80:
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

        # Add blank point at end of laser object
        blank_point_end = copy(blank_point)
        optimized_point_list.append(blank_point_end)

        # Remove laser points out of screen coordinates
        screen_width = int(global_data.config['laser_output']['width'])
        screen_height = int(global_data.config['laser_output']['height'])
        optimized_point_list = [pt for pt in optimized_point_list if 0 < pt.x < screen_width and 0 < pt.y < screen_height]

    return optimized_point_list
