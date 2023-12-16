import configparser
import logging


# return point list, but with:
# - blank points (so laser objects will not become connected by a line)
# - effects
def get_optimized_point_list():
    from models import LaserPoint
    from copy import copy
    import numpy
    import global_data

    config = configparser.ConfigParser()
    config.read('config.txt')

    optimized_point_list = []
    
    for visible_laser_object in global_data.visible_laser_objects:
        
        # Some LaserObjects need to update themselves due to current time (moving waves, moving SVG images...)
        visible_laser_object.update()

        # prepare effects
        x_shift = 0 # per laser object !
        y_shift = 0 # per laser object !
        if len(visible_laser_object.effects) > 0:
            for effect in visible_laser_object.effects:
                if effect.name == 'X_POS':
                    x_shift += effect.level
                elif effect.name == 'Y_POS':
                    y_shift += effect.level

        # add a blank point before every laser object
        # to make objects not become connected
        i = 0
        while i < int(global_data.config['laser_output']['blank_point_frames']):
            blank_laser_point1 = LaserPoint(visible_laser_object.point_list[0].x + x_shift, visible_laser_object.point_list[0].y + y_shift)
            blank_laser_point1.set_color(0, 0, 0)
            optimized_point_list.append(blank_laser_point1)
            i += 1

        # add interpolated points
        # for laser objects with just a small point amount (line)
        # to have sharper line ends
        laser_object_points = len(visible_laser_object.point_list)
        if global_data.config['logging']['laser_object_points'] == 'yes':
            logging.debug('[Optimizer] LaserObject points: ' + str(laser_object_points))
        
        previously_optimized_laser_point = None
        for laser_point in visible_laser_object.point_list:
            optimized_laser_point = copy(laser_point)

            optimized_laser_point.x += x_shift
            optimized_laser_point.y += y_shift

            # TODO optimized_laser_point.r *= intensity
            
            if previously_optimized_laser_point and laser_object_points < 80:
                # includes original start and end point
                interpolated_x_coords = numpy.linspace(previously_optimized_laser_point.x, optimized_laser_point.x, num=int(global_data.config['laser_output']['interpolated_points']))
                interpolated_y_coords = numpy.linspace(previously_optimized_laser_point.y, optimized_laser_point.y, num=int(global_data.config['laser_output']['interpolated_points']))

                i = 0
                for interpolated_x_coord in interpolated_x_coords:
                    interpolated_optimized_laser_point = copy(optimized_laser_point)
                    interpolated_optimized_laser_point.x = interpolated_x_coords[i]
                    interpolated_optimized_laser_point.y = interpolated_y_coords[i]
                    optimized_point_list.append(interpolated_optimized_laser_point)
                    i += 1

            else:
                optimized_point_list.append(optimized_laser_point)

            previously_optimized_laser_point = optimized_laser_point
            
        # add blank point at end of laser object
        blank_laser_point2 = LaserPoint(visible_laser_object.point_list[0].x + x_shift, visible_laser_object.point_list[0].y+ y_shift)
        blank_laser_point2.set_color(0, 0, 0)
        optimized_point_list.append(blank_laser_point2)

        # remove laser points out of screen coordinates
        new_optimized_point_list = copy(optimized_point_list)
        for optimized_point in optimized_point_list:
            if not optimized_point.is_blank(): 
                if optimized_point.y >= int(global_data.config['laser_output']['height']) or optimized_point.y <= 0 or optimized_point.x >= int(global_data.config['laser_output']['width']) or optimized_point.x <= 0:
                    new_optimized_point_list.remove(optimized_point)
        optimized_point_list = new_optimized_point_list

    return optimized_point_list