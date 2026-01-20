"""Output JSON validation."""

from __future__ import annotations

from typing import Any

from mgt7_pdf_to_json.config import Config
from mgt7_pdf_to_json.logging_ import LoggerFactory

logger = LoggerFactory.get_logger("validator")


class Validator:
    """Validate output JSON against schema and required fields.

    Performs validation of the output JSON structure, checking for
    required sections and fields. Can operate in strict or lenient mode.

    Example:
        >>> from mgt7_pdf_to_json.config import Config
        >>> config = Config.default()
        >>> validator = Validator(config)
        >>> output = {"meta": {"request_id": "123", "form_type": "MGT-7"}}
        >>> warnings, errors = validator.validate(output)
        >>> len(errors)  # Missing required fields
        1
    """

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
            error_msg = (
                f"Output must be a dictionary, got {type(output).__name__}. "
                f"PDF path: {pdf_path if pdf_path else 'unknown'}. "
                "This indicates a critical error in the processing pipeline."
            )
            errors.append(
                {
                    "code": "INVALID_STRUCTURE",
                    "message": error_msg,
                    "details": {
                        "expected_type": "dict",
                        "actual_type": type(output).__name__,
                        "pdf_path": pdf_path,
                    },
                }
            )
            logger.error(error_msg)
            return warnings, errors

        # Validate meta section
        if "meta" not in output:
            error_msg = (
                "Missing 'meta' section in output JSON. "
                f"PDF path: {pdf_path if pdf_path else 'unknown'}. "
                "The 'meta' section is required and contains metadata about the processing."
            )
            errors.append(
                {
                    "code": "MISSING_SECTION",
                    "message": error_msg,
                    "details": {
                        "section": "meta",
                        "field_path": "meta",
                        "pdf_path": pdf_path,
                    },
                }
            )
            logger.error(error_msg)
        else:
            meta = output["meta"]
            # Validate required meta fields
            required_meta = ["request_id", "schema_version", "form_type"]
            for field in required_meta:
                if field not in meta:
                    field_path = f"meta.{field}"
                    error_msg = (
                        f"Missing required field '{field_path}' in output JSON. "
                        f"PDF path: {pdf_path if pdf_path else 'unknown'}. "
                        f"This field is required in the 'meta' section. "
                        f"Available meta fields: {list(meta.keys())}."
                    )
                    errors.append(
                        {
                            "code": "MISSING_FIELD",
                            "message": error_msg,
                            "details": {
                                "field": field_path,
                                "section": "meta",
                                "available_fields": list(meta.keys()),
                                "pdf_path": pdf_path,
                            },
                        }
                    )
                    logger.error(error_msg)

        # Validate required fields from config
        for field_path in self.config.validation.required_fields:
            value = self._get_nested_value(output, field_path)
            if value is None or value == "":
                # Get parent path for context
                path_parts = field_path.split(".")
                parent_path = ".".join(path_parts[:-1]) if len(path_parts) > 1 else "root"
                parent_value = (
                    self._get_nested_value(output, parent_path) if parent_path != "root" else output
                )

                available_keys = list(parent_value.keys()) if isinstance(parent_value, dict) else []
                error_msg = (
                    f"Missing required field '{field_path}' in output JSON. "
                    f"PDF path: {pdf_path if pdf_path else 'unknown'}. "
                    f"Parent path: '{parent_path}'. "
                    f"Available fields at parent: {available_keys if available_keys else 'none'}."
                )
                error = {
                    "code": "MISSING_FIELD",
                    "message": error_msg,
                    "details": {
                        "field": field_path,
                        "parent_path": parent_path,
                        "available_fields": available_keys,
                        "pdf_path": pdf_path,
                    },
                }

                if self.config.validation.strict:
                    errors.append(error)
                    logger.error(error_msg)
                else:
                    warnings.append(error)
                    logger.warning(error_msg)

        # Validate data section
        if "data" not in output:
            error_msg = (
                "Missing 'data' section in output JSON. "
                f"PDF path: {pdf_path if pdf_path else 'unknown'}. "
                "The 'data' section contains the parsed document data. "
                f"Available top-level sections: {list(output.keys())}."
            )
            warnings.append(
                {
                    "code": "MISSING_SECTION",
                    "message": error_msg,
                    "details": {
                        "section": "data",
                        "field_path": "data",
                        "available_sections": list(output.keys()),
                        "pdf_path": pdf_path,
                    },
                }
            )
            logger.warning(error_msg)

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
