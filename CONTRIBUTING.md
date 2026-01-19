# Contributing to mgt7-pdf-to-json

Thank you for your interest in contributing to **mgt7-pdf-to-json**! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)
- [Documentation](#documentation)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/mgt7-pdf-to-json.git
   cd mgt7-pdf-to-json
   ```
3. **Add the upstream repository** as a remote:
   ```bash
   git remote add upstream https://github.com/KHolodilin/mgt7-pdf-to-json.git
   ```

## Development Setup

### Prerequisites

- Python 3.9 or higher
- `pip` package manager
- Git

### Installation

1. **Install the package in development mode**:
   ```bash
   pip install -e ".[dev]"
   ```

   This installs:
   - The package itself (`mgt7-pdf-to-json`)
   - All development dependencies (pytest, ruff, mypy, etc.)

2. **Verify the installation**:
   ```bash
   mgt7pdf2json --help
   pytest --version
   ruff --version
   ```

### Pre-commit Hooks (Optional but Recommended)

Install pre-commit hooks to automatically run checks before commits:

```bash
pip install pre-commit
pre-commit install
```

This will automatically run:
- Trailing whitespace and end-of-file fixes
- YAML, JSON, TOML validation
- Ruff linting and formatting
- MyPy type checking

## Development Workflow

### 1. Create a Branch

Always create a new branch for your work:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
# or
git checkout -b docs/your-documentation-update
```

**Branch naming conventions**:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test improvements
- `chore/` - Maintenance tasks

### 2. Make Your Changes

- Write clean, readable code
- Follow the coding standards (see below)
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

Before submitting, ensure all tests pass:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/mgt7_pdf_to_json --cov-report=term-missing

# Run specific test files
pytest tests/test_parser.py

# Run with verbose output
pytest -v
```

### 4. Check Code Quality

Run linting and formatting:

```bash
# Format code
ruff format .

# Check and fix linting issues
ruff check --fix .

# Type checking
mypy src/mgt7_pdf_to_json --ignore-missing-imports
```

### 5. Update Documentation

If you've added new features or changed existing behavior:
- Update `README.md` if necessary
- Add examples to `docs/EXAMPLES.md` if applicable
- Update `CHANGELOG.md` with your changes

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://peps.python.org/pep-0008/) with some modifications:

- **Line length**: 100 characters (configured in `pyproject.toml`)
- **Quote style**: Double quotes (`"`) for strings
- **Import organization**: Automatic sorting via Ruff

### Type Hints

- Use type hints for all function signatures and class attributes
- For Python 3.9 compatibility, use `Union` and `Optional` from `typing` instead of `|` syntax
- Use `from __future__ import annotations` at the top of files when possible

**Good**:
```python
from typing import Optional, Union
from pathlib import Path

def process_file(path: Union[str, Path]) -> Optional[dict]:
    ...
```

**Avoid** (Python 3.9 incompatible):
```python
def process_file(path: str | Path) -> dict | None:
    ...
```

### Code Formatting

We use **Ruff** for both linting and formatting:

```bash
# Auto-format code
ruff format .

# Auto-fix linting issues
ruff check --fix .
```

### Docstrings

Use Google-style docstrings:

```python
def extract_pdf(pdf_path: str) -> dict[str, Any]:
    """
    Extract text and tables from PDF.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Dictionary containing extracted text and tables

    Raises:
        FileNotFoundError: If PDF file doesn't exist
        ExtractionError: If extraction fails
    """
    ...
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `DocumentParser`)
- **Functions/Methods**: `snake_case` (e.g., `extract_text`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`)
- **Private methods**: Prefix with `_` (e.g., `_parse_value`)

## Testing Guidelines

### Test Structure

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test the full pipeline with real PDF files
- **Smoke tests**: Test basic CLI functionality

### Writing Tests

1. **Use descriptive test names**:
   ```python
   def test_extract_pdf_raises_error_for_nonexistent_file():
       ...
   ```

2. **Follow AAA pattern** (Arrange, Act, Assert):
   ```python
   def test_parse_cin_from_text():
       # Arrange
       text = "CIN: U17120DL2013PTC262515"
       
       # Act
       result = parser.parse(text)
       
       # Assert
       assert result["CIN"] == "U17120DL2013PTC262515"
   ```

