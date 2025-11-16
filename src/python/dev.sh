#!/bin/bash

# Development script for poly-bus Python project
# Usage: ./dev.sh [command]

set -e

PYTHON=${PYTHON:-python3}
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$PROJECT_DIR"

case "${1:-help}" in
    "install")
        echo "Installing poly-bus in development mode..."
        $PYTHON -m pip install --upgrade pip setuptools wheel
        $PYTHON -m pip install -e ".[dev]"
        ;;
    "test")
        echo "Running tests..."
        $PYTHON -m pytest
        ;;
    "test-cov")
        echo "Running tests with coverage..."
        $PYTHON -m pytest --cov=src --cov-report=html --cov-report=term
        ;;
    "lint")
        echo "Running linters..."
        echo "  - flake8..."
        $PYTHON -m flake8 src tests
        echo "  - mypy..."
        $PYTHON -m mypy src
        echo "Linting complete!"
        ;;
    "format")
        echo "Formatting code..."
        $PYTHON -m black src tests
        $PYTHON -m isort src tests
        echo "Formatting complete!"
        ;;
    "check")
        echo "Running all checks..."
        ./dev.sh format
        ./dev.sh lint
        ./dev.sh test-cov
        echo "All checks passed!"
        ;;
    "clean")
        echo "Cleaning build artifacts..."
        rm -rf build/ dist/ *.egg-info/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/
        find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
        echo "Clean complete!"
        ;;
    "build")
        echo "Building package..."
        $PYTHON -m pip install --upgrade build
        $PYTHON -m build
        echo "Build complete!"
        ;;
    "help"|*)
        echo "poly-bus development script"
        echo ""
        echo "Usage: ./dev.sh [command]"
        echo ""
        echo "Commands:"
        echo "  install   Install package in development mode"
        echo "  test      Run tests"
        echo "  test-cov  Run tests with coverage"
        echo "  lint      Run linters (flake8, mypy)"
        echo "  format    Format code (black, isort)"
        echo "  check     Run all checks (format, lint, test)"
        echo "  clean     Clean build artifacts"
        echo "  build     Build package"
        echo "  help      Show this help"
        ;;
esac