# 🖐️ EmoGestureAI

EmoGestureAI es un sistema inteligente de interacción hombre-máquina que combina Visión Artificial y Machine Learning para transformar la webcam en un periférico de juego. El proyecto permite jugar al clásico "Piedra, Papel o Tijera" detectando gestos en tiempo real y analizando la experiencia del usuario.

<!-- ## Objetivo del Proyecto
El objetivo principal de **EmoGestureAI** es desarrollar una aplicación interactiva que utilice la entrada de cámara en tiempo real para:
1. **Reconocimiento de Gestos:** Diseñado específicamente para jugar al clásico "Piedra, Papel o Tijera".
2. **Análisis de Estados Emocionales:** Detectar y clasificar expresiones faciales y sentimientos (alegría, sorpresa, frustración, etc.) durante el juego.
3. **Análisis de Comportamiento:** Proporcionar una correlación entre la respuesta emocional del usuario y sus patrones de juego. -->

## 👥 Integrantes y Roles
* **Javier Quiñonero González** (Data Engineer): Gestión de datasets y extracción de landmarks con MediaPipe.
* **David Bartol Cortés** (ML Engineer): Entrenamiento, validación y optimización del modelo de clasificación.
* **Daniel Chacón Bautista** (Platform Architect): Integración del sistema, motor de juego e interfaz con OpenCV.
* **Álvaro Benito Diaz**  (BI & QA Analyst): Persistencia en SQLite, métricas de rendimiento y dashboard en Streamlit.

## 🏗️ Arquitectura Resumida
El sistem opera como un pipeline secuencial de datos:

1. **Captura (Input):**: Entrada de vídeo en tiempo real mediante OpenCV.
2. **Procesamiento::** Extracción de 21 puntos clave (landmarks) de la mano con MediaPipe.
3. **Inferencia (ML):** Clasificación del gesto (Piedra/Papel/Tijera) mediante un modelo entrenado.
4. **Lógica:** Resolución de la ronda frente a la jugada aleatoria de la IA.
5. **Output:** Visualización de resultados (HUD) y persistencia de datos en SQLite para análisis posterior.

## 🛠️ Tecnologías Utilizadas
* **Lenguaje:** Python 3.10+
* **Visión Artificial:** OpenCV (Captura y UI) y MediaPipe (Landmarks).
* **Machine Learning:** Scikit-learn / TensorFlow Lite.
* **Base de Datos:** SQLite.
* **Visualización:** Streamlit

## 🚀 Cómo ejecutar
__Nota: El proyecto se encuentra actualmente en fase de desarrollo técnico.__ 

#### 1. Clonar el repositorio
````
git clone https://github.com/danielchb01/GesturaAI.git
cd GesturaAI
````
#### 2. Configurar el entorno virtual
````
python -m venv venv
# En Windows:
.\venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
````
#### 3. Instalar dependencias
````
pip install -r environment/requirements.txt
````
#### 4. Lanzar la aplicación
````
python src/main.py
````
#### 5. Lanzar el dashboard
````
streamlit run src/dashboard.py
````

## 📂 Estructura del Proyecto
El proyecto está organizado siguiendo una arquitectura modular para garantizar un código limpio y escalable:

```text
EmoGestureAI/
│
├── 📁 data/                   # Almacenamiento de datasets
│   └── 📄 landmarks.csv       # Coordenadas extraídas para entrenamiento
│
├── 📁 docs/                   # Documentación técnica y memorias
│   ├── 🖼️ arquitectura.png    # Diagrama de flujo del sistema
│   ├── 📄 Fase0.pdf           # Documentación de planificación
│   ├── 📄 Fase1.pdf           # Documentación de desarrollo inicial
|   ├── 📄 Fase2.pdf           # Primera versión 
│   └── 📄 services.py         # Scripts auxiliares de documentación
│
├── 📁 environment/            # Configuración del entorno
│   └── 📄 requirements.txt    # Dependencias (OpenCV, MediaPipe, Sklearn, etc.)
│
├── 📁 models/                 # Binarios de IA y métricas
│   ├── 🖼️ confusion_matrix.png # Resultado visual del entrenamiento
│   ├── 📦 label_encoder.pkl   # Traductor de etiquetas numéricas a texto
│   └── 📦 modelo_gestos.pkl    # Modelo RandomForest entrenado
│
└── 📁 src/                    # Código fuente (Core del proyecto)
    ├── 📁 ml/                 # Submódulo de Inteligencia Artificial
    │   ├── 📄 predict.py      # Motor de inferencia en tiempo real
    │   ├── 📄 processor.py    # Extracción de puntos con MediaPipe
    │   └── 📄 train.py        # Script de entrenamiento del modelo
    │
    ├── 📄 camera.py           # Gestión y abstracción de la Webcam
    ├── 📄 game_logic.py       # Reglas del juego y motor de estados
    ├── 📄 main.py             # Orquestador y punto de entrada principal
    └── 📄 ui.py               # Renderizado de interfaz y feedback visual

```
---
*Este proyecto se desarrolla como parte de la asignatura de **Proyecto de big data e inteligencia artificial**.*