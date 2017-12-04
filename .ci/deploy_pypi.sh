#!/bin/bash

pip install setuptools wheel twine
twine upload dist/*
