import cv2


class CameraManager:
    def __init__(self):
        self.cap = None

    def try_connect(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        return self.cap.isOpened()

    def get_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return cv2.flip(frame, 1)
        return None

    def release(self):
        if self.cap:
            self.cap.release()
