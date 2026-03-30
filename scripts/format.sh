#!/usr/bin/env bash
set -x

ruff check gpt_computer tests docs scripts --fix
ruff format gpt_computer tests docs scripts
