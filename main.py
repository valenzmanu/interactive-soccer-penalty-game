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
    parser = argparse.ArgumentParser(prog='main')
    parser.add_argument('-c', '--camera', type=int, default=0, help='Camera port number', required=False)
    parser.add_argument('-s', '--stream', help='RTSP Stream url')
    args = parser.parse_args()
    config_logging()

    if args.stream:
        camera_source = args.stream
    else:
        camera_source = args.camera

    game_window_kwargs = ConfigFileReader.read_game_window_configs()
    penalty_game_window2 = PenaltyGameWindow2(**game_window_kwargs)

    camera_pose_controller = CameraPoseController(
        camera_source=camera_source,
        window_to_control=penalty_game_window2
    )

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
