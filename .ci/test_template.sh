#!/bin/bash

# If running on a fork repository, we merge in the
# upstream/master branch. This is done so that merge
# requests from fork to the parent repository will
# have unit tests run on the merged code, something
# which gitlab CE does not currently do for us.
if [[ "$CI_PROJECT_PATH" != "$UPSTREAM_PROJECT" ]]; then
  git fetch upstream;
  git merge --no-commit --no-ff upstream/master;
fi;

source /test.venv/bin/activate

# All other deps can be installed as normal.
# We install test dependenciesd through pip,
# because if we let setuptools do it, it
# will build/install everything from source,
# rather than using wheels.
pip install -r requirements.txt
pip install sphinx sphinx-rtd-theme
pip install pytest pytest-cov pytest-html pytest-runner mock coverage

# style stage
if [ "$TEST_STYLE"x != "x" ]; then pip install pylint flake8; fi;
if [ "$TEST_STYLE"x != "x" ]; then flake8                           fsleyes_widgets || true; fi;
if [ "$TEST_STYLE"x != "x" ]; then pylint --output-format=colorized fsleyes_widgets || true; fi;
if [ "$TEST_STYLE"x != "x" ]; then exit 0; fi

# Run the tests.
xvfb-run python setup.py test
