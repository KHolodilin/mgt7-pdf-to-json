"""Structured logging with request_id support."""

from __future__ import annotations

import contextvars
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

if TYPE_CHECKING:
    from mgt7_pdf_to_json.config import Config

# Context variable for request_id to be accessible in all components
_request_id_context: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "request_id", default=None
)


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        # Try to get request_id from record, fallback to context
        request_id = getattr(record, "request_id", None) or get_request_id()
        
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "event": record.getMessage(),
            "request_id": request_id,
            "pdf_path": getattr(record, "pdf_path", None),
            "step": getattr(record, "step", None),
            "duration_ms": getattr(record, "duration_ms", None),
            "artifact_path": getattr(record, "artifact_path", None),
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add any extra fields
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "thread",
                "threadName",
                "exc_info",
                "exc_text",
                "stack_info",
            ]:
                log_data[key] = value

        return json.dumps(log_data, ensure_ascii=False)


class ConsoleFormatter(logging.Formatter):
    """Human-readable console formatter."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record for console output."""
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        level = record.levelname.ljust(8)
        # Try to get request_id from record, fallback to context
        request_id = getattr(record, "request_id", None) or get_request_id() or ""
        if request_id:
            request_id = f"[{request_id[:8]}] "
        step = getattr(record, "step", "")
        if step:
            step = f" [{step}]"

        msg = f"{timestamp} {level} {request_id}{record.getMessage()}{step}"

        if record.exc_info:
            msg += "\n" + self.formatException(record.exc_info)

        return msg


class LoggerFactory:
    """Factory for creating configured loggers."""

    @staticmethod
    def setup_logging(config: Config) -> logging.Logger:
        """
        Set up logging based on configuration.

        Args:
            config: Configuration object

        Returns:
            Root logger instance
        """
        logger = logging.getLogger("mgt7_pdf_to_json")
        logger.setLevel(getattr(logging, config.logging.level.upper()))

        # Remove existing handlers
        logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)

        if config.logging.format == "json":
            console_formatter: logging.Formatter = StructuredFormatter()
        else:
            console_formatter = ConsoleFormatter()

        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # File handler
        log_dir = Path(config.logging.file)
        log_dir.mkdir(parents=True, exist_ok=True)

        # Generate log file name based on date format
        log_filename = datetime.now().strftime(config.logging.date_format) + ".log"
        log_file_path = log_dir / log_filename

        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)

        # File format is always JSON
        if config.logging.format_file == "json":
            file_formatter: logging.Formatter = StructuredFormatter()
        else:
            file_formatter = ConsoleFormatter()

        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        logger.propagate = False

        return logger

    @staticmethod
    def get_logger(name: str | None = None) -> logging.Logger:
        """
        Get logger instance.

        Args:
            name: Logger name (default: root logger)

        Returns:
            Logger instance
        """
        if name:
            return logging.getLogger(f"mgt7_pdf_to_json.{name}")
        return logging.getLogger("mgt7_pdf_to_json")


def set_request_id(request_id: str | UUID) -> None:
    """
    Set request_id in context for all subsequent logs.

    Args:
        request_id: Request ID to set in context
    """
    _request_id_context.set(str(request_id))


def get_request_id() -> str | None:
    """
    Get current request_id from context.

    Returns:
        Current request_id or None if not set
    """
    return _request_id_context.get()


def log_with_request_id(
    logger: logging.Logger,
    level: int,
    message: str,
    request_id: str | UUID,
    pdf_path: str | None = None,
    step: str | None = None,
    duration_ms: float | None = None,
    artifact_path: str | None = None,
    **kwargs: Any,
) -> None:
    """
    Log message with request_id and additional context.

    Args:
        logger: Logger instance
        level: Log level
        message: Log message
        request_id: Request ID (UUID)
        pdf_path: Optional PDF file path
        step: Optional processing step
        duration_ms: Optional duration in milliseconds
        artifact_path: Optional artifact file path
        **kwargs: Additional context fields
    """
    # Update context with request_id
    set_request_id(request_id)
    
    extra = {
        "request_id": str(request_id),
        "pdf_path": pdf_path,
        "step": step,
        "duration_ms": duration_ms,
        "artifact_path": artifact_path,
        **kwargs,
    }
    logger.log(level, message, extra=extra)
