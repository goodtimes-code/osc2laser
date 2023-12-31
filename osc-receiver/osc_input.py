from models import LaserPoint, Blank, StaticLine, StaticWave, Effect, AnimatedWave, StaticCircle, StaticPoint
import logging
import configparser
import time
import global_data
import argparse
import threading
import pythonosc.udp_client
from pythonosc import dispatcher
from pythonosc import osc_server


def print_osc_message(address, *args):
    if global_data.config['logging']['osc_server_received_message'] == 'yes':
        print(f"[OSC] Received OSC message at {address}: {args}")
    

def handle_osc_message(address, *args):
    if address == "/globals/scan_rate":
        global_data.scan_rate = int(args[0])
        if global_data.config['logging']['osc_server_received_message'] == 'yes':
            logging.info(f"[OSC] Handling global scan_rate: {global_data.scan_rate}")
    elif address == "/laserobject":
        laserobject_id = int(args[0])
        if global_data.config['logging']['osc_server_received_message'] == 'yes':
            logging.info(f"[OSC] Handling laserobject ID: {laserobject_id}")
        try:
            laser_object = global_data.NOTE_LASEROBJECT_MAPPING[laserobject_id]
            laser_object.group = 0
            global_data.visible_laser_objects = [laser_object]
            if global_data.config['logging']['osc_server_add_or_remove_laser_object'] == 'yes':
                logging.info(f'[OSC] Added new laser object: {laser_object}')
        except Exception as e:
            logging.error(f'[OSC] Error while adding new laser object: {e}')
    # /effect is related to any LaserObject
    elif address.startswith("/effect/"):
        if address == "/effect/xy_pos":
            # Handle the combined XY position message
            x_pos, y_pos = int(args[0]), int(args[1])
            handle_effect("X_POS", x_pos)
            handle_effect("Y_POS", y_pos)
        else:
            # Handle other effect messages
            pos = args[0]
            effect_names = {
                "/effect/x_pos": "X_POS",
                "/effect/y_pos": "Y_POS",
                "/effect/rgb_intensity": "RGB_INTENSITY",
                "/effect/scale_factor": "SCALE_FACTOR",
                "/effect/rotation_degrees": "ROTATION_DEGREES",
                "/effect/rotation_speed": "ROTATION_SPEED",
                "/effect/color_change/r": "COLOR_CHANGE_R",
                "/effect/color_change/g": "COLOR_CHANGE_G",
                "/effect/color_change/b": "COLOR_CHANGE_B"
            }
            effect_name = effect_names.get(address, "UNKNOWN_EFFECT")
            handle_effect(effect_name, pos)
    elif address.startswith("/parameters/"):
        parameter_name = address.split('/')[2]
        parameter_value = float(args[0])
        if global_data.config['logging']['osc_server_parameter_handling'] == 'yes':
            logging.info(f"[OSC] Handling parameter {parameter_name}: {parameter_value}")
        global_data.parameters[parameter_name] = parameter_value

def handle_effect(effect_name, pos):
    if global_data.config['logging']['osc_server_effect_handling'] == 'yes':
        logging.info(f"[OSC] Handling effect {effect_name}: {pos}")

    for visible_laser_object in global_data.visible_laser_objects:
        if visible_laser_object.group == 0:
            if not visible_laser_object.has_effect(effect_name):
                effect = Effect(effect_name, pos)
                visible_laser_object.effects.append(effect)
            else:
                for effect in visible_laser_object.effects:
                    if effect.name == effect_name:
                        effect.level = pos


def process_osc_input():    
    disp = dispatcher.Dispatcher()
    disp.map("*", print_osc_message)
    disp.map("/globals/scan_rate", handle_osc_message)
    disp.map("/laserobject", handle_osc_message)
    disp.map("/effect/x_pos", handle_osc_message)
    disp.map("/effect/y_pos", handle_osc_message)
    disp.map("/effect/xy_pos", handle_osc_message)
    disp.map("/effect/rgb_intensity", handle_osc_message)
    disp.map("/effect/scale_factor", handle_osc_message)
    disp.map("/effect/rotation_degrees", handle_osc_message)
    disp.map("/effect/rotation_speed", handle_osc_message)
    disp.map("/effect/color_change/r", handle_osc_message)
    disp.map("/effect/color_change/g", handle_osc_message)
    disp.map("/effect/color_change/b", handle_osc_message)
    disp.map("/parameters/*", handle_osc_message)

    server = osc_server.ThreadingOSCUDPServer(
        (global_data.config['osc_server']['ip'], int(global_data.config['osc_server']['port'])), disp)
    print(f"[OSC] Serving on {server.server_address}")
    
    # Run the server in a separate thread
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()

    # Monitor the global_data.running flag
    try:
        while global_data.running:
            # Implement a periodic check with a short sleep to reduce CPU usage
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        # Stop the server
        server.shutdown()
        server.server_close()
        server_thread.join()
        logging.info('[OSC] Successfully stopped')

def setup():
    laser_point1 = LaserPoint(0, int(global_data.config['laser_output']['height'])/2)
    laser_point1.set_color(0, 255, 0)

    laser_point2 = LaserPoint(int(global_data.config['laser_output']['width']), int(global_data.config['laser_output']['height'])/2)
    laser_point2.set_color(0, 255, 0)

    laser_point3 = LaserPoint(int(global_data.config['laser_output']['width'])/2, 0)
    laser_point3.set_color(255, 0, 0)

    laser_point4 = LaserPoint(int(global_data.config['laser_output']['width'])/2, int(global_data.config['laser_output']['height']))
    laser_point4.set_color(255, 0, 0)

    laser_point5 = LaserPoint(int(global_data.config['laser_output']['width'])/2,int(global_data.config['laser_output']['height'])/2)
    laser_point5.set_color(0, 255, 0)

    global_data.NOTE_LASEROBJECT_MAPPING = [
        Blank(), # No points
        StaticLine(laser_point1, laser_point2, 0), # Green horizontal line
        StaticLine(laser_point3, laser_point4, 0), # Red vertical line
        StaticWave(0), # Blue static wave
        AnimatedWave(0), # Blue animated wave
        StaticCircle(int(global_data.config['laser_output']['height'])/2, int(global_data.config['laser_output']['width'])/2, int(global_data.config['laser_output']['height'])/5, 0, 255, 0, 0), # Green static circle
        StaticPoint(laser_point5,0)
    ]

setup()