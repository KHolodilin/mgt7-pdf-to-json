"""CLI interface for mgt7pdf2json."""

import argparse
import sys
from pathlib import Path

from mgt7_pdf_to_json.config import Config
from mgt7_pdf_to_json.pipeline import Pipeline


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
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
    if not input_path.exists():
        print(f"Input file not found: {input_path}", file=sys.stderr)
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
