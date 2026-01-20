"""Pytest configuration and fixtures."""

from pathlib import Path

import pytest
from mgt7_pdf_to_json.config import Config


@pytest.fixture
def config() -> Config:
    """Default test configuration."""
    return Config.default()


@pytest.fixture
def examples_dir() -> Path:
    """Path to examples directory."""
    return Path(__file__).parent.parent / "examples"


@pytest.fixture
def mgt7_pdf_path(examples_dir: Path) -> Path:
    """Path to MGT-7 example PDF."""
    return examples_dir / "U17120DL2013PTC262515_mgt7.pdf"


@pytest.fixture
def mgt7a_pdf_path(examples_dir: Path) -> Path:
    """Path to MGT-7A example PDF."""
    return examples_dir / "KA903UC002704392_mgt7a.pdf"
