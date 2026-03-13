#!/bin/bash
uvicorn gpt_computer.api.main:app --reload --host 0.0.0.0 --port 8000
