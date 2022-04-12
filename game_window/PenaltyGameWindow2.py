import logging
import time

import cv2
import numpy as np
import pygame


class PenaltyGameWindow2:
    DEFAULT_ANIMATION = 0

    def __init__(self, animations_paths: tuple, window_size: tuple = (640, 480), fullscreen: bool = False):
        """

        :param animations_paths: A tuple with the paths to video animations to play when a trigger event occurs. The animation with index 0 is the default animation
        :param window_size: A tuple with the window desired size defaults to (640, 480). This is ignored if fullscreen is True
        :param fullscreen: If True, the window is displayed in fullscreen and window_size is ignored.
        """
        # Window Configs
        self.window_size = window_size
        self.fullscreen = fullscreen
        self.is_active = True

        # Media Configs
        self.fps = 30
        assert len(animations_paths) > 0
        self.animations_paths = animations_paths
        self.caps = []
        self.current_animation_index = 0
        self.animation_is_finished = False
        for animation_paths in animations_paths:
            new_capture = cv2.VideoCapture(animation_paths)
            self.caps.append(new_capture)
        logging.info(f'Added {len(self.caps)} animations.')

        # Pygame Stuff
        self.name = "PenaltyGameWindow2"
        self.readable_name = "Penalty Game"
        self.pygame_clock = pygame.time.Clock()

        pygame.init()
        pygame.display.set_caption(self.readable_name)

        if self.fullscreen:
            import ctypes
            user32 = ctypes.windll.user32
            self.window_size = (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.window_size)

        # Flags
        self.animation_trigger_debounce_s = 3
        self.last_animation_trigger_time = 0
        self.new_trigger = False

    def update(self) -> None:
        ret, frame = self.get_frame_to_show()
        resized_frame = cv2.resize(frame, self.window_size, interpolation=cv2.INTER_AREA)
        pygame_surface = self.cv2_to_pygame(resized_frame)
        self.screen.blit(pygame_surface, [0, 0])
        pygame.display.flip()

    def get_frame_to_show(self):
        capture = self.caps[self.current_animation_index]
        ret, frame = capture.read()
        cv2.waitKey(5)

        if self.video_ended(ret):
            # First reset the video that just ended
            capture.set(cv2.CAP_PROP_POS_FRAMES, 0)

            # Then change the capture index to the default video
            self.animation_is_finished = True
            self.current_animation_index = self.DEFAULT_ANIMATION
            capture = self.caps[self.current_animation_index]
            capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = capture.read()
        return ret, frame

    def trigger_animation(self, animation_index) -> None:
        time_diff = time.time() - self.last_animation_trigger_time
        if not time_diff >= self.animation_trigger_debounce_s:
            logging.debug(f'Ignoring trigger due to time debounce. Time diff: {time_diff}')
            return

    def trigger_kick_video(self):
        logging.info("Triggering Kick Video")
        if self.animation_is_finished:
            self.current_animation_index = 1
            self.animation_is_finished = False

    @staticmethod
    def cv2_to_pygame(cv2_frame: np.ndarray) -> pygame.Surface:
        pygame_frame = cv2.cvtColor(cv2_frame, cv2.COLOR_BGR2RGB)
        pygame_frame = np.fliplr(pygame_frame)
        pygame_frame = np.rot90(pygame_frame)
        pygame_frame = pygame.surfarray.make_surface(pygame_frame)
        return pygame_frame

    @staticmethod
    def video_ended(ret: bool) -> bool:
        return not ret