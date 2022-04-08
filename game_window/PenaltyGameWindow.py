import logging
import threading

import cv2


class PenaltyGameWindow(threading.Thread):
    STANDBY_CAP = 0
    GOAL_CAP = 1
    FAIL_CAP = 2

    def __init__(self, standby_video_path: str, goal_video_path: str, fail_video_path: str, shape=(640, 480)):
        super(PenaltyGameWindow, self).__init__()
        self.is_running = False
        self.standby_video_path = standby_video_path
        self.goal_video_path = goal_video_path
        self.fail_video_path = fail_video_path
        self.name = "PenaltyGameWindow"
        self.success_counter = 0
        self._trigger_kick_video_flag = False
        self.current_cap = self.STANDBY_CAP
        self.shape = shape
        self._is_animation_triggered_flag = False

    def run(self) -> None:
        # TODO: Display high resolution videos in fullscreen
        #  https://stackoverflow.com/questions/49949639/fullscreen-a-video-on-opencv
        self.is_running = True
        logging.info(f'Running {self.name}')
        standby_cap = cv2.VideoCapture(self.standby_video_path)
        goal_cap = cv2.VideoCapture(self.goal_video_path)
        fail_cap = cv2.VideoCapture(self.fail_video_path)

        while self.is_running:
            ret, frame = standby_cap.read()
            if self._trigger_kick_video_flag:
                if self.success_counter == 0:
                    self.current_cap = self.FAIL_CAP
                    goal_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    self.show_video_uninterrupted(fail_cap)
                else:
                    self.current_cap = self.GOAL_CAP
                    fail_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    self.show_video_uninterrupted(goal_cap)
                standby_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            else:
                self.current_cap = self.STANDBY_CAP

            if ret:
                resized_frame = cv2.resize(frame, self.shape, interpolation=cv2.INTER_AREA)
                cv2.imshow(self.name, resized_frame)
                if cv2.waitKey(5) & 0xFF == 27:
                    self.is_running = False
                    logging.info(f'quit command received, {self.name} will stop.')
            else:
                self.reset_kick_trigger()
                standby_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def stop(self):
        logging.info(f'Stopping {self.name}.')
        self.is_running = False

    def trigger_kick_video(self):
        self._trigger_kick_video_flag = True
        self.success_counter = (self.success_counter + 1) % 2

    def reset_kick_trigger(self):
        self._trigger_kick_video_flag = False

    def show_video_uninterrupted(self, cv2_cap: cv2.VideoCapture):
        while True:
            ret, frame = cv2_cap.read()
            if ret:
                resized_frame = cv2.resize(frame, self.shape, interpolation=cv2.INTER_AREA)
                cv2.imshow(self.name, resized_frame)
                cv2.waitKey(5)
            else:
                break
