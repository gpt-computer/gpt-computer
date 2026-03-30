#!/usr/bin/env bash

set -e
set -x

export PYTHONPATH=./docs
pytest -n auto --dist loadgroup  tests scripts/tests/ ${@}
