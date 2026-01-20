"""Tests for logging functionality."""

import logging
from unittest.mock import MagicMock, patch

import pytest

from mgt7_pdf_to_json.config import Config
from mgt7_pdf_to_json.logging_ import (
    ConsoleFormatter,
    LoggerFactory,
    StructuredFormatter,
    get_request_id,
    log_with_request_id,
    set_request_id,
)


class TestStructuredFormatter:
    """Test structured JSON formatter."""

    def test_format_with_exception(self):
        """Test formatting log record with exception info."""
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Test error",
            args=(),
            exc_info=None,
        )
        # Add exception info using sys.exc_info()
        import sys
        try:
            raise ValueError("Test exception")
        except ValueError:
            record.exc_info = sys.exc_info()

        result = formatter.format(record)
        assert "exception" in result or "Test exception" in result

    def test_format_without_exception(self):
        """Test formatting log record without exception."""
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)
        assert "Test message" in result
        assert "exception" not in result


class TestConsoleFormatter:
    """Test console formatter."""

    def test_format_with_exception(self):
        """Test formatting log record with exception info."""
        formatter = ConsoleFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Test error",
            args=(),
            exc_info=None,
        )
        # Add exception info using sys.exc_info()
        import sys
        try:
            raise ValueError("Test exception")
        except ValueError:
            record.exc_info = sys.exc_info()

        result = formatter.format(record)
        assert "Test error" in result
        assert "\n" in result  # Exception should add newline

    def test_format_without_exception(self):
        """Test formatting log record without exception."""
        formatter = ConsoleFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)
        assert "Test message" in result


class TestLoggerFactory:
    """Test logger factory."""

    def test_setup_logging_json_format(self, tmp_path):
        """Test setting up logging with JSON format."""
        config = Config.default()
        config.logging.format = "json"
        config.logging.file = str(tmp_path / "logs")

        logger = LoggerFactory.setup_logging(config)
        assert logger is not None
        assert len(logger.handlers) >= 1

    def test_setup_logging_console_format(self, tmp_path):
        """Test setting up logging with console format."""
        config = Config.default()
        config.logging.format = "console"
        config.logging.file = str(tmp_path / "logs")

        logger = LoggerFactory.setup_logging(config)
        assert logger is not None

    def test_setup_logging_file_format_json(self, tmp_path):
        """Test setting up logging with file format JSON."""
        config = Config.default()
        config.logging.format_file = "json"
        config.logging.file = str(tmp_path / "logs")

        logger = LoggerFactory.setup_logging(config)
        assert logger is not None

    def test_setup_logging_file_format_console(self, tmp_path):
        """Test setting up logging with file format console."""
        config = Config.default()
        config.logging.format_file = "console"
        config.logging.file = str(tmp_path / "logs")

        logger = LoggerFactory.setup_logging(config)
        assert logger is not None

    def test_get_logger_with_name(self):
        """Test getting logger with specific name."""
        logger = LoggerFactory.get_logger("test_module")
        assert logger is not None
        assert logger.name == "mgt7_pdf_to_json.test_module"

    def test_get_logger_without_name(self):
        """Test getting logger without name (root logger)."""
        logger = LoggerFactory.get_logger()
        assert logger is not None
        assert logger.name == "mgt7_pdf_to_json"


class TestRequestIdContext:
    """Test request ID context management."""

    def test_set_and_get_request_id(self):
        """Test setting and getting request ID."""
        set_request_id("test-123")
        assert get_request_id() == "test-123"

    def test_get_request_id_when_not_set(self):
        """Test getting request ID when not set."""
        # Clear context by setting to empty string
        set_request_id("")
        result = get_request_id()
        assert result is None or result == ""


class TestLogWithRequestId:
    """Test logging with request ID."""

    def test_log_with_request_id(self):
        """Test logging with request ID and context."""
        logger = logging.getLogger("test")
        logger.setLevel(logging.DEBUG)

        # Create a handler to capture logs
        handler = logging.StreamHandler()
        logger.addHandler(handler)

        log_with_request_id(
            logger,
            logging.INFO,
            "Test message",
            "test-123",
            pdf_path="test.pdf",
            step="test",
            duration_ms=100.0,
        )

        # Verify request_id was set
        assert get_request_id() == "test-123"
