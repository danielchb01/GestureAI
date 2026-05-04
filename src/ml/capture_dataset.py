import cv2
import os
import time
from src.ml.processor import HandProcessor

##
# CONFIGURACIÓN
##

OUTPUT = "data/landmarks_3d.csv"

# Guardado
last_save = 0
COOLDOWN = 0.5  # segundos

# Mapeo de teclas a etiquetas
LABELS = {
    ord('1'): "piedra",
    ord('2'): "papel",
    ord('3'): "tijera"
}

current_label = "piedra"  # etiqueta inicial

# Inicializamos cámara
cap = cv2.VideoCapture(0)

# Procesador (3D)
processor = HandProcessor(use_3d=True)

os.makedirs("data", exist_ok=True)

print("Controles:")
print("1 = piedra | 2 = papel | 3 = tijera")
print("ESPACIO = guardar muestra | q = salir")

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1) # Corregir efecto espejo
    if not ret:
        break

    # Detectamos landmarks
    landmarks = processor.extract_landmarks(frame)

    ##
    # UI VISUAL
    ##

    # Mostrar etiqueta actual
    cv2.putText(frame, f"Label: {current_label}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    if landmarks:
        cv2.putText(frame, "MANO DETECTADA", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    else:
        cv2.putText(frame, "SIN MANO", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Captura Dataset", frame)

    ##
    # CONTROL TECLADO
    ##

    key = cv2.waitKey(1) & 0xFF

    # Cambiar etiqueta
    if key in LABELS:
        current_label = LABELS[key]
        print(f"Etiqueta cambiada a: {current_label}")

    # Guardar muestra
    elif key == ord(' ') and landmarks:
        now = time.time()
        if now - last_save > COOLDOWN:
            with open(OUTPUT, "a") as f:
                f.write(",".join(map(str, landmarks)) + f",{current_label}\n")
            print(f"Muestra guardada ({current_label})")
        last_save = now

    # Salir
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()