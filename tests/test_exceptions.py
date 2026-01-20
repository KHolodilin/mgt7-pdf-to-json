"""Tests for custom exceptions."""

import pytest

from mgt7_pdf_to_json.exceptions import (
    ConfigurationError,
    ExtractionError,
    MGT7Error,
    MappingError,
    ParsingError,
    UnsupportedFormatError,
    ValidationError,
)


class TestMGT7Error:
    """Test base exception class."""

    def test_mgt7_error_creation(self):
        """Test MGT7Error can be created and raised."""
        with pytest.raises(MGT7Error, match="test error"):
            raise MGT7Error("test error")

    def test_mgt7_error_inheritance(self):
        """Test that MGT7Error is a subclass of Exception."""
        assert issubclass(MGT7Error, Exception)


class TestExtractionError:
    """Test ExtractionError exception."""

    def test_extraction_error_creation(self):
        """Test ExtractionError can be created and raised."""
        with pytest.raises(ExtractionError, match="extraction failed"):
            raise ExtractionError("extraction failed")

    def test_extraction_error_inheritance(self):
        """Test that ExtractionError inherits from MGT7Error."""
        assert issubclass(ExtractionError, MGT7Error)


class TestParsingError:
    """Test ParsingError exception."""

    def test_parsing_error_creation(self):
        """Test ParsingError can be created and raised."""
        with pytest.raises(ParsingError, match="parsing failed"):
            raise ParsingError("parsing failed")

    def test_parsing_error_inheritance(self):
        """Test that ParsingError inherits from MGT7Error."""
        assert issubclass(ParsingError, MGT7Error)


class TestValidationError:
    """Test ValidationError exception."""

    def test_validation_error_creation(self):
        """Test ValidationError can be created and raised."""
        with pytest.raises(ValidationError, match="validation failed"):
            raise ValidationError("validation failed")

    def test_validation_error_inheritance(self):
        """Test that ValidationError inherits from MGT7Error."""
        assert issubclass(ValidationError, MGT7Error)


class TestMappingError:
    """Test MappingError exception."""

    def test_mapping_error_creation(self):
        """Test MappingError can be created and raised."""
        with pytest.raises(MappingError, match="mapping failed"):
            raise MappingError("mapping failed")

    def test_mapping_error_inheritance(self):
        """Test that MappingError inherits from MGT7Error."""
        assert issubclass(MappingError, MGT7Error)


class TestUnsupportedFormatError:
    """Test UnsupportedFormatError exception."""

    def test_unsupported_format_error_creation(self):
        """Test UnsupportedFormatError can be created and raised."""
        with pytest.raises(UnsupportedFormatError, match="unsupported format"):
            raise UnsupportedFormatError("unsupported format")

    def test_unsupported_format_error_inheritance(self):
        """Test that UnsupportedFormatError inherits from MGT7Error."""
        assert issubclass(UnsupportedFormatError, MGT7Error)


class TestConfigurationError:
    """Test ConfigurationError exception."""

    def test_configuration_error_creation(self):
        """Test ConfigurationError can be created and raised."""
        with pytest.raises(ConfigurationError, match="config error"):
            raise ConfigurationError("config error")

    def test_configuration_error_inheritance(self):
        """Test that ConfigurationError inherits from MGT7Error."""
        assert issubclass(ConfigurationError, MGT7Error)
