#!/bin/bash

# Test runner script for PolyBus Python error handlers

echo "Running Python error handler tests..."

# Run tests with coverage and verbose output
/Users/cyscott/Library/Python/3.9/bin/pytest tests/transport/transaction/message/handlers/error/test_error_handlers.py -v --no-cov

echo "Test run completed."