#Sets the default shell for executing commands as /bin/bash and specifies command should be executed in a Bash shell.
SHELL := /bin/bash

# Color codes for terminal output
COLOR_RESET=\033[0m
COLOR_CYAN=\033[1;36m
COLOR_GREEN=\033[1;32m

# Defines the targets help, install, test, lint, format, coverage, and translate as phony targets.
.PHONY: help install run test lint format coverage test-cov test-cov-html translate label-approved

#sets the default goal to help when no target is specified on the command line.
.DEFAULT_GOAL := help

#Disables echoing of commands.
.SILENT:

# Sets the variable name to the second word from the MAKECMDGOALS.
name := $(word 2,$(MAKECMDGOALS))

# Default model
MODEL ?= gpt-4o

# Defines a target named help.
help:
	@echo "Please use 'make <target>' where <target> is one of the following:"
	@echo "  help           	Return this message with usage instructions."
	@echo "  install        	Will install the dependencies using UV."
	@echo "  run <folder_name>  Runs GPT Computer on the folder with the given name."
	@echo "                   Set MODEL default is gpt-4o (e.g., make run calculator MODEL=gemini-1.5-pro)"
	@echo "  test           	Runs the unit tests."
	@echo "  test-cov       	Runs tests with coverage."
	@echo "  test-cov-html  	Runs tests with coverage and generates HTML report."
	@echo "  lint           	Runs linter and type checker."
	@echo "  format         	Formats code with ruff."
	@echo "  coverage       	Generates coverage reports."
	@echo "  translate      	Runs translation script."
	@echo "  label-approved 	Runs GitHub PR label approval script."

# Defines a target named install. This target will install the project using UV.
install: uv-install install-pre-commit farewell

# Defines a target named uv-install. This target will install the project dependencies using UV.
uv-install:
	@echo -e "$(COLOR_CYAN)Installing project with UV...$(COLOR_RESET)" && \
	uv sync

# Defines a target named install-pre-commit. This target will install the pre-commit hooks.
install-pre-commit:
	@echo -e "$(COLOR_CYAN)Installing pre-commit hooks...$(COLOR_RESET)" && \
	uv run pre-commit install

# Defines a target named farewell. This target will print a farewell message.
farewell:
	@echo -e "$(COLOR_GREEN)All done!$(COLOR_RESET)"

# Defines a target named run. This target will run GPT Computer on the folder with the given name.
run:
	@echo -e "$(COLOR_CYAN)Running GPT Computer on $(COLOR_GREEN)$(name)$(COLOR_CYAN) folder with model $(COLOR_GREEN)$(MODEL)$(COLOR_CYAN)...$(COLOR_RESET)" && \
	uv run gpt-computer main projects/$(name) --model $(MODEL)

# Runs unit tests
test:
	uv run pytest

# Counts the lines of code in the project
cloc:
	cloc . --exclude-dir=node_modules,dist,build,.mypy_cache,benchmark --exclude-list-file=.gitignore --fullpath --not-match-d='docs/_build' --by-file

# Runs tests with coverage
test-cov:
	@echo -e "$(COLOR_CYAN)Running tests with coverage...$(COLOR_RESET)" && \
	uv run bash scripts/test-cov.sh ${ARGS}

# Runs tests with coverage and HTML report
test-cov-html:
	@echo -e "$(COLOR_CYAN)Running tests with coverage and HTML report...$(COLOR_RESET)" && \
	uv run bash scripts/test-cov-html.sh ${ARGS}

# Runs comprehensive linting and type checking
lint:
	@echo -e "$(COLOR_CYAN)Running linter and type checker...$(COLOR_RESET)" && \
	uv run bash scripts/lint.sh

# Formats code with ruff
format:
	@echo -e "$(COLOR_CYAN)Formatting code...$(COLOR_RESET)" && \
	uv run bash scripts/format.sh

# Generates coverage reports
coverage:
	@echo -e "$(COLOR_CYAN)Generating coverage reports...$(COLOR_RESET)" && \
	uv run bash scripts/coverage.sh

# Runs translation script
translate:
	@echo -e "$(COLOR_CYAN)Running translation script...$(COLOR_RESET)" && \
	uv run python scripts/translate.py ${ARGS}

# Runs GitHub PR label approval script
label-approved:
	@echo -e "$(COLOR_CYAN)Running GitHub PR label approval script...$(COLOR_RESET)" && \
	uv run python scripts/label_approved.py
