import pygame
import random


class MovingObject:

    def __init__(self, image_filename: str, moving_plane_size: tuple = None, initial_speed: list = None,
                 initial_position: list = None,
                 resize_factor=0.25):
        image = pygame.image.load(image_filename)
        image_size = image.get_size()
        self.filename = image_filename
        self.image = self._resize_image(image, image_size, resize_factor)
        self.moving_plane_size = moving_plane_size

        if initial_speed is None:
            initial_speed = [1, 1]

        rect = self.image.get_rect()
        if initial_position is not None and len(initial_position) == 2:
            rect.left = initial_position[0]
            rect.top = initial_position[1]

        self.rect = rect
        self._initial_position = rect
        self.speed = initial_speed

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        message = "filename: %s, speed: %s, rect: [%s, %s, %s, %s]" % (
            self.filename, self.speed, self.rect.top, self.rect.bottom, self.rect.right, self.rect.left)
        return message

    @staticmethod
    def _resize_image(image, image_size, resize_factor):
        x, y = image_size
        new_size = (resize_factor * x, resize_factor * y)
        return pygame.transform.scale(image, new_size)

    def reset(self):
        self.rect = self._initial_position
        self.speed = [0, random.randint(1, (self.speed[1] + 1) % 3 + 2)]

    def move(self, speed: list = None) -> list:
        if speed is None:
            _speed = self.speed
        else:
            _speed = speed
        self.rect = self.rect.move(_speed)
        return self.rect
