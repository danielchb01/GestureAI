#!/bin/bash

echo "[1/3] Verificando Entorno Virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

echo "[2/3] Sincronizando Dependencias..."
pip install --upgrade pip -q
pip install mediapipe==0.10.11 -q
pip install -r requirements.txt -q

echo "[3/3] Iniciando Ecosistema EmoGesture AI..."

streamlit run src/dashboard.py &
python3 src/main.py

trap "kill $!" EXIT