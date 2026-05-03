import cv2
import numpy as np


class UIHandler:
    RETRO_GREEN = (0, 255, 65)   # Verde fósforo
    RETRO_PINK = (255, 0, 255)    # Rosa neón
    RETRO_AMBER = (0, 191, 255)   # Naranja/Ámbar
    BLACK = (0, 0, 0)
    WHITE = (220, 220, 220)

    @staticmethod
    def draw_menu(frame):
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0),
                      (frame.shape[1], frame.shape[0]), (15, 15, 15), -1)
        cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
        cv2.putText(frame, ">> EMO GESTURE AI <<", (60, 200),
                    cv2.FONT_HERSHEY_TRIPLEX, 1.2, UIHandler.RETRO_GREEN, 2)
        cv2.putText(frame, "INSERT COIN: [PRESS SPACE]", (140, 300),
                    cv2.FONT_HERSHEY_PLAIN, 1.5, UIHandler.RETRO_PINK, 2)
        cv2.putText(frame, "EXIT: [PRESS Q]", (230, 360),
                    cv2.FONT_HERSHEY_PLAIN, 1.2, UIHandler.WHITE, 1)
        return frame

    @staticmethod
    def draw_hud(frame, msg, score, ia_move=None, result_color=(0, 255, 65)):
        """HUD más robusto y espaciado."""
        cv2.rectangle(frame, (0, 0), (640, 75), (10, 10, 10), -1)
        cv2.line(frame, (0, 75), (640, 75), UIHandler.RETRO_GREEN, 2)

        cv2.putText(frame, f"1P SCORE: {str(score).zfill(4)}", (25, 45),
                    cv2.FONT_HERSHEY_PLAIN, 1.8, UIHandler.RETRO_GREEN, 2)

        if ia_move:
            text_ia = f"CPU: {ia_move.upper()}"
            cv2.putText(frame, text_ia, (440, 45),
                        cv2.FONT_HERSHEY_PLAIN, 1.8, UIHandler.RETRO_PINK, 2)

        cv2.putText(frame, msg.upper(), (32, 442),
                    cv2.FONT_HERSHEY_PLAIN, 1.6, (0, 0, 0), 3)
        cv2.putText(frame, msg.upper(), (30, 440),
                    cv2.FONT_HERSHEY_PLAIN, 1.6, result_color, 2)

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
