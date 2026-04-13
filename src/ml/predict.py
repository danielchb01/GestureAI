import numpy as np
import joblib

# Cargar el modelo y codificador una sola vez al importar
_modelo = joblib.load("models/modelo_gestos.pkl")
_encoder = joblib.load("models/label_encoder.pkl")

UMBRAL_CONFIANZA = 0.80
N_FEATURES = _modelo.n_features_in_

def predecir_gesto(landmarks: list) -> dict:
    """
    Recibe una lista de 63 floats (21 puntos x,y,z de MediaPipe)
    y devuelve el gesto predicho y el nivel de confianza.

    Returns:
        {
            "gesto": "Paper" | "Scissors" | "Stone" | None,
            "confianza": float (0.0 - 1.0),
            "reconocido": bool
        }
    """
    if len(landmarks) != N_FEATURES:
        raise ValueError(f"Se esperaban {N_FEATURES} landmarks, se recibieron {len(landmarks)}")
    
    X = np.array(landmarks).reshape(1, -1)
    probas = _modelo.predict_proba(X)[0]
    confianza = float(np.max(probas))
    idx = int(np.argmax(probas))
    gesto = _encoder.inverse_transform([idx])[0]

    if confianza < UMBRAL_CONFIANZA:
        return {"gesto": None, "confianza": confianza, "reconocido": False}
    
    return {"gesto": gesto, "confianza": confianza, "reconocido": True}


if __name__ == "__main__":
    # Test rápido con landmarks a cero (solo para verificar que carga bien)
    test = [0.0] * _modelo.n_features_in_
    resultado = predecir_gesto(test)
    print(f"Test de carga OK: {resultado}")
