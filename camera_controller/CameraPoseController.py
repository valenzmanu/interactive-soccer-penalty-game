import threading
import logging
import time

import cv2
import mediapipe as mp


class CameraPoseController(threading.Thread):

    def __init__(self, camera_source=0):
        super().__init__()
        self.camera_source = camera_source
        self.is_running = False
        self.name = "CameraPoseController"

        # Media Pipe Objects
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_pose = mp.solutions.pose
        self.mp_holistic = mp.solutions.holistic

    def run(self) -> None:
        logging.info(f'Running {self.name}.')
        self.is_running = True
        cap = cv2.VideoCapture(self.camera_source)
        logging.debug(f'Using {self.camera_source} as camera source.')
        error_counter = 0
        start_time = time.time()
        start_fps = time.time()
        while self.is_running:
            try:
                ret, frame = cap.read()
                if ret is False:
                    error_counter += 1
                    logging.error(
                        f'Stream error No. {error_counter} in {round(time.time() - start_time, 2)}s of running.')
                    cap.release()
                    cap.open(self.camera_source)
                else:
                    start_fps = time.time()
                    self.infer(frame)
                    fps = 1 / (time.time() - start_fps)
                    logging.info(f'Running {self.name} @ {fps}')
            except Exception as ex:
                logging.error(ex)

        logging.info(f'{self.name} stopped.')
        cap.release()
        exit(0)

    def stop(self):
        logging.info(f'Stopping {self.name}.')
        self.is_running = False

    def infer(self, image):
        with self.mp_holistic.Holistic(
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
                model_complexity=0) as holistic:
            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False

            # Process the image and detect the holistic
            results = holistic.process(image)

            # Draw landmark annotation on the image.
            image.flags.writeable = True

            # Convert the image color back so it can be displayed
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            print(results.pose_landmarks)

            cv2.imshow('MediaPipe Holistic', image)

            if cv2.waitKey(5) & 0xFF == 27:
                self.stop()
