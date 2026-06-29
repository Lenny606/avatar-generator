import cv2
from PIL import Image as PILImage

class CameraService:
    def __init__(self, device_index=0):
        self.device_index = device_index
        self.cap = cv2.VideoCapture(self.device_index)
        self.last_frame = None
        
        # Načtení Haarova klasifikátoru pro detekci obličejů
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def is_opened(self):
        return self.cap.isOpened()

    def get_frame(self, draw_faces=False):
        """Přečte snímek z kamery a vrátí jej jako PIL Image."""
        if not self.cap.isOpened():
            return None
        ret, frame = self.cap.read()
        if ret:
            self.last_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).copy()
            
            display_frame = self.last_frame.copy()
            if draw_faces:
                faces = self.detect_faces(frame)
                for (x, y, w, h) in faces:
                    cv2.rectangle(display_frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            return PILImage.fromarray(display_frame)
        return None

    def detect_faces(self, frame=None):
        """Detekuje obličeje v zadaném snímku nebo v posledním zachyceném."""
        if frame is None:
            if self.last_frame is None:
                return []
            # Poslední snímek je v RGB, OpenCV potřebuje BGR (nebo grayscale) pro detekci
            frame = cv2.cvtColor(self.last_frame, cv2.COLOR_RGB2BGR)
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        return faces

    def get_last_frame_as_image(self):
        """Vrátí poslední zachycený snímek jako PIL Image."""
        if self.last_frame is not None:
            return PILImage.fromarray(self.last_frame)
        return None

    def release(self):
        """Uvolní prostředky kamery."""
        if self.cap.isOpened():
            self.cap.release()
