import argparse
import logging

import pygame

from camera_controller.CameraPoseController import CameraPoseController
from config_file_reader.ConfigFileReader import ConfigFileReader
from game_window.PenaltyGameWindow2 import PenaltyGameWindow2


def config_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - [%(levelname)s][Thread %(threadName)s %(thread)d] %(filename)s:%(lineno)s -> %(message)s')


def main():

    config_logging()
    game_window_kwargs = ConfigFileReader.read_game_window_configs()
    penalty_game_window2 = PenaltyGameWindow2(**game_window_kwargs)

    camera_source = ConfigFileReader.read_camera_source()
    show_camera_window = ConfigFileReader.read_show_camera_window()
    camera_pose_controller = CameraPoseController(
        camera_source=camera_source,
        window_to_control=penalty_game_window2,
        show_camera_window=show_camera_window
    )

    camera_configs_kwargs = ConfigFileReader.read_camera_roi_configs()
    camera_pose_controller.set_camera_configs(**camera_configs_kwargs)
    camera_pose_controller.start()

    while True:
        penalty_game_window2.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                camera_pose_controller.stop()
                logging.info(f'Stopping Game')
                exit(0)


if __name__ == "__main__":
    main()
