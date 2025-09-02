@echo off
setlocal
set VENV_PATH=venv

if not exist "%VENV_PATH%" (
    echo setting up venv
    python -m venv "%VENV_PATH%"
)

echo activating venv
call "%VENV_PATH%\Scripts\activate.bat"

echo checking requirements
python -m pip install -r requirements.txt

echo starting restim
python restim.py
