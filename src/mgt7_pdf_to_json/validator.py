"""Output JSON validation."""

from __future__ import annotations

from typing import Any

from mgt7_pdf_to_json.config import Config
from mgt7_pdf_to_json.logging_ import LoggerFactory

logger = LoggerFactory.get_logger("validator")


class Validator:
    """Validate output JSON against schema and required fields."""

    def __init__(self, config: Config):
        """
        Initialize validator with configuration.

        Args:
            config: Configuration object
        """
        self.config = config

    def validate(
        self, output: dict[str, Any], pdf_path: str | None = None
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """
        Validate output JSON.

        Args:
            output: Output JSON dictionary
            pdf_path: Optional PDF path for context

        Returns:
            Tuple of (warnings, errors)
        """
        logger.debug("Validating output JSON")

        warnings: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []

        # Validate structure
        if not isinstance(output, dict):
            errors.append(
                {
                    "code": "INVALID_STRUCTURE",
                    "message": "Output must be a dictionary",
                    "details": {},
                }
            )
            return warnings, errors

        # Validate meta section
        if "meta" not in output:
            errors.append(
                {
                    "code": "MISSING_SECTION",
                    "message": "Missing 'meta' section",
                    "details": {"section": "meta"},
                }
            )
        else:
            meta = output["meta"]
            # Validate required meta fields
            required_meta = ["request_id", "schema_version", "form_type"]
            for field in required_meta:
                if field not in meta:
                    errors.append(
                        {
                            "code": "MISSING_FIELD",
                            "message": f"meta.{field} is missing",
                            "details": {"field": f"meta.{field}"},
                        }
                    )

        # Validate required fields from config
        for field_path in self.config.validation.required_fields:
            value = self._get_nested_value(output, field_path)
            if value is None or value == "":
                error = {
                    "code": "MISSING_FIELD",
                    "message": f"{field_path} is missing",
                    "details": {"field": field_path},
                }

                if self.config.validation.strict:
                    errors.append(error)
                else:
                    warnings.append(error)

        # Validate data section
        if "data" not in output:
            warnings.append(
                {
                    "code": "MISSING_SECTION",
                    "message": "Missing 'data' section",
                    "details": {"section": "data"},
                }
            )

        return warnings, errors

    def _get_nested_value(self, data: dict[str, Any], path: str) -> Any:
        """
        Get nested value from dictionary using dot notation.

        Args:
            data: Dictionary to search
            path: Dot-separated path (e.g., "meta.form_type")

        Returns:
            Value at path or None if not found
        """
        keys = path.split(".")
        current = data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None

        return current
