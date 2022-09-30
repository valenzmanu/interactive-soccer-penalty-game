import logging
import threading
import time

import cv2
import mediapipe as mp
import numpy as np

from game_window.PenaltyGameWindow2 import PenaltyGameWindow2
from pose_classification.simple_threshold_pose_classification import SimpleThresholdPoseClassification


class CameraPoseController(threading.Thread):

    def __init__(self, camera_source=0, window_to_control: PenaltyGameWindow2 = None, show_camera_window=True):
        super().__init__()
        self.camera_source = camera_source
        self.is_running = False
        self.name = "CameraPoseController"
        self.pose_samples_folder = 'poses_csvs'
        self.class_name = 'kicking'
        self._is_kicking = False
        self.window_to_control = window_to_control
        self.threshold_line_y = 350
        self.person_roi_w = 400
        self.person_roi_h = 400
        self._person_roi_w_half = int(self.person_roi_w / 2)
        self._person_roi_h_half = int(self.person_roi_h / 2)
        self.frame_shape = None
        self.frame_center = None
        self.frame_shape_is_set = False
        self.show_camera_window = show_camera_window

    def set_camera_configs(self, person_roi_w: int, person_roi_h: int, threshold_line_y: int) -> None:
        self.person_roi_w = person_roi_w
        self.person_roi_h = person_roi_h
        self.threshold_line_y = threshold_line_y
        self._person_roi_w_half = int(self.person_roi_w / 2)
        self._person_roi_h_half = int(self.person_roi_h / 2)

    def set_frame_shape(self, frame_shape: tuple):
        self.frame_shape = frame_shape
        height, width, channels = self.frame_shape
        self.frame_center = (int(height / 2), int(width / 2))
        logging.info(f"Frame shape: {height, width} -> Frame Center: {self.frame_center}")

    def get_person_roi(self, frame):
        if self.frame_center is None:
            self.set_frame_shape(frame_shape=frame.shape)
        x_center, y_center = self.frame_center
        if self._person_roi_w_half <= x_center and self._person_roi_h_half <= y_center:
            y0, y1 = y_center - self._person_roi_h_half, y_center + self._person_roi_h_half
            x0, x1 = x_center - self._person_roi_w_half, x_center + self._person_roi_w_half
            return frame[y0:y1, x0:x1]
        return frame

    def run(self) -> None:
        self.is_running = True
        logging.info(f'Running {self.name}')
        logging.debug(f'Creating Mediapipe Objects')
        mp_drawing = mp.solutions.drawing_utils
        mp_holistic = mp.solutions.holistic
        simple_threshold_classificator = SimpleThresholdPoseClassification(threshold_y=self.threshold_line_y)
        logging.debug(f'Opening video capture from {self.camera_source}')
        cap = cv2.VideoCapture(self.camera_source, cv2.CAP_DSHOW)

        with mp_holistic.Holistic(
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5) as holistic:

            while cap.isOpened() and self.is_running:

                success, _frame = cap.read()
                frame = self.get_person_roi(_frame)
                unprocessed_frame = frame.copy()
                start = time.time()

                # To improve performance, optionally mark the image as not writeable to
                # pass by reference.
                # frame.flags.writeable = False

                # Process the image and detect the holistic
                results = holistic.process(frame)

                # Draw landmark annotation on the image.
                frame.flags.writeable = True

                # Convert the image color back so it can be displayed
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                pose_landmarks = results.pose_landmarks

                output_frame = frame.copy()
                if pose_landmarks is not None:
                    # Get landmarks.
                    frame_height, frame_width = output_frame.shape[0], output_frame.shape[1]
                    pose_landmarks = np.array([[lmk.x * frame_width, lmk.y * frame_height, lmk.z * frame_width]
                                               for lmk in pose_landmarks.landmark], dtype=np.float32)
                    assert pose_landmarks.shape == (33, 3), 'Unexpected landmarks shape: {}'.format(
                        pose_landmarks.shape)

                    # Classify the pose on the current frame.
                    self._is_kicking = simple_threshold_classificator.detect_kick(pose_landmarks, unprocessed_frame)

                    if self._is_kicking and self.window_to_control is not None:
                        logging.info(f'Triggering kick video')
                        self.window_to_control.trigger_kick_video()

                mp_drawing.draw_landmarks(
                    unprocessed_frame, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
                mp_drawing.draw_landmarks(
                    unprocessed_frame, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
                mp_drawing.draw_landmarks(
                    unprocessed_frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)

                end = time.time()
                totalTime = end - start

                fps = 1 / totalTime
                cv2.putText(unprocessed_frame, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0),
                            2)

                thickness = 2
                height, width, channels = frame.shape
                cv2.line(unprocessed_frame, (0, self.threshold_line_y), (width, self.threshold_line_y), (0, 255, 0),
                         thickness=thickness)

                if self.show_camera_window:
                    cv2.imshow(self.name, unprocessed_frame)

                if cv2.waitKey(1) & 0xFF == 27:
                    break

    def stop(self):
        logging.info(f'Stopping {self.name}.')
        self.is_running = False

    def is_kicking(self):
        return self._is_kicking
