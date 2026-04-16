import os
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "..", "data", "landmarks.csv")
MODELS_DIR = os.path.join(BASE_DIR, "..", "..", "models")


def entrenar_modelo():
    print("Cargando datos...")
    if not os.path.exists(DATA_PATH):
        print(f"Error: No se encuentra {DATA_PATH}")
        return

    df = pd.read_csv(DATA_PATH)
    X = df.drop(columns=["Category"]).values
    y = df["Category"].values

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )

    print(f"Entrenando Random Forest con {len(X_train)} muestras...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Precisión del modelo: {acc*100:.2f}%")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(model, os.path.join(MODELS_DIR, "modelo_gestos.pkl"))
    joblib.dump(le, os.path.join(MODELS_DIR, "label_encoder.pkl"))

    print(f"Modelo guardado en {MODELS_DIR}")


if __name__ == "__main__":
    entrenar_modelo()
