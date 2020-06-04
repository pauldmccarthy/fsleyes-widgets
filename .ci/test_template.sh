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

apt install -y locales
locale-gen en_US.UTF-8
locale-gen en_GB.UTF-8
update-locale


PIPARGS="--retries 10 --timeout 30"

pip install $PIPARGS -r requirements-dev.txt
pip install $PIPARGS -r requirements.txt

# style stage
if [ "$TEST_STYLE"x != "x" ]; then pip install $PIPARGS pylint flake8; fi;
if [ "$TEST_STYLE"x != "x" ]; then flake8                           fsleyes_widgets || true; fi;
if [ "$TEST_STYLE"x != "x" ]; then pylint --output-format=colorized fsleyes_widgets || true; fi;
if [ "$TEST_STYLE"x != "x" ]; then exit 0; fi

# Run the tests.
xvfb-run -a -s "-screen 0 1920x1200x24" python setup.py test  -m "not dodgy"
