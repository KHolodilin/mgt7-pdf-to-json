"""CLI interface for mgt7pdf2json."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from mgt7_pdf_to_json.config import Config
from mgt7_pdf_to_json.pipeline import Pipeline


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments namespace

    Example:
        >>> import sys
        >>> sys.argv = ["mgt7pdf2json", "input.pdf", "-o", "output.json"]
        >>> args = parse_args()
        >>> args.input
        'input.pdf'
        >>> args.output
        'output.json'
    """
    parser = argparse.ArgumentParser(
        prog="mgt7pdf2json",
        description="Convert MGT-7 and MGT-7A PDF forms to JSON",
    )

    parser.add_argument(
        "input",
        type=str,
        help="Input PDF path",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output JSON path. If not set — <input>.json",
    )

    parser.add_argument(
        "--outdir",
        type=str,
        help="Output directory (alternative to --output)",
    )

    parser.add_argument(
        "--mapper",
        type=str,
        choices=["default", "minimal", "db"],
        default="default",
        help="Mapper selection (default: default)",
    )

    parser.add_argument(
        "--config",
        type=str,
        help="YAML config path",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Override logging.level",
    )

    parser.add_argument(
        "--log-format",
        type=str,
        choices=["console", "json"],
        help="Override logging.format",
    )

    parser.add_argument(
        "--log-dir",
        type=str,
        help="Override logging.file",
    )

    parser.add_argument(
        "--debug-artifacts",
        action="store_true",
        help="Enable artifacts saving",
    )

    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable strict validation",
    )

    parser.add_argument(
        "--fail-on-warnings",
        action="store_true",
        help="Exit with error code if warnings exist",
    )

    return parser.parse_args()


def validate_input_file(input_path: Path) -> tuple[bool, str | None]:
    """
    Validate input file before processing.

    Args:
        input_path: Path to input file

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if file exists
    if not input_path.exists():
        return False, (
            f"Input file not found: {input_path}. "
            "Please check that the file path is correct and the file exists."
        )

    # Check if it's a file (not a directory)
    if not input_path.is_file():
        return False, (
            f"Input path is not a file: {input_path}. "
            "Please provide a path to a PDF file, not a directory."
        )

    # Check file extension (PDF)
    if input_path.suffix.lower() != ".pdf":
        return False, (
            f"Input file does not have PDF extension: {input_path}. "
            f"File extension: '{input_path.suffix}'. "
            "Please provide a PDF file (.pdf extension)."
        )

    # Check file size (not empty, reasonable size)
    try:
        file_size = input_path.stat().st_size
        if file_size == 0:
            return False, (
                f"Input file is empty (0 bytes): {input_path}. "
                "Please provide a valid PDF file with content."
            )
        # Warn about very large files (>100MB)
        if file_size > 100 * 1024 * 1024:  # 100 MB
            print(
                f"Warning: Input file is very large ({file_size / (1024 * 1024):.2f} MB): "
                f"{input_path}. Processing may take a long time.",
                file=sys.stderr,
            )
    except OSError as e:
        return False, (
            f"Cannot access file size for {input_path}: {e}. "
            "Please check file permissions and accessibility."
        )

    # Check file readability
    if not os.access(input_path, os.R_OK):
        return False, (
            f"Input file is not readable: {input_path}. "
            "Please check file permissions. The file must be readable."
        )

    # Check if file is actually a PDF by reading first bytes
    try:
        with open(input_path, "rb") as f:
            header = f.read(4)
            # PDF files start with %PDF
            if not header.startswith(b"%PDF"):
                return False, (
                    f"Input file does not appear to be a valid PDF: {input_path}. "
                    f"File header: {header.hex()}. "
                    "PDF files should start with '%PDF'. "
                    "The file may be corrupted or not a PDF."
                )
    except OSError as e:
        return False, (
            f"Cannot read input file: {input_path}. Error: {e}. "
            "Please check file permissions and that the file is not locked by another process."
        )

    return True, None


def main() -> int:
    """Main CLI entry point."""
    args = parse_args()

    # Load configuration
    try:
        config = Config.from_file_or_default(args.config)
    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        return 6  # CONFIG_ERROR

    # Override config with CLI args (CLI args > YAML config > defaults)
    if args.log_level:
        config.logging.level = args.log_level
    if args.log_format:
        config.logging.format = args.log_format
    if args.log_dir:
        config.logging.file = args.log_dir
    if args.debug_artifacts:
        config.artifacts.enabled = True
    if args.strict:
        config.validation.strict = True
    if args.mapper:
        config.pipeline.mapper = args.mapper

    # Validate input file
    input_path = Path(args.input)
    is_valid, error_message = validate_input_file(input_path)
    if not is_valid:
        print(f"Error: {error_message}", file=sys.stderr)
        return 3  # INPUT_NOT_FOUND

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    elif args.outdir:
        output_path = Path(args.outdir) / f"{input_path.stem}.json"
    else:
        output_path = input_path.with_suffix(".json")

    # Create output directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Process PDF
    try:
        pipeline = Pipeline(config)
        result = pipeline.process(str(input_path), output_path=str(output_path))

        # Check for validation errors in strict mode
        errors = result.get("errors", [])
        if config.validation.strict and errors:
            return 2  # VALIDATION_FAILED

        # Check for unsupported format (cannot detect form type)
        meta = result.get("meta", {})
        form_type = meta.get("form_type", "")
        if not form_type or form_type not in ["MGT-7", "MGT-7A"]:
            return 4  # UNSUPPORTED_FORMAT

        # Check for warnings
        warnings = result.get("warnings", [])
        if args.fail_on_warnings and warnings:
            return 5  # WARNINGS_AS_ERRORS

        return 0  # SUCCESS

    except FileNotFoundError as e:
        print(f"Error: Input file not found: {e}", file=sys.stderr)
        print("Hint: Check that the file path is correct and the file exists.", file=sys.stderr)
        return 3  # INPUT_NOT_FOUND
    except ValueError as e:
        error_msg = str(e)
        if "No extractable text" in error_msg or "scanned" in error_msg.lower():
            print("Error: Unsupported PDF format", file=sys.stderr)
            print(f"Details: {error_msg}", file=sys.stderr)
            print(
                "Hint: This PDF appears to be scanned/image-only. OCR is required.", file=sys.stderr
            )
            return 4  # UNSUPPORTED_FORMAT
        print(f"Error: Processing failed: {error_msg}", file=sys.stderr)
        return 1  # PROCESSING_ERROR
    except Exception as e:
        error_type = type(e).__name__
        print(f"Error: {error_type}: {e}", file=sys.stderr)
        if hasattr(e, "__cause__") and e.__cause__:
            print(f"Caused by: {type(e.__cause__).__name__}: {e.__cause__}", file=sys.stderr)
        return 1  # PROCESSING_ERROR


if __name__ == "__main__":
    sys.exit(main())
