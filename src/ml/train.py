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

###
# CONFIGURACIÓN INICIAL
###

# Directorio base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Rutas a modelos
DATA_PATH_2D = os.path.join(BASE_DIR, "..", "..", "data", "landmarks_2d.csv")
DATA_PATH_3D = os.path.join(BASE_DIR, "..", "..", "data", "landmarks_3d.csv")

# Ruta a modelo entrenado
MODELS_DIR = os.path.join(BASE_DIR, "..", "..", "models")


###
# ENTRENAMIENTO DEL MODELO
###

def entrenar_modelo(use_3d=False):

    # Entrenamiento dep de clasificador de gestos. 
    # Si use_3d=True, se entrena con las 63 features, si es False, con las 42 features.

    print("Cargando datos...")


    # 1. Selección del dataset
    if use_3d:
        DATA_PATH = DATA_PATH_3D
        model_name = "modelo_gestos_3d.pkl"
        print("Entrenando modelo 3D (63 features)")
    else:
        DATA_PATH = DATA_PATH_2D
        model_name = "modelo_gestos_2d.pkl"
        print("Entrenando modelo 2D (42 features)")


    # 2. Carga y preparación de datos
    if not os.path.exists(DATA_PATH):
        print(f"Error: No se encuentra {DATA_PATH}")
        return

    df = pd.read_csv(DATA_PATH, header=None)

    # Última columna = etiqueta (piedra/papel/tijera)


    X = df.iloc[:, :-1].values  # x = todas las columnas menos la última → features
    y = df.iloc[:, -1].values   # y = última columna → etiquetas

    print(f"Shape del dataset: {X.shape}")
    print(f"Número de features: {X.shape[1]}")

    if X.shape[1] == 63:
        print("Modo 3D detectado")
    elif X.shape[1] == 42:
        print("Modo 2D detectado")


    # 3. Codificación de etiquetas
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)


    # 4. División en train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )


    # 5. Entrenamiento del modelo
    print(f"Entrenando Random Forest con {len(X_train)} muestras...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # 6. Evaluación
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)

    print(f"Precisión del modelo: {acc*100:.2f}%")

    print("Reporte de clasificación:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    # 7. Guardado
    os.makedirs(MODELS_DIR, exist_ok=True)

    model_path = os.path.join(MODELS_DIR, model_name)

    joblib.dump(model, model_path)
    joblib.dump(le, os.path.join(MODELS_DIR, "label_encoder.pkl"))

    print(f"Modelo guardado en {model_path}")


if __name__ == "__main__":
    entrenar_modelo(use_3d=True)
