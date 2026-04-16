import cv2
import numpy as np


class UIHandler:
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (0, 0, 255)
    BLUE = (255, 100, 0)
    BLACK = (0, 0, 0)

    @staticmethod
    def draw_hud(frame, msg, score, ia_move=None, result_color=(255, 255, 255)):
        cv2.rectangle(frame, (0, 0), (640, 80), (30, 30, 30), -1)
        cv2.line(frame, (0, 80), (640, 80), (200, 200, 200), 2)

        cv2.putText(frame, f"SCORE: {score}", (20, 35),
                    cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 0), 2)
        cv2.putText(frame, msg, (20, 65),
                    cv2.FONT_HERSHEY_DUPLEX, 0.6, result_color, 1)

        if ia_move:
            cv2.putText(frame, f"IA: {ia_move}", (450, 45),
                        cv2.FONT_HERSHEY_TRIPLEX, 0.9, (0, 165, 255), 2)

        cv2.rectangle(frame, (350, 120), (600, 400), (255, 255, 255), 2)
        cv2.putText(frame, "COLOCA TU MANO AQUI", (370, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        return frame

    @staticmethod
    def draw_error_screen():
        """Crea un frame negro con un aviso de error cuando la cámara falla."""
        error_frame = np.zeros((480, 640, 3), dtype="uint8")

        txt_main = "ERROR: CAMARA NO DETECTADA"
        txt_sub = "Revisa la conexion y reinicia la app"

        cv2.putText(error_frame, txt_main, (120, 220),
                    cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 255), 2)
        cv2.putText(error_frame, txt_sub, (150, 260),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        return error_frame
