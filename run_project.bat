@echo off
echo [1/3] Verificando Entorno Virtual...
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate

echo [2/3] Sincronizando Dependencias...
pip install mediapipe==0.10.11 -q
pip install -r requirements.txt -q

echo [3/3] Iniciando Ecosistema EmoGesture AI...
start "Dashboard" cmd /k "call venv\Scripts\activate && streamlit run src/dashboard.py"

python src/main.py

pause