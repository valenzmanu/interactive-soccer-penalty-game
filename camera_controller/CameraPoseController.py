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

    def run(self) -> None:
        logging.info(f'Running {self.name}')
        logging.debug(f'Creating Mediapipe Objects')
        mp_drawing = mp.solutions.drawing_utils
        mp_holistic = mp.solutions.holistic
        logging.debug(f'Opening video capture from {self.camera_source}')
        cap = cv2.VideoCapture(self.camera_source)

        with mp_holistic.Holistic(
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5) as holistic:

            while cap.isOpened():

                success, image = cap.read()
                start = time.time()

                # Flip the image horizontally for a later selfie-view display
                # Convert the BGR image to RGB.
                image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

                # To improve performance, optionally mark the image as not writeable to
                # pass by reference.
                image.flags.writeable = False

                # Process the image and detect the holistic
                results = holistic.process(image)

                # Draw landmark annotation on the image.
                image.flags.writeable = True

                # Convert the image color back so it can be displayed
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                # print(results.pose_landmarks)

                mp_drawing.draw_landmarks(
                    image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
                mp_drawing.draw_landmarks(
                    image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
                mp_drawing.draw_landmarks(
                    image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)

                end = time.time()
                totalTime = end - start

                fps = 1 / totalTime
                cv2.putText(image, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 2)
                cv2.imshow(self.name, image)

                if cv2.waitKey(5) & 0xFF == 27:
                    break

    def stop(self):
        logging.info(f'Stopping {self.name}.')
        self.is_running = False
