#!/usr/bin/env bash

set -e
set -x

mypy gpt_computer
ty check gpt_computer
ruff check gpt_computer tests docs scripts
ruff format gpt_computer tests --check
