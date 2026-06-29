import cv2
from PIL import Image as PILImage

class CameraService:
    def __init__(self, device_index=0):
        self.device_index = device_index
        self.cap = cv2.VideoCapture(self.device_index)
        self.last_frame = None

    def is_opened(self):
        return self.cap.isOpened()

    def get_frame(self):
        """Přečte snímek z kamery a vrátí jej jako PIL Image."""
        if not self.cap.isOpened():
            return None
        ret, frame = self.cap.read()
        if ret:
            self.last_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return PILImage.fromarray(self.last_frame)
        return None

    def get_last_frame_as_image(self):
        """Vrátí poslední zachycený snímek jako PIL Image."""
        if self.last_frame is not None:
            return PILImage.fromarray(self.last_frame)
        return None

    def release(self):
        """Uvolní prostředky kamery."""
        if self.cap.isOpened():
            self.cap.release()
