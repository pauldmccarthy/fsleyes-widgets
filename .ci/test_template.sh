#!/bin/bash

source /test.venv/bin/activate

PIPARGS="--retries 10 --timeout 30"

pip install ".[test,style]"

# style stage
if [ "$TEST_STYLE"x != "x" ]; then flake8                           fsleyes_widgets || true; fi;
if [ "$TEST_STYLE"x != "x" ]; then pylint --output-format=colorized fsleyes_widgets || true; fi;
if [ "$TEST_STYLE"x != "x" ]; then exit 0;                                                   fi

# Run the tests.
xvfb-run -a -s "-screen 0 1920x1200x24" pytest -m 'not dodgy'
