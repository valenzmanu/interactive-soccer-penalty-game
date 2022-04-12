import pygame


class AccuracyMovingBar:
    DOWN = 1
    UP = -1

    def __init__(self, base_image_path: str, moving_object_image_path: str, velocity: int, window_size: tuple):
        # Base Image
        self.base_image_path = base_image_path
        self.moving_object_image_path = moving_object_image_path
        self._base_image_dimensions = (30, 300)
        self._base_image = pygame.image.load(self.base_image_path)
        self._base_image = pygame.transform.scale(self._base_image, self._base_image_dimensions)
        self._base_image_origin = (20, 100)

        # Moving Circle
        self._moving_object_image_dimensions = (40, 40)
        self._moving_object_image = pygame.image.load(self.moving_object_image_path)
        self._moving_object_image = pygame.transform.scale(self._moving_object_image,
                                                           self._moving_object_image_dimensions)
        self.velocity = velocity
        self._current_velocity_direction = 1
        self.upper_limit = self._base_image_origin[1]
        self.lower_limit = self._base_image_origin[1] + self._base_image_dimensions[1] - 35
        print("upper_limit", self.upper_limit)
        print("lower_limit", self.lower_limit)
        self.current_y_position = int(self.lower_limit - self.upper_limit / 2)

    def start(self):
        _base_image = pygame.image.load(self.base_image_path)
        _moving_object_image = pygame.image.load(self.moving_object_image_path)

    def update(self, screen: pygame.Surface):
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
        position.x = self._base_image_origin[0] - 5
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
