import pygame
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOUNDS_DIR = os.path.join(BASE_DIR, "assets", "sounds")


class SoundManager:
    def __init__(self):
        try:
            pygame.mixer.pre_init(44100, -16, 2, 2048)
            pygame.mixer.init()
            self.enabled = True
        except Exception as e:
            print(f"No se pudo inicializar el audio: {e}")
            self.enabled = False

        self.sounds = {}
        if self.enabled:
            self._load_assets()

    def _load_assets(self):

        assets = {
            "start": "start.wav",    # Al pulsar ESPACIO
            "tick": "tick.wav",      # En el 3, 2, 1
            "win": "win.wav",        # Al ganar
            "lose": "lose.wav",      # Al perder
            "tie": "tie.wav"         # Empate
        }

        for name, file in assets.items():
            full_path = os.path.join(SOUNDS_DIR, file)
            if os.path.exists(full_path):
                self.sounds[name] = pygame.mixer.Sound(full_path)
            else:
                print(f"Sonido no encontrado: {full_path}")

    def play(self, name):
        """Reproduce un sonido si está cargado."""
        if self.enabled and name in self.sounds:
            self.sounds[name].play()

    def play_music(self):
        """Reproduce la música de fondo en bucle."""
        if self.enabled:
            # if pygame.mixer.music.get_busy():
            #     return
            music_path = os.path.join(SOUNDS_DIR, "ingame.wav")
            if os.path.exists(music_path):
                try:
                    pygame.mixer.music.load(music_path)
                    pygame.mixer.music.set_volume(0.2)
                    pygame.mixer.music.play(-1)
                except Exception as e:
                    print(f"Error al cargar archivo OGG: {e}")

    def stop_music(self):
        if self.enabled:
            pygame.mixer.music.stop()
