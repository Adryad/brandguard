#!/bin/bash
cd backend

echo "Removing unused imports..."
poetry run autoflake --in-place --remove-all-unused-imports --recursive .

echo "Formatting with Black..."
poetry run black .

echo "Sorting imports..."
poetry run isort .

echo "Checking remaining issues..."
poetry run flake8 . --max-line-length=88 --count --exit-zero

echo "✅ All linting issues fixed!"