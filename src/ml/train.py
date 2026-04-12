import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# --- 1. Cargar el dataset ---
df = pd.read_csv("data/landmarks.csv")

print(f"Shape del dataset: {df.shape}")
print(f"\nDistribución de clases:\n{df['Category'].value_counts()}")
print(f"\nValores nulos:\n{df.isnull().sum().sum()}")

# --- 2. Separar características y etiquetas ---
X = df.drop(columns=["Category"]).values
y = df["Category"].values

# Codificar etiquetas (Piedra/Papel/Tijera -> 0/1/2)
le = LabelEncoder()
y_encoded = le.fit_transform(y)
print(f"\nClases detectadas: {le.classes_}")

# --- 3. Dividir en conjunto de entrenamiento y prueba ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)
print(f"\nEntrenamiento: {X_train.shape[0]} muestras | Prueba: {X_test.shape[0]} muestras")

# --- 4. Entrenar modelos ---
modelos = {
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
    "SVM": SVC(kernel="rbf", probability=True, random_state=42),
}

resultados = {}
for nombre, modelo in modelos.items():
    print(f"\nEntrenando: {nombre}...")
    modelo.fit(X_train, y_train)
    y_pred = modelo.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    resultados[nombre] = {"modelo": modelo, "accuracy": acc, "y_pred": y_pred}
    print(f"Accuracy: {acc:.4f} ({acc*100:.2f}%)")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

# --- 5. Elegir el mejor modelo ---
mejor_nombre = max(resultados, key=lambda k: resultados[k]["accuracy"])
mejor = resultados[mejor_nombre]
print(f"\n Mejor modelo: {mejor_nombre} ({mejor['accuracy']*100:.2f}%)")

# --- 6. Matriz de confusión ---
cm = confusion_matrix(y_test, mejor["y_pred"])
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=le.classes_, yticklabels=le.classes_)
plt.title(f"Matriz de confusión - {mejor_nombre}")
plt.ylabel("Real")
plt.xlabel("Predicho")
plt.tight_layout()
plt.savefig("models/confusion_matrix.png")
plt.show()
print("Matriz guardada en models/confusion_matrix.png")

# --- 7. Guardar el modelo y el codificador ---
joblib.dump(mejor["modelo"], "models/modelo_gestos.pkl")
joblib.dump(le, "models/label_encoder.pkl")
print(f"Modelo guardado en models/modelo_gestos.pkl")
print(f"Codificador guardado en models/label_encoder.pkl")
