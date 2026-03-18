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

## 📂 Estructura del Proyecto
El proyecto está organizado siguiendo una arquitectura modular para garantizar un código limpio y escalable:

```text
EmoGestureAI/
│
├── 📄 .gitignore              # Archivos excluidos del control de versiones
├── 📘 README.md               # Documentación general y guía de inicio
│
├── 📁 docs/                   # Documentación técnica y memoria del grado
│   └── 📄 .gitkeep            # Archivo para mantener la carpeta en Git
│
├── 📁 environment/            # Configuración del entorno de desarrollo
│   └── 📄 requirements.txt    # Dependencias (OpenCV, MediaPipe, etc.)
│
└── 📁 src/                    # Código fuente de la aplicación
    └── 📄 main.py             # Punto de entrada principal

```
---
*Este proyecto se desarrolla como parte de la asignatura de **Proyecto de big data e inteligencia artificial**.*