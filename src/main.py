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


##
# CONFIGURACIÓN DE LOGGING
##

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


##
# CLASE PRINCIPAL
##

class EmoGestureApp:
    def __init__(self):
        logger.info("Inicializando EmoGestureApp...")

        # 1. Configuración de modo 3D o 2D (depende de qué modelo se cargue)
        self.use_3d = True

        logger.info(f"Modo de features: {'3D (63)' if self.use_3d else '2D (42)'}")

        # 2. Inicialización de componentes
        #Cámara
        self.camera = CameraManager()

        # Intentamos conectar con la cámara al inicio para detectar problemas temprano
        if not self.camera.try_connect():
            logger.error("No se detecta la cámara. Revisa la conexión.")
            print("ERROR: No se detecta la cámara. Revisa la conexión.")

        self.ui = UIHandler()                               # UI (dibujos en pantalla)
        self.game = GameEngine()                            # Lógica del juego (piedra-papel-tijera)
        self.processor = HandProcessor(use_3d=self.use_3d)  # Procesador de manos (MediaPipe)
        self.db = DatabaseManager()                         # Base de datos (SQLite)

        # 3. Variables de estado
        self.score = 0                              # Puntuación del jugador
        self.state = "START"                        # Estado del juego
        self.msg = "Presiona ESPACIO para jugar"    
        self.ia_move = None                         # Jugada de la IA
        self.color_msg = (180, 180, 180)            # Color del mensaje
        self.start_time = 0                         # Tiempo inicio cuenta atrás
        self.last_confianza = 0.0                   # Última confianza de predicción
        self.result_time = 0
        self.RESULT_DELAY = 1.5                     # segundos de pausa entre rondas
        self.victorias = 0
        self.derrotas = 0
        self.empates = 0

        logger.info("EmoGestureApp inicializada correctamente.")


    ##
    # LÓGICA DE JUEGO
    ##
    def resolve_game(self, user_gesture, confianza=0.0):
        """Resuelve la ronda y guarda el resultado en la BD."""
        self.ia_move = self.game.get_ia_move()                          # Jugada de la IA
        result = self.game.check_winner(user_gesture, self.ia_move)     # Resultado del enfrentamiento

        # Resultados
        if result == 1:
            self.score += 1
            self.victorias += 1
            self.msg = f"GANASTE ({confianza:.2f}): {user_gesture} vs {self.ia_move}"
            self.color_msg = (0, 255, 0)
            resultado_txt = "victoria"
        elif result == -1:
            self.score -= 1
            self.derrotas += 1
            self.msg = f"PERDISTE ({confianza:.2f}): {user_gesture} vs {self.ia_move}"
            self.color_msg = (0, 0, 255)
            resultado_txt = "derrota"
        else:
            self.empates += 1
            self.msg = f"EMPATE ({confianza:.2f}): Ambos {user_gesture}"
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

    ##
    # BUCLE PRINCIPAL
    ##
    def run(self):
        """Bucle principal del juego."""
        logger.info("Aplicación iniciada. Presiona 'q' para salir.")
        print("Aplicación iniciada. Presiona 'q' para salir.")

        # 1. Captura del frame
        while True:
            frame = self.camera.get_frame()

            if frame is None:
                frame = self.ui.draw_error_screen()
            else:

                # 2. Detección de landmarks
                h, w, _ = frame.shape

                # Zona de detección (sólo al estar jugando, no en GAME_OVER)
                if self.state != "GAME_OVER":
                    x1, y1 = int(w * 0.3), int(h * 0.2)
                    x2, y2 = int(w * 0.7), int(h * 0.8)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
                    
                    #Oscurecemos el exterior de la zona de detección para guiar al usuario
                    overlay = frame.copy()

                    # Oscurecemos toda la imagen
                    cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)

                    # Restauramos la zona de detección (no oscurecida)
                    overlay[y1:y2, x1:x2] = frame[y1:y2, x1:x2]

                    # Mezclamos
                    alpha = 0.6  # intensidad del oscurecido
                    frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

                if self.state != "GAME_OVER":
                    landmarks = self.processor.extract_landmarks(frame)
                else:
                    landmarks = None
                    
                if landmarks:
                    logger.debug(f"Features detectadas: {len(landmarks)}")

                # 3. Lógica de juego
                if self.state == "COUNTDOWN":
                    elapsed = time.time() - self.start_time

                    if elapsed < 3:
                        # self.msg = f"Lanzando en... {3 - int(elapsed)}"
                        count = 3 - int(elapsed)
                        self.msg = f"{count}..."
                        self.color_msg = (255, 255, 255)

                    else:

                        # 4. Predicción del gesto 
                        if landmarks:
                            
                            res = predecir_gesto(landmarks)

                            # Traducción de gestos
                            MAP_GESTOS = {
                                "piedra": "Stone",
                                "papel": "Paper",
                                "tijera": "Scissor"
                            }

                            if res["reconocido"]:
                                gesto_traducido = MAP_GESTOS.get(res["gesto"], None)

                                if gesto_traducido:
                                    self.resolve_game(
                                        gesto_traducido,
                                        confianza=res["confianza"]
                                    )
                                else:
                                    self.msg = "Gesto desconocido"
                                    self.color_msg = (0, 165, 255)
                            
                            else:
                                self.msg = f"No reconocido ({res['confianza']:.2f})"
                                self.color_msg = (0, 165, 255)
                                logger.warning(
                                    "Gesto no reconocido (confianza=%.2f)",
                                    res["confianza"]
                                )
                        else:
                            self.msg = "No se detecta la mano"
                            self.color_msg = (0, 0, 255)
                            logger.warning("No se detectó mano en el frame.")

                        # Volvemos al estado inicial
                        self.state = "RESULT"
                        self.result_time = time.time()

                elif self.state == "RESULT":
                    if time.time() - self.result_time > self.RESULT_DELAY:
                        self.state = "COUNTDOWN"
                        self.start_time = time.time()
                        self.ia_move = None
                        self.msg = " "

                elif self.state == "GAME_OVER":

                    # Oscurecer pantalla para ver que el juego ha terminado
                    overlay = frame.copy()
                    cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
                    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

                    total = self.victorias + self.derrotas + self.empates

                    if total > 0:
                        winrate = (self.victorias / total) * 100
                    else:
                        winrate = 0

                    self.msg = f"FinalScore: {self.score}"
                    self.color_msg = (255, 255, 255)
                    start_y = int(h * 0.35)

                    # Estadísticas
                    cv2.putText(frame, f"Victorias: {self.victorias}",  (int(w*0.35), start_y),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                    cv2.putText(frame, f"Derrotas: {self.derrotas}", (int(w*0.35), start_y + 40),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                    cv2.putText(frame, f"Empates: {self.empates}", (int(w*0.35), start_y + 80),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

                    cv2.putText(frame, f"Winrate: {winrate:.1f}%", (int(w*0.35), start_y + 120),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                    # Instrucciones
                    cv2.putText(frame, "Pulsa R para reiniciar", (10, h - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)


                # 5. Dibujamos HUD (puntuación, mensajes, IA, etc)
                #frame = self.ui.draw_hud(
                #    frame, self.msg, self.score, self.ia_move, self.color_msg)

                # Título
                cv2.putText(frame, "EmoGesture AI", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

                # Score
                cv2.putText(frame, f"Score: {self.score}", (10, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

                # Mensaje centrado
                (tw, th), _ = cv2.getTextSize(self.msg,
                                             cv2.FONT_HERSHEY_SIMPLEX, 1, 2)

                x = int((w - tw) / 2)
                y = int(h * 0.9)

                cv2.putText(frame, self.msg, (x, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 1,
                            self.color_msg, 2)
                    

            # 6. Mostramos el frame resultante
            cv2.imshow("EmoGestureAI", frame)

            # 7. Control de teclas
            key = cv2.waitKey(1) & 0xFF

            # Al pulsar 'Espacio'
            if key == ord(' '):
                if self.state == "START": # Solo iniciamos el juego si estamos en estado START
                    self.state = "COUNTDOWN"
                    self.start_time = time.time()
                    self.ia_move = None
                    self.msg = " "

                elif self.state in ["COUNTDOWN", "RESULT"]: #Si estamos en una partida, termina la partida
                        self.state = "GAME_OVER"
                        self.color_msg = (255, 255, 255)

            # Salir de la partida
            elif key == ord('q'):
                break

            # Reiniciar partida
            elif key == ord('r') and self.state == "GAME_OVER":
                self.score = 0
                self.victorias = 0
                self.derrotas = 0
                self.empates = 0
                self.state = "START"
                self.msg = "Pulsa ESPACIO para empezar"

        # 8. Cerramos todo al salir
        logger.info("Cerrando aplicación...")

        self.db.cerrar()
        self.camera.release()
        cv2.destroyAllWindows()

        logger.info("Aplicación cerrada correctamente.")


##
# EJECUCIÓN PRINCIPAL
##
if __name__ == "__main__":
    app = EmoGestureApp()
    app.run()
