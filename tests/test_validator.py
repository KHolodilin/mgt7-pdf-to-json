"""Tests for validator."""

import pytest

from mgt7_pdf_to_json.config import Config
from mgt7_pdf_to_json.validator import Validator


class TestValidator:
    """Test output validation."""

    @pytest.fixture
    def validator(self):
        """Create validator with default config."""
        config = Config.default()
        return Validator(config)

    def test_validate_valid_output(self, validator):
        """Test validation of valid output."""
        output = {
            "meta": {
                "request_id": "test-id",
                "schema_version": "1.0",
                "form_type": "MGT-7",
                "financial_year": {
                    "from": "01/04/2024",
                    "to": "31/03/2025",
                },
                "source": {
                    "input_file": "test.pdf",
                },
            },
            "data": {
                "company": {
                    "cin": "U17120DL2013PTC262515",
                    "name": "TEST COMPANY",
                },
            },
            "warnings": [],
            "errors": [],
        }

        warnings, errors = validator.validate(output)

        assert isinstance(warnings, list)
        assert isinstance(errors, list)

    def test_validate_missing_meta(self, validator):
        """Test validation with missing meta section."""
        output = {"data": {}}

        warnings, errors = validator.validate(output)

        assert len(errors) > 0
        assert any(e["code"] == "MISSING_SECTION" for e in errors)

    def test_validate_missing_required_field_strict(self):
        """Test validation with missing required field in strict mode."""
        config = Config.default()
        config.validation.strict = True
        validator = Validator(config)

        output = {
            "meta": {
                "request_id": "test-id",
                "schema_version": "1.0",
                "form_type": "MGT-7",
            },
            "data": {},
        }

        warnings, errors = validator.validate(output)

        # In strict mode, missing required fields should be errors
        assert len(errors) > 0

    def test_validate_missing_required_field_non_strict(self, validator):
        """Test validation with missing required field in non-strict mode."""
        output = {
            "meta": {
                "request_id": "test-id",
                "schema_version": "1.0",
                "form_type": "MGT-7",
            },
            "data": {},
        }

        warnings, errors = validator.validate(output)

        # In non-strict mode, missing required fields should be warnings
        assert len(warnings) > 0

    def test_validate_invalid_structure(self, validator):
        """Test validation with invalid structure (not a dict)."""
        output = "not a dict"  # type: ignore[assignment]

        warnings, errors = validator.validate(output)  # type: ignore[arg-type]

        assert len(errors) > 0
        assert any(e["code"] == "INVALID_STRUCTURE" for e in errors)

    def test_validate_missing_meta_fields(self, validator):
        """Test validation with missing meta fields."""
        output = {
            "meta": {
                "request_id": "test-id",
                # Missing schema_version and form_type
            },
            "data": {},
        }

        warnings, errors = validator.validate(output)

        assert len(errors) > 0
        assert any(e["code"] == "MISSING_FIELD" for e in errors)

    def test_validate_missing_data_section(self, validator):
        """Test validation with missing data section."""
        output = {
            "meta": {
                "request_id": "test-id",
                "schema_version": "1.0",
                "form_type": "MGT-7",
            },
            # Missing data section
        }

        warnings, errors = validator.validate(output)

        assert len(warnings) > 0
        assert any(w["code"] == "MISSING_SECTION" for w in warnings)

    def test_validate_with_pdf_path(self, validator):
        """Test validation with PDF path provided."""
        output = {
            "meta": {
                "request_id": "test-id",
                "schema_version": "1.0",
                "form_type": "MGT-7",
            },
            "data": {},
        }

        warnings, errors = validator.validate(output, pdf_path="test.pdf")

        assert isinstance(warnings, list)
        assert isinstance(errors, list)
