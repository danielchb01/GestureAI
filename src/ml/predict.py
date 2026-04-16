import os
import joblib
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_MODELO = os.path.join(BASE_DIR, "..", "..", "models", "modelo_gestos.pkl")
PATH_ENCODER = os.path.join(
    BASE_DIR, "..", "..", "models", "label_encoder.pkl")

if not os.path.exists(PATH_MODELO):
    raise FileNotFoundError(f"No se encuentra el modelo en {PATH_MODELO}")

_modelo = joblib.load(PATH_MODELO)
_encoder = joblib.load(PATH_ENCODER)

UMBRAL_CONFIANZA = 0.50
N_FEATURES = _modelo.n_features_in_


def predecir_gesto(landmarks: list) -> dict:
    if len(landmarks) != N_FEATURES:
        return {
            "gesto": f"Error: modelo espera {N_FEATURES}",
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
