#!/bin/bash

set -e

pip install ".[doc]"
sphinx-build doc public
