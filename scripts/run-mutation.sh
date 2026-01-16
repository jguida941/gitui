#!/bin/bash
# Run mutation testing using the pyproject.toml config.
# Usage: ./scripts/run-mutation.sh

set -e

echo "Running mutation tests on parser modules (see pyproject.toml)..."
mutmut run

echo ""
echo "=== Mutation Testing Results ==="
mutmut results
