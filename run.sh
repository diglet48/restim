PYTHON_PATH="venv/bin/python"

if ! [ -f $PYTHON_PATH ]; then
  echo "setting up venv"
  python3 -m venv venv
fi

$PYTHON_PATH -m pip install -r requirements.txt

$PYTHON_PATH ./restim.py
