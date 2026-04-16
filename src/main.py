import cv2
import time

from camera import CameraManager
from game_logic import GameEngine
from ui import UIHandler
from ml.predict import predecir_gesto
from ml.processor import HandProcessor


class EmoGestureApp:
    def __init__(self):
        self.camera = CameraManager()
        if not self.camera.try_connect():
            print("ERROR: No se detecta la cámara. Revisa la conexión.")

        self.ui = UIHandler()
        self.game = GameEngine()
        self.processor = HandProcessor()
        self.score = 0
        self.state = "START"
        self.msg = "Presiona ESPACIO para jugar"
        self.ia_move = None
        self.color_msg = (255, 255, 255)
        self.start_time = 0

    def resolve_game(self, user_gesture):
        self.ia_move = self.game.get_ia_move()
        result = self.game.check_winner(user_gesture, self.ia_move)

        if result == 1:
            self.score += 1
            self.msg = f"GANASTE: {user_gesture} vs {self.ia_move}"
            self.color_msg = (0, 255, 0)
        elif result == -1:
            self.score -= 1
            self.msg = f"PERDISTE: {user_gesture} vs {self.ia_move}"
            self.color_msg = (0, 0, 255)
        else:
            self.msg = f"EMPATE: Ambos {user_gesture}"
            self.color_msg = (255, 255, 0)

    def run(self):
        print("Aplicación iniciada. Presiona 'q' para salir.")
        while True:
            frame = self.camera.get_frame()

            if frame is None:
                frame = self.ui.draw_error_screen()
            else:
                landmarks = self.processor.extract_landmarks(frame)
                if self.state == "COUNTDOWN":
                    elapsed = time.time() - self.start_time
                    if elapsed < 3:
                        self.msg = f"Lanzando en... {3 - int(elapsed)}"
                    else:
                        if landmarks:
                            res = predecir_gesto(landmarks)
                            if res["reconocido"]:
                                self.resolve_game(res["gesto"])
                            else:
                                self.msg = "Gesto no reconocido"
                        else:
                            self.msg = "No se detecto mano"

                        self.state = "START"

                frame = self.ui.draw_hud(
                    frame, self.msg, self.score, self.ia_move, self.color_msg)

            cv2.imshow("EmoGestureAI", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord(' ') and self.state == "START":
                self.state = "COUNTDOWN"
                self.start_time = time.time()
                self.ia_move = None
            elif key == ord('q'):
                break

        self.camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    app = EmoGestureApp()
    app.run()
