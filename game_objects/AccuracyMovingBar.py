import logging
import random

import pygame
import time
from threading import Timer


class AccuracyMovingBar:
    DOWN = 1
    UP = -1

    INVALID_REGION = -1
    RED = 1
    YELLOW = 2
    GREEN = 3

    RED_REGION_UP = (60, 80)
    YELLOW_REGION_UP = (81, 100)
    GREEN_REGION = (101, 120)
    YELLOW_REGION_DOWN = (121, 140)
    RED_REGION_DOWN = (141, 160)

    def __init__(self, base_image_path: str, moving_object_image_dir: list, velocity: int, window_size: tuple):

        self.window_size = window_size

        # Base Image
        self.base_image_path = base_image_path
        self.moving_object_image_dir = moving_object_image_dir
        self.moving_object_image_path = random.choice(moving_object_image_dir)
        self._base_image_dimensions = (0.14 * window_size[0], 0.75 * window_size[1])
        self._base_image = pygame.image.load(self.base_image_path)
        self._base_image = pygame.transform.scale(self._base_image, self._base_image_dimensions)
        self._base_image_origin = (0.01 * window_size[0] - 10, 0.125 * window_size[1])

        # Moving Circle
        base_image_width = self._base_image_dimensions[0]
        self._moving_object_image = pygame.image.load(self.moving_object_image_path)
        original_size = self._moving_object_image.get_size()
        self._moving_object_image_dimensions = (
            int(0.0004 * window_size[0] * original_size[0]), int(0.0004 * window_size[0] * original_size[1]))
        self._moving_object_image = pygame.transform.scale(self._moving_object_image,
                                                           self._moving_object_image_dimensions)
        self._moving_object_image = pygame.transform.rotate(self._moving_object_image, 10)
        self._moving_object_is_paused = False
        self.velocity = velocity
        self._current_velocity_direction = 1
        self.upper_limit = self._base_image_origin[1]
        self.lower_limit = self._base_image_origin[1] + self._base_image_dimensions[1] - \
                           self._moving_object_image.get_size()[1]
        print("********** Bar Limits **********")
        print("upper_limit:", self.upper_limit)
        print("lower_limit:", self.lower_limit)
        self.current_y_position = int(self.lower_limit - self.upper_limit / 2)

        # Bar Regions
        y_offset = self._base_image_origin[1]
        bar_y_size = self._base_image_dimensions[1]
        self.red_region_up = (y_offset, y_offset + 0.2 * bar_y_size)
        self.yellow_region_up = (y_offset + 0.2 * bar_y_size, y_offset + 0.4 * bar_y_size)
        self.green_region = (y_offset + 0.4 * bar_y_size, y_offset + 0.6 * bar_y_size)
        self.yellow_region_down = (y_offset + 0.6 * bar_y_size, y_offset + 0.8 * bar_y_size)
        self.red_region_down = (y_offset + 0.8 * bar_y_size, y_offset + bar_y_size)
        print("********** Bar Regions **********")
        print("red_region_up:", self.red_region_up)
        print("yellow_region_up:", self.yellow_region_up)
        print("green_region:", self.green_region)
        print("yellow_region_down:", self.yellow_region_down)
        print("red_region_down:", self.red_region_down)

    def start(self):
        _base_image = pygame.image.load(self.base_image_path)
        _moving_object_image = pygame.image.load(self.moving_object_image_path)

    def _update_paused(self, y_position: int, screen: pygame.surface):
        position = self._moving_object_image.get_rect()
        position.y = y_position
        position.x = self._base_image_origin[0] + int(self._moving_object_image.get_size()[0] * 0.1)
        screen.blit(self._base_image, self._base_image_origin)
        screen.blit(self._moving_object_image, position)
        pygame.display.update()

    def set_moving_object_new_image(self):
        self._moving_object_image = pygame.image.load(random.choice(self.moving_object_image_dir))
        original_size = self._moving_object_image.get_size()
        self._moving_object_image_dimensions = (
            int(0.0004 * self.window_size[0] * original_size[0]), int(0.0004 * self.window_size[0] * original_size[1]))
        self._moving_object_image = pygame.transform.scale(self._moving_object_image,
                                                           self._moving_object_image_dimensions)
        self._moving_object_image = pygame.transform.rotate(self._moving_object_image, 10)

    def update(self, screen: pygame.Surface):

        if self._moving_object_is_paused:
            self._update_paused(self.current_y_position, screen)
            return

        screen.blit(self._base_image, self._base_image_origin)
        position = self._moving_object_image.get_rect()

        if self.current_y_position <= self.upper_limit and self._current_velocity_direction == self.UP:
            self._current_velocity_direction = self.DOWN
            position = self.move_object_down(self._moving_object_image)
        elif self.current_y_position <= self.upper_limit and self._current_velocity_direction == self.DOWN:
            position = self.move_object_down(self._moving_object_image)
        elif self.upper_limit <= self.current_y_position <= self.lower_limit and self._current_velocity_direction == self.DOWN:
            position = self.move_object_down(self._moving_object_image)
        elif self.upper_limit <= self.current_y_position <= self.lower_limit and self._current_velocity_direction == self.UP:
            position = self.move_object_up(self._moving_object_image)
        elif self.current_y_position >= self.lower_limit and self._current_velocity_direction == self.DOWN:
            self._current_velocity_direction = self.UP
            position = self.move_object_up(self._moving_object_image)
        elif self.current_y_position >= self.lower_limit and self._current_velocity_direction == self.UP:
            position = self.move_object_up(self._moving_object_image)

        self.current_y_position = position.y
        position.x = self._base_image_origin[0] + int(self._moving_object_image.get_size()[0] * 0.1)
        screen.blit(self._moving_object_image, position)
        pygame.display.update()

    def move_object_down(self, moving_object: pygame.Surface) -> pygame.Rect:
        position = moving_object.get_rect()
        self.current_y_position = self.current_y_position + self.velocity
        return position.move(0, self.current_y_position)

    def move_object_up(self, moving_object: pygame.Surface) -> pygame.Rect:
        position = moving_object.get_rect()
        self.current_y_position = self.current_y_position - self.velocity
        return position.move(0, self.current_y_position)

    def get_current_y_position(self):
        return self.current_y_position

    def stop(self):
        self.set_moving_object_new_image()
        self._moving_object_is_paused = True

    def play(self):
        self._moving_object_is_paused = False

    def pause(self, pause_time_s=3):
        self._moving_object_is_paused = True
        _pause_timer = Timer(pause_time_s, self.reset_pause_flag)
        _pause_timer.start()

    def reset_pause_flag(self):
        self._moving_object_is_paused = False

    def get_moving_object_region(self) -> int:
        if self.red_region_up[0] < self.current_y_position <= self.red_region_up[1]:
            return self.RED
        elif self.yellow_region_up[0] < self.current_y_position <= self.yellow_region_up[1]:
            return self.YELLOW
        elif self.green_region[0] <= self.current_y_position <= self.green_region[1]:
            return self.GREEN
        elif self.yellow_region_down[0] <= self.current_y_position < self.yellow_region_down[1]:
            return self.YELLOW
        elif self.red_region_down[0] <= self.current_y_position < self.red_region_down[1]:
            return self.RED
        else:
            logging.warning(f'Moving object should be inside a region. Y pos: {self.current_y_position}')
            return self.INVALID_REGION
