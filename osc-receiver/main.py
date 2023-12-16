import os
import art
import time
import argparse
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as pg
import threading
import logging
import configparser
import global_data

# Initialization
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', default='config_laser1.txt', help='Path to the configuration file')
args = parser.parse_args()

# Read configuration from the specified file
global_data.config = configparser.ConfigParser()
global_data.config.read(args.config)


def main():
    from osc_input import process_osc_input
    from laser_output import process_laser_output
    from laser_preview import LaserPreview

    global main_running

    print(art.text2art("osc2laser"))
    logging.info('[Main] osc2laser - Starting up...')

    laser_output_thread = threading.Thread(target=process_laser_output)
    laser_output_thread.start()

    # midi_input_thread = threading.Thread(target=process_midi_input)
    # midi_input_thread.start()

    osc_input_thread = threading.Thread(target=process_osc_input)
    osc_input_thread.start()

    laser_preview = LaserPreview()
    laser_preview.run()
    global_data.running = False


if __name__ == "__main__":
    main()
    logging.info('[Main] Successfully stopped')
