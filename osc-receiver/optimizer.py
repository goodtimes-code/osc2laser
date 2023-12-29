import configparser
import logging
import numpy as np
from models import LaserPoint
from copy import copy
import global_data
import time
import math

def apply_effects_to_laser_points(visible_laser_object):
    optimized_points = []
    rgb_intensity, x_shift, y_shift, scale_factor, rotation_degrees,color_r,color_g,color_b = 255, 0, 0, 1, 0, None, None, None

    # Extracting effect levels from the visible laser object
    for effect in visible_laser_object.effects:
        if effect.name == 'RGB_INTENSITY':
            rgb_intensity = effect.level
        elif effect.name == 'X_POS':
            x_shift = effect.level
        elif effect.name == 'Y_POS':
            y_shift = effect.level
        elif effect.name == 'SCALE_FACTOR':
            scale_factor = effect.level
        elif effect.name == 'ROTATION_DEGREES':
            rotation_degrees = effect.level
        elif effect.name == 'COLOR_CHANGE_R':
            color_r = effect.level
            print("Wert Input R:"+effect.level)
        elif effect.name == 'COLOR_CHANGE_G':
            color_g = effect.level
            print("Wert Input R:"+effect.level)
        elif effect.name == 'COLOR_CHANGE_B':
            color_b = effect.level

    # Apply X_POS and Y_POS effects and calculate the new geometric center
    shifted_points = []
    for laser_point in visible_laser_object.point_list:
        shifted_point = copy(laser_point)
        shifted_point.x += x_shift
        shifted_point.y += y_shift
        shifted_points.append(shifted_point)

        if color_r:
            shifted_point.r = color_r
            print("Wert R:"+color_r)
        if color_b: 
            shifted_point.b = color_b
        if color_g:
            shifted_point.g = color_g
            print("Wert G:"+color_g)

    total_x, total_y = sum(p.x for p in shifted_points), sum(p.y for p in shifted_points)
    center_x, center_y = total_x / len(shifted_points), total_y / len(shifted_points)

    # Convert rotation degrees to radians
    rotation_radians = math.radians(rotation_degrees)

    # Apply SCALE_FACTOR, RGB_INTENSITY, and ROTATION_DEGREES effects
    for shifted_point in shifted_points:
        optimized_point = copy(shifted_point)

        # Apply RGB_INTENSITY effect
        for color in ['r', 'g', 'b']:
            if rgb_intensity > 0:
                setattr(optimized_point, color, getattr(optimized_point, color) / 255 * rgb_intensity)
            else:
                setattr(optimized_point, color, 0)

        # Apply SCALE_FACTOR effect
        optimized_point.x = center_x + (shifted_point.x - center_x) * scale_factor
        optimized_point.y = center_y + (shifted_point.y - center_y) * scale_factor

        # Apply ROTATION_DEGREES effect
        dx, dy = optimized_point.x - center_x, optimized_point.y - center_y
        optimized_point.x = center_x + dx * math.cos(rotation_radians) - dy * math.sin(rotation_radians)
        optimized_point.y = center_y + dx * math.sin(rotation_radians) + dy * math.cos(rotation_radians)

        optimized_points.append(optimized_point)

    return optimized_points


def interpolate_points(point1, point2, num_points):
    """
    Interpolates points between two given laser points.

    Parameters:
    - point1, point2: The start and end points for interpolation.
    - num_points: The number of points to interpolate between the two points.

    Returns:
    - Arrays of interpolated x and y coordinates.
    """
    interpolated_x_coords = np.linspace(point1.x, point2.x, num=num_points)
    interpolated_y_coords = np.linspace(point1.y, point2.y, num=num_points)
    return interpolated_x_coords, interpolated_y_coords

def adjust_points_for_screen(optimized_point_list, screen_width, screen_height, blank_point):
    """
    Adjusts points to ensure they fit within the screen dimensions. If a point falls outside the screen,
    it is replaced with a blank point at the nearest border.

    Parameters:
    - optimized_point_list: List of optimized points.
    - screen_width, screen_height: Dimensions of the screen.
    - blank_point: A point with no color used to represent out-of-bounds points.

    Returns:
    - List of points adjusted for screen boundaries.
    """
    new_optimized_point_list = []
    for pt in optimized_point_list:
        if 0 <= pt.x <= screen_width and 0 <= pt.y <= screen_height:
            new_optimized_point_list.append(pt)
        else:
            border_point = copy(blank_point)
            border_point.x = max(0, min(pt.x, screen_width))
            border_point.y = max(0, min(pt.y, screen_height))
            new_optimized_point_list.append(border_point)
    return new_optimized_point_list

def get_optimized_point_list():
    optimized_point_list = []
    
    for visible_laser_object in global_data.visible_laser_objects:
        visible_laser_object.update()

        applied_points = apply_effects_to_laser_points(visible_laser_object)
        
        # Setup blank point for later use
        blank_point = LaserPoint(applied_points[0].x, applied_points[0].y)
        blank_point.set_color(0, 0, 0)

        # Check if the shape has the same start and end points
        same_start_end_points = (applied_points[0].x == applied_points[-1].x and 
                                 applied_points[0].y == applied_points[-1].y)

        # Add initial blank points only if start and end points are different
        if not same_start_end_points:
            blank_point_frames = int(global_data.config['laser_output']['blank_point_frames'])
            optimized_point_list.extend([copy(blank_point)] * blank_point_frames)

        previously_optimized_laser_point = None
        for optimized_point in applied_points:
            
            if previously_optimized_laser_point and len(visible_laser_object.point_list) < int(global_data.config['laser_output']['interpolated_points']):
                interpolated_x_coords, interpolated_y_coords = interpolate_points(previously_optimized_laser_point, optimized_point, int(global_data.config['laser_output']['interpolated_points']))

                for x, y in zip(interpolated_x_coords, interpolated_y_coords):
                    interpolated_point = copy(optimized_point)
                    interpolated_point.x = x
                    interpolated_point.y = y
                    optimized_point_list.append(interpolated_point)
            else:
                optimized_point_list.append(optimized_point)

            previously_optimized_laser_point = optimized_point

        # Add a blank point at the end to ensure a smooth transition, only if start and end points are different
        if not same_start_end_points:
            blank_point_end = copy(blank_point)
            optimized_point_list.append(blank_point_end)

        screen_width = int(global_data.config['laser_output']['width'])
        screen_height = int(global_data.config['laser_output']['height'])

        # Adjust points to fit within screen bounds, replacing out-of-bounds points with blank points.
        optimized_point_list = adjust_points_for_screen(optimized_point_list, screen_width, screen_height, blank_point)

    return optimized_point_list

