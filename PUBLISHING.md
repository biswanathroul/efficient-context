# Publishing to PyPI

This guide explains how to build and publish the `efficient-context` package to PyPI.

## Prerequisites

1. Create an account on PyPI: https://pypi.org/account/register/
2. Install build and twine packages:

```bash
pip install build twine
```

## Build the Package

1. Navigate to the project directory:

```bash
cd /path/to/efficient-context
```

2. Build the distribution packages:

```bash
python -m build
```

This will create a directory called `dist` containing both `.tar.gz` (source distribution) and `.whl` (built distribution) files.

## Upload to TestPyPI (Recommended)

Before publishing to the main PyPI repository, it's a good practice to test on TestPyPI:

```bash
python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

You'll be prompted for your TestPyPI username and password.

Then install from TestPyPI to verify it works:

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple efficient-context
```

## Upload to PyPI

Once you've verified everything works correctly, upload to the actual PyPI:

```bash
python -m twine upload dist/*
```

You'll be prompted for your PyPI username and password.

## Verify Installation

After uploading, verify that your package can be installed from PyPI:

```bash
pip install efficient-context
```

## Updating the Package

To update the package:

1. Update the version number in `setup.py`
2. Rebuild the package: `python -m build`
3. Upload to PyPI again: `python -m twine upload dist/*`

## GitHub Integration

If your code is hosted on GitHub, you may want to set up GitHub Actions to automatically build and publish your package when you create a new release. The code for this project is available at: https://github.com/biswanathroul/efficient-context

## Tips

- Always increment the version number in `setup.py` before publishing a new version
- Keep your PyPI credentials secure
- Include comprehensive documentation and examples in your package
- Add proper classifiers in `setup.py` for better searchability
