# mgt7-pdf-to-json

Convert India MCA annual return PDF forms **MGT-7** and **MGT-7A** into structured **JSON**.

A Python CLI tool and library for parsing India Ministry of Corporate Affairs (MCA) annual return forms and converting them to structured JSON format with comprehensive logging and validation.

## Features

- ✅ **CLI Tool**: Easy-to-use command-line interface
- ✅ **Python Library**: Programmatic API for integration
- ✅ **Multiple Mappers**: Support for `default`, `minimal`, and `db` output formats
- ✅ **Structured Logging**: JSON and console logging with request_id tracking
- ✅ **Artifacts**: Optional intermediate file saving for debugging
- ✅ **Validation**: Built-in validation with warnings and errors
- ✅ **Configurable**: YAML-based configuration with CLI override support
- ✅ **Production Ready**: Comprehensive error handling and exit codes

## Installation

### Basic Installation

```bash
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

This installs additional development dependencies:
- `pytest` and `pytest-cov` for testing
- `ruff` and `black` for code formatting
- `mypy` for type checking

## Usage

### CLI

#### Basic Usage

```bash
mgt7pdf2json examples/U17120DL2013PTC262515_mgt7.pdf
```

This creates `U17120DL2013PTC262515_mgt7.json` in the same directory.

#### With Output File

```bash
mgt7pdf2json examples/U17120DL2013PTC262515_mgt7.pdf -o output.json
```

#### With Custom Mapper

```bash
mgt7pdf2json examples/U17120DL2013PTC262515_mgt7.pdf --mapper minimal -o output.json
```

Available mappers:
- `default`: Full JSON output with all parsed fields
- `minimal`: Minimal output with essential fields only
- `db`: Database-friendly format with flattened structure

#### With Configuration

```bash
mgt7pdf2json examples/U17120DL2013PTC262515_mgt7.pdf --config config.yml
```

#### Enable Debug Artifacts

```bash
mgt7pdf2json examples/U17120DL2013PTC262515_mgt7.pdf --debug-artifacts
```

This saves intermediate files (raw, normalized, parsed) in `logs/artifacts/`.

#### Strict Validation

```bash
mgt7pdf2json examples/U17120DL2013PTC262515_mgt7.pdf --strict
```

Fails if any required fields are missing.

### Python Library

```python
from mgt7_pdf_to_json import Pipeline, Config

# Using default configuration
config = Config.default()
pipeline = Pipeline(config)
result = pipeline.process("input.pdf", output_path="output.json")

print(f"Form Type: {result['meta']['form_type']}")
print(f"Company CIN: {result['data']['company']['cin']}")
print(f"Warnings: {len(result['warnings'])}")
print(f"Errors: {len(result['errors'])}")
```

#### With Custom Configuration

```python
from mgt7_pdf_to_json import Pipeline, Config

# Load from YAML file
config = Config.from_yaml("config.yml")

# Or override programmatically
config.logging.level = "DEBUG"
config.artifacts.enabled = True
config.pipeline.mapper = "minimal"

pipeline = Pipeline(config)
result = pipeline.process("input.pdf")
```

## Configuration

Configuration is managed via YAML files. See `config.example.yml` for a complete example.

### Example Configuration

```yaml
logging:
  level: INFO
  format: console
  format_file: json
  file: logs
  date_format: "%d-%m-%Y"

artifacts:
  enabled: false
  dir: artifacts
  save_raw: true
  save_normalized: true
  save_parsed: true
  save_output: false
  keep_days: 7

pipeline:
  mapper: default

validation:
  strict: false
  required_fields:
    - meta.form_type
    - meta.financial_year.from
    - meta.financial_year.to
    - company.cin
    - company.name
```

## Output Format

### Default Mapper

```json
{
  "meta": {
    "request_id": "6a1d1c35-7f88-4e12-9e9f-8d3d4d1b6f5a",
    "schema_version": "1.0",
    "form_type": "MGT-7",
    "financial_year": {
      "from": "01/04/2024",
      "to": "31/03/2025"
    },
    "source": {
      "input_file": "example.pdf"
    }
  },
  "data": {
    "company": {
      "cin": "U17120DL2013PTC262515",
      "name": "TEGAN TEXOFAB PRIVATE LIMITED"
    },
    "turnover_and_net_worth": {
      "turnover_inr": 891114630,
      "net_worth_inr": 266771238
    },
    "meetings": {
      "board_meetings": [
        {
          "date": "01/04/2024",
          "directors_total": 2,
          "directors_attended": 2
        }
      ]
    }
  },
  "warnings": [],
  "errors": []
}
```

## Exit Codes

The CLI uses standard exit codes:

- `0`: Success
- `1`: Processing error (extraction/parsing/mapping/write error)
- `2`: Validation failed (in strict mode)
- `3`: Input file not found
- `4`: Unsupported format (cannot detect form type)
- `5`: Warnings as errors (`--fail-on-warnings` enabled)
- `6`: Configuration error

## Development

### Code Formatting

```bash
ruff format .
```

### Linting

```bash
ruff check --fix .
```

### Type Checking

```bash
mypy src/mgt7_pdf_to_json
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/mgt7_pdf_to_json --cov-report=term-missing

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m smoke
```

### Project Structure

```
mgt7-pdf-to-json/
├── src/
│   └── mgt7_pdf_to_json/
│       ├── __init__.py
│       ├── cli.py              # CLI interface
│       ├── config.py           # Configuration management
│       ├── pipeline.py         # Main pipeline orchestrator
│       ├── extractor.py        # PDF extraction
│       ├── normalizer.py       # Text normalization
│       ├── parser.py           # Document parsing
│       ├── mappers.py          # Output mappers
│       ├── validator.py        # JSON validation
│       ├── artifacts.py        # Artifact management
│       ├── logging_.py         # Structured logging
│       ├── models.py           # Data models
│       └── date_utils.py       # Date parsing utilities
├── tests/                      # Test suite
├── examples/                   # Example PDF files
├── docs/                       # Documentation
├── config.example.yml          # Example configuration
└── pyproject.toml              # Project configuration
```

## License

MIT

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:

- Development setup
- Coding standards
- Testing guidelines
- Commit message conventions
- Pull request process

Quick start:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Support

For issues and questions, please open an issue on the GitHub repository.