3. **Use fixtures** for reusable test data:
   ```python
   @pytest.fixture
   def sample_config():
       return Config.default()
   ```

4. **Test edge cases**:
   - Empty inputs
   - Invalid inputs
   - Boundary conditions
   - Error cases

### Test Coverage

- Aim for **≥90% code coverage** for core modules
- All new code should include tests
- Integration tests should use real PDF files from `examples/` directory

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_parser.py

# Specific test
pytest tests/test_parser.py::TestKeyValueParser::test_parse_cin

# With coverage report
pytest --cov=src/mgt7_pdf_to_json --cov-report=html
```

## Commit Message Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/) format:

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Maintenance tasks
- `perf`: Performance improvements

### Examples

```bash
# Feature
feat(parser): add support for parsing board meetings

# Bug fix
fix(extractor): handle empty PDF pages correctly

# Documentation
docs(readme): add installation instructions for Windows

# Refactoring
refactor(mappers): simplify date formatting logic

# Test
test(parser): add tests for financial year parsing

# Chore
chore(deps): update pdfplumber to v0.11.0
```

### Subject Line

- Use imperative mood ("add" not "added" or "adds")
- First line should be ≤72 characters
- Don't end with a period

### Body (Optional)

- Explain the "what" and "why", not the "how"
- Wrap at 72 characters
- Reference issues: `Fixes #123` or `Closes #456`

## Pull Request Process

### Before Submitting

1. **Update your branch** with the latest changes from upstream:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Ensure all tests pass**:
   ```bash
   pytest
   ```

3. **Ensure code quality checks pass**:
   ```bash
   ruff check .
   ruff format --check .
   mypy src/mgt7_pdf_to_json --ignore-missing-imports
   ```

4. **Update CHANGELOG.md** with your changes:
   ```markdown
   ## [Unreleased]

   ### Added
   - Your new feature description

   ### Fixed
   - Bug fix description
   ```

### Submitting a Pull Request

1. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request** on GitHub:
   - Use a clear, descriptive title
   - Fill out the PR template (if available)
   - Reference related issues: `Fixes #123` or `Related to #456`
   - Describe what changes you made and why

3. **PR Checklist**:
   - [ ] All tests pass locally
   - [ ] Code follows style guidelines
   - [ ] Documentation is updated
   - [ ] CHANGELOG.md is updated
   - [ ] No merge conflicts

### PR Review Process

- Maintainers will review your PR
- Address any feedback or requested changes
- Keep your branch up to date with upstream/main
- Respond to review comments promptly

### After Approval

Once approved, a maintainer will merge your PR. Your contribution will be included in the next release!

## Documentation

### Code Documentation

- Add docstrings to all public functions and classes
- Include type hints in function signatures
- Add comments for complex logic or non-obvious behavior

### User Documentation

- Update `README.md` for user-facing changes
- Add examples to `docs/EXAMPLES.md` for new features
- Update `CHANGELOG.md` with all changes

### Documentation Style

- Use clear, concise language
- Include code examples where helpful
- Keep documentation up to date with code changes

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Minimal steps to reproduce the issue
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment**:
   - Python version
   - Operating system
   - Package version
6. **Sample PDF** (if applicable): Attach or link to a sample PDF that triggers the issue
7. **Logs**: Relevant error messages or logs

### Feature Requests

When requesting features, please include:

1. **Use Case**: Why is this feature needed?
2. **Proposed Solution**: How should it work?
3. **Alternatives**: Other solutions you've considered
4. **Additional Context**: Any other relevant information

## Getting Help

If you have questions or need help:

1. **Check existing issues** on GitHub
2. **Read the documentation**: `README.md` and `docs/EXAMPLES.md`
3. **Open a new issue** with the `question` label
4. **Start a discussion** (if available)

## Thank You!

Thank you for contributing to **mgt7-pdf-to-json**! Your contributions make this project better for everyone.

---

**Questions?** Open an issue on GitHub or contact the maintainers.
