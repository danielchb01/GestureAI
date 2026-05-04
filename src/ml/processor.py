import cv2
import mediapipe as mp
from ml.predict import N_FEATURES


class HandProcessor:
    def __init__(self, use_3d=False):
        
        # Inicializamos MediaPipe Hands y configuramos el 2D/3D
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )

        # Controla si usamos 42 o 63 features
        self.use_3d = use_3d

    def extract_landmarks(self, frame):

        # Recibimos un frame de la cámara y devuelve:
        # - Lista de 42 o 63 features (x,y o x,y,z)
        # - None si no se detecta mano

        # 1. Convertir imagen a RGB
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 2. Procesar con MediaPipe
        results = self.hands.process(img_rgb)

        # 3. Si hay mano detectada
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]

            landmarks_final = []

            # Normalización base (muñeca)
            base_x = hand_landmarks.landmark[0].x
            base_y = hand_landmarks.landmark[0].y
            base_z = hand_landmarks.landmark[0].z

            # 4. Extraer las coordenadas de cada landmark
            for lm in hand_landmarks.landmark:

                # Normalizamos para eliminar posición absoluta
                x = lm.x - base_x
                y = lm.y - base_y

                landmarks_final.extend([x, y])

                # Añadimos Z solo si usamos 3D
                if self.use_3d:
                    z = lm.z - base_z
                    landmarks_final.append(z)

            # 5. Dibujar landmarks en pantalla (visual)
            self.mp_draw.draw_landmarks(
                frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
            )

            # 6. Devolver la lista de features
            return landmarks_final  
        
        # 7. Si no se detecta mano, devolvemos None
        return None


