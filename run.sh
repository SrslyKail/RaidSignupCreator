#! /usr/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd "$SCRIPT_DIR"
git pull
source .venv/bin/activate
python -m pip install -r requirements.txt -q
python RaidSignupCreator.py -w
deactivate
