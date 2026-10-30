#!/bin/bash
# Test runner script for local development.
# Usage: ./run_tests.sh [--pytest]

set -e

cd "$(dirname "$0")"

if [ "${1:-}" == "--pytest" ]; then
    # Run tests with pytest (requires pytest installed).
    python3 -m pytest --ds=render_minimum.settings render_minimum/tests.py -v || true
else
    # Run Django unittests.
    python3 manage.py test render_minimum.tests -v 2
fi
