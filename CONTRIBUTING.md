# Contributing to mgt7-pdf-to-json

Thank you for your interest in contributing to mgt7-pdf-to-json! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Basic knowledge of Python development

### Development Setup

1. **Fork the repository** on GitHub

2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/mgt7-pdf-to-json.git
   cd mgt7-pdf-to-json
   ```

3. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. **Install development dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

5. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/mgt7_pdf_to_json --cov-report=term-missing --cov-fail-under=85

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m smoke

# Run specific test file
pytest tests/test_cli.py
```

### Code Quality Checks

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type checking
mypy src/mgt7_pdf_to_json --ignore-missing-imports

# Run all pre-commit checks
pre-commit run --all-files
```

## Development Workflow

### 1. Create a Branch

Create a feature branch from `main`:

```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test improvements

### 2. Make Changes

- Write clean, readable code
- Follow the existing code style
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 3. Commit Changes

Follow the commit message convention:

```
{type}({scope}): {subject}

{body}

Fixes #{issue_number}
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `test`: Test additions/changes
- `refactor`: Code refactoring
- `ci`: CI/CD changes
- `docs`: Documentation changes
- `chore`: Maintenance tasks

**Examples:**
```bash
git commit -m "feat(cli): add --include-stats flag

Add optional flag to include processing statistics in output JSON.

Fixes #5"
```

### 4. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Coding Standards

### Python Style

- Follow PEP 8 style guide
- Use `ruff` for formatting and linting
- Maximum line length: 100 characters
- Use type hints for all public functions
- Use Google-style docstrings

### Code Organization

- Keep functions focused and small
- Use meaningful variable and function names
- Add comments for complex logic
- Follow the existing project structure

### Type Hints

Always add type hints for public functions:

```python
def process_pdf(pdf_path: str, output_path: str | None = None) -> dict[str, Any]:
    """Process PDF and return parsed data."""
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def parse_date(date_str: str | None) -> str | None:
    """
    Parse date string in various formats.

    Args:
        date_str: Date string in DD/MM/YYYY, YYYY-MM-DD, or other formats

    Returns:
        Normalized date string in DD/MM/YYYY format, or None if parsing fails

    Example:
        >>> parse_date("15/03/2024")
        '15/03/2024'
        >>> parse_date("2024-03-15")
        '15/03/2024'
    """
    ...
```

## Testing Guidelines

### Test Coverage

- Maintain test coverage above 85%
- Add tests for all new functionality
- Test edge cases and error conditions
- Use appropriate test markers (`@pytest.mark.unit`, `@pytest.mark.integration`)

### Test Structure

```python
class TestFeatureName:
    """Test feature description."""

    def test_basic_functionality(self):
        """Test basic use case."""
        ...

    def test_edge_case(self):
        """Test edge case."""
        ...

    def test_error_handling(self):
        """Test error conditions."""
        ...
```

### Running Tests Before Committing

Always run tests before committing:

```bash
pytest
pre-commit run --all-files
```

## Pull Request Process

### Before Submitting

1. **Update version** in `pyproject.toml` (patch version bump)
2. **Run all tests** and ensure they pass
3. **Run pre-commit checks** and fix any issues
4. **Update documentation** if needed
5. **Add changelog entry** if applicable

### PR Description

Include:
- Description of changes
- Related issue number
- Testing performed
- Screenshots (if UI changes)
- Breaking changes (if any)

### Review Process

- All PRs require review before merging
- Address review comments promptly
- Ensure CI checks pass
- Keep PRs focused and reasonably sized

## Project Structure

```
mgt7-pdf-to-json/
├── src/mgt7_pdf_to_json/    # Source code
├── tests/                    # Test suite
├── examples/                 # Example PDF files
├── .github/                  # GitHub workflows and templates
├── config.example.yml        # Example configuration
└── pyproject.toml           # Project configuration
```

## Adding New Features

### Before Starting

1. **Check existing issues** to see if the feature is already requested
2. **Open an issue** to discuss the feature if it's significant
3. **Get approval** from maintainers before starting large changes

### Implementation Steps

1. Create feature branch
2. Implement feature with tests
3. Update documentation
4. Run all checks
5. Submit PR

## Reporting Bugs

### Before Reporting

1. Check if the bug is already reported
2. Try to reproduce with the latest version
3. Check if it's a known issue

### Bug Report Template

Include:
- **Description:** Clear description of the bug
- **Steps to Reproduce:** Detailed steps
- **Expected Behavior:** What should happen
- **Actual Behavior:** What actually happens
- **Environment:** OS, Python version, package version
- **Error Messages:** Full error traceback
- **Additional Context:** Any other relevant information

## Questions?

- **GitHub Issues:** For bug reports and feature requests
- **GitHub Discussions:** For questions and general discussion
- **Security Issues:** Use GitHub Security Advisories

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
