import os
import joblib
import numpy as np

###
# CONFIGURACIÓN INICIAL
###

# Directorio base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Rutas a modelos
PATH_MODELO_2D = os.path.join(BASE_DIR, "..", "..", "models", "modelo_gestos_2d.pkl")
PATH_MODELO_3D = os.path.join(BASE_DIR, "..", "..", "models", "modelo_gestos_3d.pkl")

# Ruta a encoder
PATH_ENCODER = os.path.join(BASE_DIR, "..", "..", "models", "label_encoder.pkl")


###
# CARGA DE MODELOS Y ENCODER
###

_modelo = None
MODO_3D_ACTIVO = False

# Intentamos cargar el modelo 3D, si no existe, cargamos el 2D
if os.path.exists(PATH_MODELO_3D):
    try:
        _modelo = joblib.load(PATH_MODELO_3D)
        MODO_3D_ACTIVO = True
        print(f"Modelo 3D cargado correctamente desde {PATH_MODELO_3D}")
    except Exception as e:
        print(f"Error al cargar modelo 3D: {e}")
        print(f"Pasamos modelo a 2D")
        MODO_3D_ACTIVO = False

# Si no hay modelo 3D o falla la carga, intentamos cargar el 2D
if not MODO_3D_ACTIVO:
    if not os.path.exists(PATH_MODELO_2D):
        print(f"No se encuentra el modelo en {PATH_MODELO_2D}")
        print("Modo captura activo")
        _modelo = None
    else:
        try:
            _modelo = joblib.load(PATH_MODELO_2D)
            print(f"Modelo 2D cargado correctamente desde {PATH_MODELO_2D}")
            MODO_3D_ACTIVO = False
        except Exception as e:
            raise RuntimeError(f"Error al cargar modelo 2D: {e}")

# Encoder
_encoder = joblib.load(PATH_ENCODER)


###
# CONFIGURACIÓN DE PREDICCIÓN
###

UMBRAL_CONFIANZA = 0.60
if _modelo is not None:
    N_FEATURES = _modelo.n_features_in_
else:
    N_FEATURES = None

def predecir_gesto(landmarks: list) -> dict:
    
    if _modelo is None:
        return {
            "gesto": None,
            "confianza": 0,
            "reconocido": False
        }

    # Predice el gesto usando el modelo activo (3D o 2D)
    if len(landmarks) != N_FEATURES:
        return {
            "gesto": f"Error: modelo espera {N_FEATURES}, recibido {len(landmarks)}",
            "confianza": 0,
            "reconocido": False
        }

    X = np.array(landmarks).reshape(1, -1)

    probas = _modelo.predict_proba(X)[0]

    confianza = float(np.max(probas))
    idx = int(np.argmax(probas))

    gesto = _encoder.inverse_transform([idx])[0]

    reconocido = confianza >= UMBRAL_CONFIANZA

    return {
        "gesto": gesto if reconocido else None,
        "confianza": confianza,
        "reconocido": reconocido
    }
