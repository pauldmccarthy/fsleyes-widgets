#!/bin/bash

set -e

source /test.venv/bin/activate

pip install --upgrade pip wheel setuptools twine
python setup.py sdist
python setup.py bdist_wheel
twine check dist/*

PIPARGS="--retries 10 --timeout 30"

pip install dist/*.whl
pip uninstall -y fsleyes-widgets

pip install dist/*.tar.gz
pip uninstall -y fsleyes-widgets
