import cv2


class AccuracyMovingBar:

    def __init__(self, base_image_path: str, moving_object_image_path: str, velocity: int):
        self.base_image_path = base_image_path
        self.moving_object_image_path = moving_object_image_path
        self.velocity = velocity

    def start(self):
        _base_image = cv2.imread(self.base_image_path)
        _moving_object_image = cv2.imread(self.moving_object_image_path)

    def get_frame(self):
        pass
