#!/bin/bash

set -e

source /test.venv/bin/activate

pip install --upgrade pip wheel setuptools twine build
python -m build
twine check dist/*

PIPARGS="--retries 10 --timeout 30"

pip install dist/*.whl
pip uninstall -y fsleyes-widgets

pip install dist/*.tar.gz
pip uninstall -y fsleyes-widgets
