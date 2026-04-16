import cv2
import mediapipe as mp
from ml.predict import N_FEATURES


class HandProcessor:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )

    def extract_landmarks(self, frame):
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)

        if results.multi_hand_landmarks:
            landmarks_final = []
            hand_landmarks = results.multi_hand_landmarks[0]

            for lm in hand_landmarks.landmark:
                if N_FEATURES == 63:
                    landmarks_final.extend([lm.x, lm.y, lm.z])
                else:
                    landmarks_final.extend([lm.x, lm.y])

            self.mp_draw.draw_landmarks(
                frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
            return landmarks_final  # Esto devuelve la lista de 42
        return None
