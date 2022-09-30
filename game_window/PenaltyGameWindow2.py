import logging
import time

import cv2
import numpy as np
import pygame
import random
import os

from config_file_reader.ConfigFileReader import ConfigFileReader
from game_objects.AccuracyMovingBar import AccuracyMovingBar


class PenaltyGameWindow2:
    DEFAULT_ANIMATION = 0

    def __init__(self, animations_paths: tuple, window_size: tuple = (640, 480), window_start_position=(500, 500),
                 fullscreen: bool = False,
                 spots_paths: tuple = ("spots/spot1.mp4", "spots/spot2.mp4", "spots/spot3.mp4")):
        """

        :param animations_paths: A tuple with the paths to video animations to play when a trigger event occurs. The animation with index 0 is the default animation
        :param window_size: A tuple with the window desired size defaults to (640, 480). This is ignored if fullscreen is True
        :param fullscreen: If True, the window is displayed in fullscreen and window_size is ignored.
        """
        # Window Configs
        self.window_size = window_size
        self.fullscreen = fullscreen
        self.is_active = True
        self.window_start_position = window_start_position

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

        # Spots configs
        self.spots = []
        self.current_spot_index = 0
        for spot_path in spots_paths:
            new_spot_cap = cv2.VideoCapture(spot_path)
            self.spots.append(new_spot_cap)

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
            self.fake_screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            os.environ['SDL_VIDEO_WINDOW_POS'] = str(self.window_start_position[0]) + "," + str(
                self.window_start_position[1])
            self.screen = pygame.display.set_mode(self.window_size)
            self.fake_screen = self.screen.copy()

        # Flags
        self.animation_trigger_debounce_s = 3
        self.last_animation_trigger_time = 0
        self.new_trigger = False
        self.waiting = False
        self.showing_spot = True

        # Pause Buffer
        self.pause_frame = None

        # Moving Objects
        self.accuracy_bar = AccuracyMovingBar(
            base_image_path="game_icons/accuracy_bar_degradated.png",
            moving_object_image_path="game_icons/ducal-qtar-rojos-dp-brasil.png",
            velocity=ConfigFileReader.read_game_settings()["bar-velocity"],
            window_size=self.window_size
        )

    def get_spot_frame(self):
        capture = self.spots[self.current_spot_index]
        ret, frame = capture.read()
        cv2.waitKey(30)

        if self.video_ended(ret):
            # First reset the video that just ended
            capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.current_spot_index = (self.current_spot_index + 1) % len(self.spots)

            # Then change the capture to the next spot
            capture = self.spots[self.current_spot_index]
            capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = capture.read()
            cv2.waitKey(80)

        return ret, frame

    def update(self) -> None:
        ret, frame = self.get_frame_to_show() if not self.showing_spot else self.get_spot_frame()
        if not ret:
            return
        try:
            resized_frame = cv2.resize(frame, self.window_size, interpolation=cv2.INTER_AREA)
            pygame_surface = self.cv2_to_pygame(resized_frame)
            self.fake_screen.blit(pygame_surface, [0, 0])
            if not self.showing_spot:
                self.accuracy_bar.update(self.fake_screen)
            self.screen.blit(pygame.transform.scale(self.fake_screen, self.window_size), (0, 0))
            pygame.display.update()
            pygame.display.flip()
        except Exception as ex:
            logging.info(ex)

    def get_frame_to_show(self):

        if self.waiting and self.pause_frame is not None:
            return True, self.pause_frame

        capture = self.caps[self.current_animation_index]
        ret, frame = capture.read()
        cv2.waitKey(1)

        if self.video_ended(ret):

            # If win or loose, make a pause
            if self.current_animation_index != 0:
                self.wait_until_time_or_signal()
                return True, self.pause_frame

            # First reset the video that just ended
            capture.set(cv2.CAP_PROP_POS_FRAMES, 0)

            # Then change the capture index to the default video
            self.animation_is_finished = True
            self.current_animation_index = self.DEFAULT_ANIMATION
            capture = self.caps[self.current_animation_index]
            capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = capture.read()
            cv2.waitKey(80)
        else:
            self.pause_frame = frame.copy()
        return ret, frame

    def trigger_animation(self, animation_index) -> None:
        time_diff = time.time() - self.last_animation_trigger_time
        if not time_diff >= self.animation_trigger_debounce_s:
            logging.debug(f'Ignoring trigger due to time debounce. Time diff: {time_diff}')
            return

    def trigger_kick_video(self):
        if self.showing_spot or self.waiting:
            return
        region = self.accuracy_bar.get_moving_object_region()
        self.accuracy_bar.stop()
        logging.info(f"Triggering Kick Video. Ball in region {region}")
        if self.animation_is_finished:
            if region == self.accuracy_bar.GREEN:
                self.current_animation_index = 1
            elif region == self.accuracy_bar.YELLOW:
                self.current_animation_index = random.randint(1, 2)
            else:
                self.current_animation_index = 2
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

    def wait_until_time_or_signal(self):
        self.waiting = True

    def quit_waiting(self):
        self.waiting = False
        self.pause_frame = None
        self.animation_is_finished = True
        self.current_animation_index = self.DEFAULT_ANIMATION
        for capture in self.caps:
            capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.accuracy_bar.play()

    def toggle_mode(self):
        self.showing_spot = not self.showing_spot
