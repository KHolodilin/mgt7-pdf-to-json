"""Custom exceptions for mgt7-pdf-to-json."""

from __future__ import annotations


class MGT7Error(Exception):
    """Base exception for mgt7-pdf-to-json errors."""

    pass


class ExtractionError(MGT7Error):
    """Error during PDF extraction."""

    pass


class ParsingError(MGT7Error):
    """Error during document parsing."""

    pass


class ValidationError(MGT7Error):
    """Error during validation."""

    pass


class MappingError(MGT7Error):
    """Error during mapping."""

    pass


class UnsupportedFormatError(MGT7Error):
    """Unsupported PDF format (e.g., scanned/image-only)."""

    pass


class ConfigurationError(MGT7Error):
    """Configuration error."""

    pass
