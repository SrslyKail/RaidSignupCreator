#! /usr/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd "$SCRIPT_DIR"
git pull
VENV_DIR=".venv/bin/activate"
if ! [ -d "$VENV_DIR"]; then python -m venv $VENV_DIR; fi
source .venv/bin/activate
python -m pip install -r requirements.txt -q
python RaidSignupCreator.py
deactivate
