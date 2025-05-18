#!/bin/bash
# Set the PYTHONPATH to include the current directory
export PYTHONPATH=.
# Run uvicorn as a Python module to ensure proper import resolution
python -m uvicorn main:app --host 0.0.0.0 --port 10000
