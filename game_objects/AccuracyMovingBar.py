import logging

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

    def __init__(self, base_image_path: str, moving_object_image_path: str, velocity: int, window_size: tuple):
        # Base Image
        self.base_image_path = base_image_path
        self.moving_object_image_path = moving_object_image_path
        self._base_image_dimensions = (15, 90)
        self._base_image = pygame.image.load(self.base_image_path)
        self._base_image = pygame.transform.scale(self._base_image, self._base_image_dimensions)
        self._base_image_origin = (5, 60)

        # Moving Circle
        self._moving_object_image_dimensions = (15, 15)
        self._moving_object_image = pygame.image.load(self.moving_object_image_path)
        self._moving_object_image = pygame.transform.scale(self._moving_object_image,
                                                           self._moving_object_image_dimensions)
        self._moving_object_is_paused = False
        self.velocity = velocity
        self._current_velocity_direction = 1
        self.upper_limit = self._base_image_origin[1]
        self.lower_limit = self._base_image_origin[1] + self._base_image_dimensions[1] - 15
        print("upper_limit", self.upper_limit)
        print("lower_limit", self.lower_limit)
        self.current_y_position = int(self.lower_limit - self.upper_limit / 2)

    def start(self):
        _base_image = pygame.image.load(self.base_image_path)
        _moving_object_image = pygame.image.load(self.moving_object_image_path)

    def _update_paused(self, y_position: int, screen: pygame.surface):
        position = self._moving_object_image.get_rect()
        position.y = y_position
        position.x = self._base_image_origin[0]
        screen.blit(self._base_image, self._base_image_origin)
        screen.blit(self._moving_object_image, position)
        pygame.display.update()

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
        position.x = self._base_image_origin[0]
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

    def pause(self, pause_time_s=3):
        self._moving_object_is_paused = True
        _pause_timer = Timer(pause_time_s, self.reset_pause_flag)
        _pause_timer.start()

    def reset_pause_flag(self):
        self._moving_object_is_paused = False

    def get_moving_object_region(self) -> int:
        if self.RED_REGION_UP[0] <= self.current_y_position <= self.RED_REGION_UP[1]:
            return self.RED
        elif self.YELLOW_REGION_UP[0] <= self.current_y_position <= self.YELLOW_REGION_UP[1]:
            return self.YELLOW
        elif self.GREEN_REGION[0] <= self.current_y_position <= self.GREEN_REGION[1]:
            return self.GREEN
        elif self.YELLOW_REGION_DOWN[0] <= self.current_y_position <= self.YELLOW_REGION_DOWN[1]:
            return self.YELLOW
        elif self.RED_REGION_DOWN[0] <= self.current_y_position <= self.RED_REGION_DOWN[1]:
            return self.RED
        else:
            logging.warning(f'Moving object should be inside a region. Y pos: {self.current_y_position}')
            return self.INVALID_REGION
