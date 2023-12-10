import logging
import ctypes
from optimizer import get_optimized_point_list
import global_data


def process_laser_output():
    SCAN_RATE = int(global_data.config['laser_output']['scan_rate'])
    INTENSITY_FACTOR = float(global_data.config['laser_output']['intensity_factor']) # 0.0 - 1.0

    logging.info('[LaserOut] Initializing laser output thread...')

    # define point structure
    class HeliosPoint(ctypes.Structure):
        _fields_ = [('x', ctypes.c_uint16),
                    ('y', ctypes.c_uint16),
                    ('r', ctypes.c_uint8),
                    ('g', ctypes.c_uint8),
                    ('b', ctypes.c_uint8),
                    ('i', ctypes.c_uint8)] # useless

    def initialize():
        global HeliosLib
        HeliosLib = ctypes.cdll.LoadLibrary("./libHeliosDacAPI.so")
        numDevices = HeliosLib.OpenDevices()
        logging.info('[LaserOut] Found ' + str(numDevices) + ' Helios DACs')

    def wait_until_ready():
        statusAttempts = 0
        max_status_attempts = 512
        while (statusAttempts < max_status_attempts and HeliosLib.GetStatus(0) != 1):
                statusAttempts += 1

    def blackout():
        point_type = HeliosPoint * 1
        helios_points = point_type()
        helios_points[0] = HeliosPoint(0, 0, 0, 0, 0, 0)
        HeliosLib.WriteFrame(0, SCAN_RATE, 0, ctypes.pointer(helios_points), 1)

    initialize()
    
    while global_data.running:
        optimized_point_list = get_optimized_point_list()
        count_points = len(optimized_point_list)

        if count_points > 0:

            if global_data.config['logging']['points_per_frame'] == 'yes':
                logging.debug('[LaserOutput] Points per frame: ' + str(count_points))

            helios_point_type = HeliosPoint * count_points
            helios_points = helios_point_type()

            i = 0
            for laser_point in optimized_point_list:
                helios_points[i] = HeliosPoint(int(laser_point.x), int(laser_point.y), int(laser_point.r * INTENSITY_FACTOR), int(laser_point.g * INTENSITY_FACTOR), int(laser_point.b * INTENSITY_FACTOR), 0)
                if global_data.config['logging']['laser_point'] == 'yes':
                    logging.debug('[LaserOutput] LaserPoint: ' + str(laser_point))
                i += 1

            wait_until_ready()

            # really draw points via Helios Laser DAC
            HeliosLib.WriteFrame(0, SCAN_RATE, 0, ctypes.pointer(helios_points), count_points)
        else:
            wait_until_ready()
            blackout()

    logging.info('[LaserOutput] Successfully stopped')

