import cv2


class SimpleThresholdPoseClassification:
    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32

    def __init__(self, threshold_line_y: int):
        self.threshold_line_y = threshold_line_y

    def is_kicking(self, pose_landmarks, frame) -> bool:
        height, width, channels = frame.shape
        if frame is not None:
            line_thickness = 2
            cv2.line(frame, (0, self.threshold_line_y), (width, self.threshold_line_y), (0, 255, 0),
                     thickness=line_thickness)
        left_foot_y = pose_landmarks[self.LEFT_FOOT_INDEX, 1]
        right_foot_y = pose_landmarks[self.RIGHT_FOOT_INDEX, 1]
        is_kicking = False
        if left_foot_y < self.threshold_line_y < right_foot_y or right_foot_y < self.threshold_line_y < left_foot_y:
            is_kicking = True
            if frame is not None:
                cv2.putText(frame, 'Kicking!', (20, 140), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 2)
        return is_kicking
