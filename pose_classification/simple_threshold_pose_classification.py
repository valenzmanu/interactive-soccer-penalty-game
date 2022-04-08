import cv2


class SimpleThresholdPoseClassification:
    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32
    NOT_KICKING = False
    KICKING = True

    def __init__(self, threshold_y: int):
        self.threshold_y = threshold_y
        self.last_state = self.NOT_KICKING

    def is_kicking(self, pose_landmarks, frame) -> bool:
        height, width, channels = frame.shape
        if frame is not None:
            thickness = 2
            cv2.line(frame, (0, self.threshold_y), (width, self.threshold_y), (0, 255, 0), thickness=thickness)
        left_foot_y = pose_landmarks[self.LEFT_FOOT_INDEX, 1]
        right_foot_y = pose_landmarks[self.RIGHT_FOOT_INDEX, 1]
        is_kicking = False
        right_foot_is_up = right_foot_y < self.threshold_y < left_foot_y
        left_foot_is_up = left_foot_y < self.threshold_y < right_foot_y
        if right_foot_is_up or left_foot_is_up:
            is_kicking = True
            if frame is not None:
                cv2.putText(frame, 'Kicking!', (20, 140), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 2)
        return is_kicking

    def detect_kick(self, pose_landmarks, frame) -> bool:
        _is_kicking = self.is_kicking(pose_landmarks, frame)
        if _is_kicking and self.last_state == self.NOT_KICKING:
            self.last_state = self.KICKING
            return self.KICKING
        elif not _is_kicking and self.last_state == self.KICKING:
            self.last_state = self.NOT_KICKING
        return self.NOT_KICKING
