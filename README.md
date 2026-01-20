# mgt7-pdf-to-json

[![CI](https://github.com/KHolodilin/mgt7-pdf-to-json/actions/workflows/ci.yml/badge.svg)](https://github.com/KHolodilin/mgt7-pdf-to-json/actions/workflows/ci.yml)
[![Test Coverage](https://codecov.io/gh/KHolodilin/mgt7-pdf-to-json/branch/main/graph/badge.svg)](https://codecov.io/gh/KHolodilin/mgt7-pdf-to-json)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type checking: MyPy](https://img.shields.io/badge/mypy-checked-blue.svg)](http://mypy-lang.org/)

Convert India MCA annual return PDF forms **MGT-7** and **MGT-7A** into structured **JSON**.

A Python CLI tool and library for parsing India Ministry of Corporate Affairs (MCA) annual return forms and converting them to structured JSON format with comprehensive logging and validation.

## Quickstart

### Installation

```bash
pip install -e .
```

### Basic Usage

```bash
# Convert PDF to JSON (outputs to same directory)
mgt7pdf2json input.pdf

# Convert with custom output file
mgt7pdf2json input.pdf -o output.json

# Convert with processing statistics
mgt7pdf2json input.pdf -o output.json --include-stats
```

### Python Library

```python
from mgt7_pdf_to_json import Pipeline, Config

# Quick start with defaults
config = Config.default()
pipeline = Pipeline(config)
result = pipeline.process("input.pdf", output_path="output.json")

# Access results
print(f"Form Type: {result['meta']['form_type']}")
print(f"Company: {result['data']['company']['name']}")
```

### What You Get

The tool converts PDF forms into structured JSON with:
- **Company Information**: CIN, name, registered address
- **Financial Data**: Turnover, net worth, financial year
- **Meeting Records**: Board meetings, AGM details
- **Directors Information**: Director details and changes
- **Validation**: Warnings and errors for data quality

See [Usage](#usage) section for more examples and advanced features.

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

#### Include Processing Statistics

```bash
mgt7pdf2json examples/U17120DL2013PTC262515_mgt7.pdf --include-stats -o output.json
```

Includes processing statistics (time, pages, tables, parsed fields) in the output JSON.

#### Output to Directory

```bash
mgt7pdf2json examples/U17120DL2013PTC262515_mgt7.pdf --outdir output/
```

Creates `output/U17120DL2013PTC262515_mgt7.json`.

#### Custom Logging

```bash
# Set log level
mgt7pdf2json examples/U17120DL2013PTC262515_mgt7.pdf --log-level DEBUG

# Use JSON logging format
mgt7pdf2json examples/U17120DL2013PTC262515_mgt7.pdf --log-format json

# Set custom log directory
mgt7pdf2json examples/U17120DL2013PTC262515_mgt7.pdf --log-dir custom_logs/
```

#### Fail on Warnings

```bash
mgt7pdf2json examples/U17120DL2013PTC262515_mgt7.pdf --fail-on-warnings
```

Exits with error code if any warnings are generated during processing.

#### Complete Example

```bash
mgt7pdf2json examples/U17120DL2013PTC262515_mgt7.pdf \
  --output result.json \
  --mapper minimal \
  --config config.yml \
  --log-level INFO \
  --strict \
  --include-stats
```

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

#### With Processing Statistics

```python
from mgt7_pdf_to_json import Pipeline, Config

config = Config.default()
pipeline = Pipeline(config)

# Enable statistics collection
result = pipeline.process(
    "input.pdf",
    output_path="output.json",
    include_stats=True
)

# Access statistics
if "statistics" in result.get("meta", {}):
    stats = result["meta"]["statistics"]
    print(f"Processing time: {stats['processing_total_duration_seconds']:.2f}s")
    print(f"Pages: {stats['pages_count']}")
    print(f"Tables: {stats['tables_count']}")
    print(f"Parsed fields: {stats['parsed_fields_count']}")
```

#### Processing Without Output File

```python
from mgt7_pdf_to_json import Pipeline, Config

config = Config.default()
pipeline = Pipeline(config)

# Process without saving to file (returns dict only)
result = pipeline.process("input.pdf")

# Access parsed data
form_type = result["meta"]["form_type"]
company_name = result["data"]["company"]["name"]
warnings = result["warnings"]
errors = result["errors"]
```

#### Error Handling

```python
from mgt7_pdf_to_json import Pipeline, Config
from mgt7_pdf_to_json.exceptions import UnsupportedFormatError

config = Config.default()
pipeline = Pipeline(config)

try:
    result = pipeline.process("input.pdf", output_path="output.json")
except FileNotFoundError:
    print("Input file not found")
except ValueError as e:
    if "scanned" in str(e).lower():
        print("PDF appears to be scanned. OCR required.")
    else:
        print(f"Processing error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
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

## Troubleshooting

### Common Issues

#### "Input file not found" Error

**Problem:** The tool cannot find the specified PDF file.

**Solutions:**
- Check that the file path is correct
- Use absolute path if relative path doesn't work
- Ensure the file has `.pdf` extension
- Check file permissions (must be readable)

#### "Unsupported PDF format" Error

**Problem:** The PDF appears to be scanned or image-only.

**Solutions:**
- The PDF may be a scanned document requiring OCR
- Try using OCR tools to convert scanned PDFs to text-based PDFs
- Ensure the PDF contains extractable text (not just images)

#### "Validation failed" Error (in strict mode)

**Problem:** Required fields are missing in the parsed output.

**Solutions:**
- Check if the PDF is a valid MGT-7 or MGT-7A form
- Try processing without `--strict` flag to see warnings instead
- Enable `--debug-artifacts` to inspect intermediate parsing results
- Check the `errors` array in the output JSON for details

#### Low Parsing Accuracy

**Problem:** Some fields are not parsed correctly.

**Solutions:**
- Enable `--debug-artifacts` to inspect raw extracted text
- Check the normalized text artifact to see how text was cleaned
- Review the parsed artifact to see what was extracted
- Some PDFs may have non-standard formatting

#### Memory Issues with Large PDFs

**Problem:** Processing fails or is slow with large PDF files.

**Solutions:**
- Ensure sufficient system memory
- Process files one at a time rather than in batch
- Consider splitting very large PDFs if possible

### Getting Help

1. **Check the logs:** Enable `--log-level DEBUG` for detailed information
2. **Enable artifacts:** Use `--debug-artifacts` to inspect intermediate files
3. **Review output:** Check the `warnings` and `errors` arrays in the JSON output
4. **Open an issue:** Provide the error message, PDF file type, and log output

## FAQ

### What PDF formats are supported?

Currently, the tool supports:
- **MGT-7**: Annual Return form for companies
- **MGT-7A**: Annual Return form for One Person Companies (OPC)

The PDF must contain extractable text (not scanned images).

### Can I process multiple PDFs at once?

Currently, the CLI processes one PDF at a time. For batch processing, you can:
- Use a shell script to loop through files
- Use the Python library in a loop
- Process files in parallel using Python's `multiprocessing`

### How accurate is the parsing?

Parsing accuracy depends on:
- PDF quality and formatting
- Text extraction quality
- Form structure consistency

The tool includes validation to identify missing or incorrect fields. Use `--strict` mode for production to ensure all required fields are present.

### Can I customize the output format?

Yes! You can:
- Use different mappers: `default`, `minimal`, or `db`
- Create custom mappers by extending `BaseMapper`
- Process the output JSON programmatically to transform it

### How do I handle warnings and errors?

- **Warnings:** Indicate missing optional fields or minor parsing issues
- **Errors:** Indicate missing required fields (in strict mode) or critical issues
- Use `--fail-on-warnings` to treat warnings as errors
- Check the `warnings` and `errors` arrays in the output JSON

### What are artifacts?

Artifacts are intermediate files saved during processing:
- **Raw:** Extracted text and metadata from PDF
- **Normalized:** Cleaned and normalized text
- **Parsed:** Structured parsed data
- **Output:** Final JSON output

Enable with `--debug-artifacts` for debugging parsing issues.

### How do I contribute?

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:
- Development setup
- Code style and conventions
- Testing requirements
- Pull request process

## Support

For issues and questions:
- **GitHub Issues:** [Open an issue](https://github.com/KHolodilin/mgt7-pdf-to-json/issues)
- **Security Issues:** [Report security vulnerability](https://github.com/KHolodilin/mgt7-pdf-to-json/security/advisories/new)
- **Discussions:** [Start a discussion](https://github.com/KHolodilin/mgt7-pdf-to-json/discussions)
