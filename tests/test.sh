#!/bin/bash
# Quick test runner script for ITM352-SwingScore
# Usage: ./tests/test.sh

cd "$(dirname "$0")/.." || exit
python3 tests/run_tests.py
