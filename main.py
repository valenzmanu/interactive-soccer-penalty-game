import argparse
import logging

from camera_controller.CameraPoseController import CameraPoseController


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

    camera_pose_controller = CameraPoseController(camera_source)
    camera_pose_controller.start()


if __name__ == "__main__":
    main()
