# Contributing to efficient-context

Thank you for considering contributing to efficient-context! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How Can I Contribute?

### Reporting Bugs

Bug reports help make efficient-context better for everyone. When reporting a bug, please include:

1. A clear title and description
2. Steps to reproduce the issue
3. Expected behavior
4. Actual behavior
5. Environment details (OS, Python version, etc.)

### Suggesting Enhancements

We welcome suggestions for improvements! Please include:

1. A clear description of the enhancement
2. The rationale/use case
3. Possible implementation approaches (if any)

### Pull Requests

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes with appropriate tests
4. Ensure all tests pass
5. Submit a pull request

## Development Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment: `source venv/bin/activate` (Unix) or `venv\Scripts\activate` (Windows)
4. Install development dependencies: `pip install -e ".[dev]"`

## Testing

Run tests with pytest:

```bash
pytest
```

## Style Guide

This project follows PEP 8 with a line length of 88 characters (compatible with black).

To format code:

```bash
black .
isort .
```

## Documentation

- Update documentation for any new features or changes
- Add docstrings for classes and functions

## Contact

For questions, feel free to open an issue or contact [Biswanath Roul](https://github.com/biswanathroul).

Thank you for contributing to efficient-context!
