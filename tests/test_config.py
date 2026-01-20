"""Tests for configuration management."""

import pytest
import yaml

from mgt7_pdf_to_json.config import Config


class TestConfig:
    """Test configuration loading and defaults."""

    def test_default_config(self):
        """Test default configuration."""
        config = Config.default()

        assert config.logging.level == "INFO"
        assert config.logging.format == "console"
        assert config.artifacts.enabled is False
        assert config.pipeline.mapper == "default"
        assert config.validation.strict is False

    def test_from_yaml(self, tmp_path):
        """Test loading config from YAML."""
        config_data = {
            "logging": {
                "level": "DEBUG",
                "format": "json",
            },
            "pipeline": {
                "mapper": "minimal",
            },
        }

        config_file = tmp_path / "config.yml"
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        config = Config.from_yaml(config_file)

        assert config.logging.level == "DEBUG"
        assert config.logging.format == "json"
        assert config.pipeline.mapper == "minimal"

    def test_from_file_or_default_existing(self, tmp_path):
        """Test loading config from existing file."""
        config_data = {
            "logging": {
                "level": "WARNING",
            },
        }

        config_file = tmp_path / "config.yml"
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Change to temp directory
        import os

        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            config = Config.from_file_or_default()
            assert config.logging.level == "WARNING"
        finally:
            os.chdir(old_cwd)

    def test_from_file_or_default_not_existing(self):
        """Test loading default config when file doesn't exist."""
        config = Config.from_file_or_default("nonexistent.yml")
        assert config.logging.level == "INFO"  # default

    def test_from_yaml_file_not_found(self, tmp_path):
        """Test from_yaml raises FileNotFoundError when file doesn't exist."""
        nonexistent_file = tmp_path / "nonexistent.yml"
        with pytest.raises(FileNotFoundError, match="Config file not found"):
            Config.from_yaml(nonexistent_file)

    def test_from_file_or_default_with_existing_path(self, tmp_path):
        """Test from_file_or_default with existing file path."""
        config_data = {"logging": {"level": "DEBUG"}}
        config_file = tmp_path / "test_config.yml"
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        config = Config.from_file_or_default(config_file)
        assert config.logging.level == "DEBUG"
