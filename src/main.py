# main.py - Archivo principal del juego
# Aqui se junta todo: camara, manos, juego y base de datos

import cv2
import time
import logging

from camera import CameraManager
from game_logic import GameEngine
from ui import UIHandler
from ml.predict import predecir_gesto
from ml.processor import HandProcessor
from database import DatabaseManager

# Configuramos el logging para que guarde un archivo de log
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("gesturaai.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EmoGestureApp:
    def __init__(self):
        logger.info("Inicializando EmoGestureApp...")

        self.camera = CameraManager()
        if not self.camera.try_connect():
            logger.error("No se detecta la cámara. Revisa la conexión.")
            print("ERROR: No se detecta la cámara. Revisa la conexión.")

        self.ui = UIHandler()
        self.game = GameEngine()
        self.processor = HandProcessor()
        self.db = DatabaseManager()

        self.score = 0
        self.state = "START"
        self.msg = "Presiona ESPACIO para jugar"
        self.ia_move = None
        self.color_msg = (255, 255, 255)
        self.start_time = 0
        self.last_confianza = 0.0

        logger.info("EmoGestureApp inicializada correctamente.")

    def resolve_game(self, user_gesture, confianza=0.0):
        """Resuelve la ronda y guarda el resultado en la BD."""
        self.ia_move = self.game.get_ia_move()
        result = self.game.check_winner(user_gesture, self.ia_move)

        if result == 1:
            self.score += 1
            self.msg = f"GANASTE: {user_gesture} vs {self.ia_move}"
            self.color_msg = (0, 255, 0)
            resultado_txt = "victoria"
        elif result == -1:
            self.score -= 1
            self.msg = f"PERDISTE: {user_gesture} vs {self.ia_move}"
            self.color_msg = (0, 0, 255)
            resultado_txt = "derrota"
        else:
            self.msg = f"EMPATE: Ambos {user_gesture}"
            self.color_msg = (255, 255, 0)
            resultado_txt = "empate"

        # Guardamos la partida en SQLite
        try:
            self.db.guardar_partida(
                gesto_usuario=user_gesture,
                gesto_ia=self.ia_move,
                resultado=resultado_txt,
                confianza=confianza,
                score_acumulado=self.score
            )
        except Exception as e:
            logger.error("Error al guardar partida en BD: %s", e)

    def run(self):
        """Bucle principal del juego."""
        logger.info("Aplicación iniciada. Presiona 'q' para salir.")
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
                                self.resolve_game(
                                    res["gesto"],
                                    confianza=res["confianza"]
                                )
                            else:
                                self.msg = "Gesto no reconocido"
                                logger.warning(
                                    "Gesto no reconocido (confianza=%.2f)",
                                    res["confianza"]
                                )
                        else:
                            self.msg = "No se detecto mano"
                            logger.warning("No se detectó mano en el frame.")

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

        # Cerramos todo al salir
        logger.info("Cerrando aplicación...")
        self.db.cerrar()
        self.camera.release()
        cv2.destroyAllWindows()
        logger.info("Aplicación cerrada correctamente.")


if __name__ == "__main__":
    app = EmoGestureApp()
    app.run()
