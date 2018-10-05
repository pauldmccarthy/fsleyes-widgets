#!/bin/bash

pip install -r requirements-dev.txt
python setup.py doc
mv doc/html doc/"$CI_COMMIT_REF_NAME"
