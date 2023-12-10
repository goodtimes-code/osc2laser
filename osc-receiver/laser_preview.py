import logging
import pygame as pg
from copy import copy
import global_data


class LaserPreview():
    
    LASER_POINT_SIZE = int(global_data.config['laser_preview']['laser_point_size'])

    def __init__(self):
        logging.info('[LaserPreview] Initializing...')

        pg.init()
        pg.display.set_caption('osc2laser - Preview')

        self.screen = pg.display.set_mode((int(global_data.config['laser_output']['width']) * float(global_data.config['laser_preview']['screen_scale_factor']), int(global_data.config['laser_output']['height']) * float(global_data.config['laser_preview']['screen_scale_factor'])))
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()

    def update_screen(self):
        from optimizer import get_optimized_point_list
        
        self.screen.fill('black') # clear screen

        previous_laser_point_output = None
        for laser_point in get_optimized_point_list():

            laser_point_output = copy(laser_point)
            laser_point_output.x =laser_point_output.x * float(global_data.config['laser_preview']['screen_scale_factor'])
            laser_point_output.y =laser_point_output.y * float(global_data.config['laser_preview']['screen_scale_factor'])  

            pg.draw.circle(self.screen, (laser_point_output.r, laser_point_output.g, laser_point_output.b) , (laser_point_output.x, laser_point_output.y), self.LASER_POINT_SIZE)
            if previous_laser_point_output and not laser_point.is_blank():
                pg.draw.line(self.screen, (laser_point_output.r, laser_point_output.g, laser_point_output.b), (previous_laser_point_output.x, previous_laser_point_output.y), (laser_point_output.x, laser_point_output.y), self.LASER_POINT_SIZE)
            previous_laser_point_output = laser_point_output

        pg.display.flip() # show all drawings

    def run(self):
        import time

        while global_data.running:

            self.update_screen()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    global_data.running = False
                    pg.quit()
                    logging.info('[LaserPreview] Successfully stopped')


            
