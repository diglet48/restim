#!/bin/bash

VENV_PATH="./venv"

if ! [ -d "$VENV_PATH" ]; then
  echo "setting up venv"
  python3 -m venv "$VENV_PATH"
fi

echo "activating venv"
. "$VENV_PATH"/bin/activate

echo "checking requirements"
python3 -m pip install -r requirements.txt

echo "starting restim"
python3 ./restim.py
