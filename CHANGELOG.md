# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-19

### Added
- Initial release of mgt7-pdf-to-json
- CLI tool `mgt7pdf2json` for converting MGT-7 and MGT-7A PDF forms to JSON
- Python library API with Pipeline and Config classes
- Support for three output mappers: `default`, `minimal`, and `db`
- Structured logging with request_id tracking (console and file)
- JSON and console logging formats
- Date-based log file naming (`DD-MM-YYYY.log`)
- Artifact management with retention policy
- Configuration via YAML files with CLI override support
- Comprehensive validation with warnings and errors
- Strict validation mode (`--strict`)
- Exit codes for automation use cases
- Custom exceptions (ExtractionError, ParsingError, ValidationError, MappingError, UnsupportedFormatError)
- Pre-commit hooks configuration
- Comprehensive test suite (unit, integration, smoke tests)
- Code coverage reporting (HTML report)
- Complete documentation:
  - README.md with usage examples
  - EXAMPLES.md with detailed usage scenarios
  - CONTRIBUTING.md with contribution guidelines
  - Technical specification document

### Features
- Extract text and tables from PDF files using pdfplumber
- Normalize and clean extracted text
- Parse structured data from MGT-7 and MGT-7A forms
- Extract company information (CIN, name)
- Extract financial data (turnover, net worth)
- Extract financial year information
- Parse board meeting data
- Support for date parsing in multiple formats (DD/MM/YYYY, DD-MM-YYYY, ISO)
- Enhanced error handling with informative messages
- Support for Python 3.9+

### Changed
- N/A (initial release)

### Fixed
- N/A (initial release)

### Security
- N/A (initial release)

---

## [Unreleased]

### Planned
- Performance optimization for large PDFs
- Enhanced parsing of additional MGT-7 sections
- Improved error recovery mechanisms
- Extended test coverage for CLI and edge cases
- Additional output mapper formats

[0.1.0]: https://github.com/KHolodilin/mgt7-pdf-to-json/releases/tag/v0.1.0
