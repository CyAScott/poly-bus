# PolyBus Python

A Python implementation of the PolyBus messaging library, providing a unified interface for message transport across different messaging systems.

## Prerequisites

- [Python 3.8+](https://www.python.org/downloads/) (supports Python 3.8-3.12)
- pip (Python package installer)
- Any IDE that supports Python development (VS Code, PyCharm, etc.)

## Quick Start

### Setting Up Development Environment

```bash
# Navigate to the python directory
cd src/python

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in development mode with dev dependencies
./dev.sh install
# Or manually:
pip install -e ".[dev]"
```

### Building the Project

```bash
# Install dependencies and package
./dev.sh install

# Build the package
./dev.sh build
```

### Running Tests

```bash
# Run all tests
./dev.sh test
# Or: python -m pytest

# Run tests with coverage
./dev.sh test-cov
# Or: python -m pytest --cov=poly_bus --cov-report=html

# Run specific test files
python -m pytest tests/test_poly_bus.py

# Run tests with verbose output
python -m pytest -v

# Run tests matching a pattern
python -m pytest -k "test_pattern"
```

## Development Workflow

### Code Quality and Linting

This project includes comprehensive code analysis and formatting tools:

```bash
# Run the complete development check suite
./dev.sh check

# Format code automatically
./dev.sh format

# Run linters only
./dev.sh lint

# Individual tools:
python -m black src tests          # Code formatting
python -m isort src tests          # Import sorting
python -m flake8 src tests         # Style checking
python -m mypy src                 # Type checking
```

### IDE Integration

#### Visual Studio Code
1. Install the Python extension
2. Install Python development extensions (Black, isort, Flake8, mypy)
3. Open the `src/python` folder in VS Code
4. The project includes configuration for auto-formatting and linting

#### PyCharm
1. Open the `src/python` folder as a project
2. Configure the virtual environment as the project interpreter
3. Enable code inspections and formatting tools

## Configuration

### Project Configuration

The project uses `pyproject.toml` for modern Python packaging:

- **Python Version**: 3.8+ (supports 3.8-3.12)
- **Build System**: setuptools
- **Testing**: pytest with coverage
- **Code Quality**: black, isort, flake8, mypy
- **Package Structure**: src layout

### Code Style

Code style is enforced through:
- **Black** (88 character line length)
- **isort** (import sorting with black profile)
- **flake8** (PEP 8 compliance)
- **mypy** (type checking with strict settings)

### Testing Configuration

Pytest configuration includes:
- Coverage reporting (HTML, XML, terminal)
- Strict marker and config validation
- Support for async tests (pytest-asyncio)
- Test discovery patterns

## Dependencies

### Runtime Dependencies
- No runtime dependencies (pure Python implementation)

### Development Dependencies
- `pytest>=7.0.0` - Testing framework
- `pytest-cov>=4.0.0` - Coverage reporting
- `pytest-asyncio>=0.21.0` - Async test support
- `black>=23.0.0` - Code formatting
- `isort>=5.12.0` - Import sorting
- `flake8>=6.0.0` - Style checking
- `mypy>=1.0.0` - Type checking

## Common Commands

```bash
# Development script commands
./dev.sh install     # Install in development mode
./dev.sh test         # Run tests
./dev.sh test-cov     # Run tests with coverage
./dev.sh lint         # Run all linters
./dev.sh format       # Format code
./dev.sh check        # Run all checks (format + lint + test)
./dev.sh clean        # Clean build artifacts
./dev.sh build        # Build package
./dev.sh help         # Show all available commands

# Direct pytest commands
python -m pytest                             # Run all tests
python -m pytest --cov-report=html           # Generate HTML coverage report
python -m pytest tests/example.py            # Run specific test file
python -m pytest -x                          # Stop on first failure
python -m pytest --lf                        # Run last failed tests only

# Package management
pip install -e ".[dev]"                      # Install in development mode
pip install -r requirements-dev.txt          # Install dev dependencies only
python -m build                              # Build wheel and source distribution
```

## Troubleshooting

### Environment Issues

1. **Python Version**: Ensure Python 3.8+ is installed
   ```bash
   python3 --version
   ```

2. **Virtual Environment**: Always use a virtual environment
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Package Installation Issues**: Upgrade pip and setuptools
   ```bash
   pip install --upgrade pip setuptools wheel
   ```

### Test Issues

1. **Import Errors**: Ensure package is installed in development mode
   ```bash
   pip install -e ".[dev]"
   ```

2. **Coverage Issues**: Check that source paths are correct in `pyproject.toml`

3. **Type Checking Issues**: mypy configuration is strict; add type annotations as needed

### Code Quality Issues

1. **Formatting**: Run `./dev.sh format` to auto-fix most formatting issues
2. **Import Order**: isort will automatically fix import ordering
3. **Type Errors**: Add proper type annotations for mypy compliance

## Contributing

1. Follow the established code style (enforced by formatters and linters)
2. Run `./dev.sh check` before committing
3. Ensure all tests pass and maintain high coverage
4. Add tests for new functionality
5. Add type annotations for all new code
6. Update documentation as needed

## Coverage Reports

After running tests with coverage (`./dev.sh test-cov`):
- **Terminal**: Coverage summary displayed in terminal
- **HTML**: Detailed report available in `htmlcov/index.html`
- **XML**: Machine-readable report in `coverage.xml`

## Additional Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [pytest Documentation](https://docs.pytest.org/)
- [Black Code Formatter](https://black.readthedocs.io/)
- [mypy Type Checking](https://mypy.readthedocs.io/)

## License

See the main project LICENSE file for licensing information.