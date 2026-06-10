@echo off

cd /d %~dp0

echo ===== CREO VENV (se non esiste) =====
py -3.11 -m venv venv

echo ===== ATTIVO VENV E INSTALL0 DIPENDENZE =====
call venv\Scripts\activate.bat

python -m pip install --upgrade pip

pip install mediapipe==0.10.9 opencv-python

echo ===== AVVIO PROGRAMMA =====
python main.py

pause