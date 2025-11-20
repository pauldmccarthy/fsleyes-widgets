#!/bin/bash

set -e

pip install  dist/*.whl

exp=${CI_COMMIT_REF_NAME}
got=$(python -c "import fsleyes_widgets as w;print(w.__version__)")

if [[ ${exp} == ${got} ]]; then
  exit 0
else
  exit 1
fi
