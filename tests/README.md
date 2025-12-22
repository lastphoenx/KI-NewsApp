# Manual Tests

This directory contains manual test scripts for development and debugging purposes.

## Available Tests

### `manual_test_setup.py`
Tests basic setup and configuration:
- Database connectivity
- Template loading
- API keys validation
- LLM module imports

**Usage:**
```bash
python tests/manual_test_setup.py
```

### `manual_test_api.py`
Tests API endpoint for run creation:
- Creates a test run via POST /runs
- Checks response status and content

**Prerequisites:** API server must be running

**Usage:**
```bash
python tests/manual_test_api.py
```

## Note

These are **not** automated unit tests. For proper test automation with pytest, create tests with `test_*.py` naming in this directory.
