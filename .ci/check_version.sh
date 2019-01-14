#!/bin/bash

set -e

cat fsleyes_widgets/__init__.py | egrep "^__version__ += +'$CI_COMMIT_REF_NAME' *$"
