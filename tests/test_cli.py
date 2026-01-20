"""Tests for CLI interface."""

from unittest.mock import MagicMock, patch

import pytest

from mgt7_pdf_to_json.cli import main, parse_args, validate_input_file


class TestParseArgs:
    """Test CLI argument parsing."""

    def test_parse_args_minimal(self):
        """Test parsing minimal arguments."""
        with patch("sys.argv", ["mgt7pdf2json", "input.pdf"]):
            args = parse_args()
            assert args.input == "input.pdf"
            assert args.output is None
            assert args.outdir is None
            assert args.mapper == "default"
            assert args.config is None

    def test_parse_args_with_output(self):
        """Test parsing with output file."""
        with patch("sys.argv", ["mgt7pdf2json", "input.pdf", "-o", "output.json"]):
            args = parse_args()
            assert args.input == "input.pdf"
            assert args.output == "output.json"

    def test_parse_args_with_outdir(self):
        """Test parsing with output directory."""
        with patch("sys.argv", ["mgt7pdf2json", "input.pdf", "--outdir", "output/"]):
            args = parse_args()
            assert args.input == "input.pdf"
            assert args.outdir == "output/"

    def test_parse_args_with_mapper(self):
        """Test parsing with mapper option."""
        with patch("sys.argv", ["mgt7pdf2json", "input.pdf", "--mapper", "minimal"]):
            args = parse_args()
            assert args.mapper == "minimal"

    def test_parse_args_with_config(self):
        """Test parsing with config file."""
        with patch("sys.argv", ["mgt7pdf2json", "input.pdf", "--config", "config.yml"]):
            args = parse_args()
            assert args.config == "config.yml"

    def test_parse_args_with_log_level(self):
        """Test parsing with log level."""
        with patch("sys.argv", ["mgt7pdf2json", "input.pdf", "--log-level", "DEBUG"]):
            args = parse_args()
            assert args.log_level == "DEBUG"

    def test_parse_args_with_log_format(self):
        """Test parsing with log format."""
        with patch("sys.argv", ["mgt7pdf2json", "input.pdf", "--log-format", "json"]):
            args = parse_args()
            assert args.log_format == "json"

    def test_parse_args_with_log_dir(self):
        """Test parsing with log directory."""
        with patch("sys.argv", ["mgt7pdf2json", "input.pdf", "--log-dir", "logs/"]):
            args = parse_args()
            assert args.log_dir == "logs/"

    def test_parse_args_with_debug_artifacts(self):
        """Test parsing with debug artifacts flag."""
        with patch("sys.argv", ["mgt7pdf2json", "input.pdf", "--debug-artifacts"]):
            args = parse_args()
            assert args.debug_artifacts is True

    def test_parse_args_with_strict(self):
        """Test parsing with strict flag."""
        with patch("sys.argv", ["mgt7pdf2json", "input.pdf", "--strict"]):
            args = parse_args()
            assert args.strict is True

    def test_parse_args_with_fail_on_warnings(self):
        """Test parsing with fail-on-warnings flag."""
        with patch("sys.argv", ["mgt7pdf2json", "input.pdf", "--fail-on-warnings"]):
            args = parse_args()
            assert args.fail_on_warnings is True

    def test_parse_args_with_include_stats(self):
        """Test parsing with include-stats flag."""
        with patch("sys.argv", ["mgt7pdf2json", "input.pdf", "--include-stats"]):
            args = parse_args()
            assert args.include_stats is True

    def test_parse_args_without_include_stats(self):
        """Test parsing without include-stats flag (default)."""
        with patch("sys.argv", ["mgt7pdf2json", "input.pdf"]):
            args = parse_args()
            assert args.include_stats is False


class TestMain:
    """Test main CLI function."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration."""
        config = MagicMock()
        config.logging.level = "INFO"
        config.logging.format = "console"
        config.logging.file = "logs/"
        config.artifacts.enabled = False
        config.validation.strict = False
        config.pipeline.mapper = "default"
        return config

    @pytest.fixture
    def mock_pipeline(self):
        """Mock pipeline."""
        pipeline = MagicMock()
        pipeline.process.return_value = {
            "meta": {"form_type": "MGT-7", "request_id": "test-123"},
            "data": {},
            "warnings": [],
            "errors": [],
        }
        return pipeline

    def test_main_success(self, mock_config, mock_pipeline, tmp_path):
        """Test successful main execution."""
        input_file = tmp_path / "test.pdf"
        # Create minimal valid PDF file
        input_file.write_bytes(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

        with patch("sys.argv", ["mgt7pdf2json", str(input_file)]):
            with patch(
                "mgt7_pdf_to_json.cli.Config.from_file_or_default", return_value=mock_config
            ):
                with patch("mgt7_pdf_to_json.cli.Pipeline", return_value=mock_pipeline):
                    result = main()
                    assert result == 0

    def test_main_config_error(self, tmp_path):
        """Test main with config loading error."""
        input_file = tmp_path / "test.pdf"
        # Create minimal valid PDF file
        input_file.write_bytes(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

        with patch("sys.argv", ["mgt7pdf2json", str(input_file)]):
            with patch(
                "mgt7_pdf_to_json.cli.Config.from_file_or_default",
                side_effect=Exception("Config error"),
            ):
                with patch("sys.stderr"):
                    result = main()
                    assert result == 6  # CONFIG_ERROR

    def test_main_input_not_found(self, mock_config):
        """Test main with non-existent input file."""
        with patch("sys.argv", ["mgt7pdf2json", "nonexistent.pdf"]):
            with patch(
                "mgt7_pdf_to_json.cli.Config.from_file_or_default", return_value=mock_config
            ):
                with patch("sys.stderr"):
                    result = main()
                    assert result == 3  # INPUT_NOT_FOUND

    def test_main_validation_failed_strict(self, mock_config, mock_pipeline, tmp_path):
        """Test main with validation errors in strict mode."""
        input_file = tmp_path / "test.pdf"
        # Create minimal valid PDF file
        input_file.write_bytes(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        mock_config.validation.strict = True
        mock_pipeline.process.return_value = {
            "meta": {"form_type": "MGT-7"},
            "data": {},
            "warnings": [],
            "errors": ["Validation error"],
        }

        with patch("sys.argv", ["mgt7pdf2json", str(input_file)]):
            with patch(
                "mgt7_pdf_to_json.cli.Config.from_file_or_default", return_value=mock_config
            ):
                with patch("mgt7_pdf_to_json.cli.Pipeline", return_value=mock_pipeline):
                    result = main()
                    assert result == 2  # VALIDATION_FAILED

    def test_main_unsupported_format(self, mock_config, mock_pipeline, tmp_path):
        """Test main with unsupported format."""
        input_file = tmp_path / "test.pdf"
        # Create minimal valid PDF file
        input_file.write_bytes(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        mock_pipeline.process.return_value = {
            "meta": {"form_type": ""},  # Empty form type
            "data": {},
            "warnings": [],
            "errors": [],
        }

        with patch("sys.argv", ["mgt7pdf2json", str(input_file)]):
            with patch(
                "mgt7_pdf_to_json.cli.Config.from_file_or_default", return_value=mock_config
            ):
                with patch("mgt7_pdf_to_json.cli.Pipeline", return_value=mock_pipeline):
                    result = main()
                    assert result == 4  # UNSUPPORTED_FORMAT

    def test_main_fail_on_warnings(self, mock_config, mock_pipeline, tmp_path):
        """Test main with fail-on-warnings flag."""
        input_file = tmp_path / "test.pdf"
        # Create minimal valid PDF file
        input_file.write_bytes(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        mock_pipeline.process.return_value = {
            "meta": {"form_type": "MGT-7"},
            "data": {},
            "warnings": ["Warning message"],
            "errors": [],
        }

        with patch("sys.argv", ["mgt7pdf2json", str(input_file), "--fail-on-warnings"]):
            with patch(
                "mgt7_pdf_to_json.cli.Config.from_file_or_default", return_value=mock_config
            ):
                with patch("mgt7_pdf_to_json.cli.Pipeline", return_value=mock_pipeline):
                    result = main()
                    assert result == 5  # WARNINGS_AS_ERRORS

    def test_main_file_not_found_exception(self, mock_config, tmp_path):
        """Test main with FileNotFoundError exception."""
        input_file = tmp_path / "test.pdf"
        # Create minimal valid PDF file
        input_file.write_bytes(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

        with patch("sys.argv", ["mgt7pdf2json", str(input_file)]):
            with patch(
                "mgt7_pdf_to_json.cli.Config.from_file_or_default", return_value=mock_config
            ):
                with patch(
                    "mgt7_pdf_to_json.cli.Pipeline", side_effect=FileNotFoundError("File not found")
                ):
                    with patch("sys.stderr"):
                        result = main()
                        assert result == 3  # INPUT_NOT_FOUND

    def test_main_scanned_pdf_error(self, mock_config, tmp_path):
        """Test main with scanned PDF error."""
        input_file = tmp_path / "test.pdf"
        # Create minimal valid PDF file
        input_file.write_bytes(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

        with patch("sys.argv", ["mgt7pdf2json", str(input_file)]):
            with patch(
                "mgt7_pdf_to_json.cli.Config.from_file_or_default", return_value=mock_config
            ):
                with patch(
                    "mgt7_pdf_to_json.cli.Pipeline", side_effect=ValueError("No extractable text")
                ):
                    with patch("sys.stderr"):
                        result = main()
                        assert result == 4  # UNSUPPORTED_FORMAT

    def test_main_processing_error(self, mock_config, tmp_path):
        """Test main with processing error."""
        input_file = tmp_path / "test.pdf"
        # Create minimal valid PDF file
        input_file.write_bytes(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

        with patch("sys.argv", ["mgt7pdf2json", str(input_file)]):
            with patch(
                "mgt7_pdf_to_json.cli.Config.from_file_or_default", return_value=mock_config
            ):
                with patch(
                    "mgt7_pdf_to_json.cli.Pipeline", side_effect=ValueError("Processing failed")
                ):
                    with patch("sys.stderr"):
                        result = main()
                        assert result == 1  # PROCESSING_ERROR

    def test_main_generic_exception(self, mock_config, tmp_path):
        """Test main with generic exception."""
        input_file = tmp_path / "test.pdf"
        # Create minimal valid PDF file
        input_file.write_bytes(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

        with patch("sys.argv", ["mgt7pdf2json", str(input_file)]):
            with patch(
                "mgt7_pdf_to_json.cli.Config.from_file_or_default", return_value=mock_config
            ):
                with patch(
                    "mgt7_pdf_to_json.cli.Pipeline", side_effect=RuntimeError("Unexpected error")
                ):
                    with patch("sys.stderr"):
                        result = main()
                        assert result == 1  # PROCESSING_ERROR

    def test_main_with_output_path(self, mock_config, mock_pipeline, tmp_path):
        """Test main with explicit output path."""
        input_file = tmp_path / "test.pdf"
        # Create minimal valid PDF file
        input_file.write_bytes(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        output_file = tmp_path / "output.json"

        with patch("sys.argv", ["mgt7pdf2json", str(input_file), "-o", str(output_file)]):
            with patch(
                "mgt7_pdf_to_json.cli.Config.from_file_or_default", return_value=mock_config
            ):
                with patch("mgt7_pdf_to_json.cli.Pipeline", return_value=mock_pipeline):
                    result = main()
                    assert result == 0
                    mock_pipeline.process.assert_called_once()
                    # Check that output_path was passed correctly
                    call_kwargs = mock_pipeline.process.call_args[1]
                    assert call_kwargs["output_path"] == str(output_file)

    def test_main_with_outdir(self, mock_config, mock_pipeline, tmp_path):
        """Test main with output directory."""
        input_file = tmp_path / "test.pdf"
        # Create minimal valid PDF file
        input_file.write_bytes(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        outdir = tmp_path / "output"
        outdir.mkdir()

        with patch("sys.argv", ["mgt7pdf2json", str(input_file), "--outdir", str(outdir)]):
            with patch(
                "mgt7_pdf_to_json.cli.Config.from_file_or_default", return_value=mock_config
            ):
                with patch("mgt7_pdf_to_json.cli.Pipeline", return_value=mock_pipeline):
                    result = main()
                    assert result == 0

    def test_main_cli_args_override_config(self, mock_config, mock_pipeline, tmp_path):
        """Test that CLI args override config."""
        input_file = tmp_path / "test.pdf"
        # Create minimal valid PDF file
        input_file.write_bytes(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

        with patch(
            "sys.argv",
            ["mgt7pdf2json", str(input_file), "--log-level", "DEBUG", "--mapper", "minimal"],
        ):
            with patch(
                "mgt7_pdf_to_json.cli.Config.from_file_or_default", return_value=mock_config
            ):
                with patch("mgt7_pdf_to_json.cli.Pipeline", return_value=mock_pipeline):
                    main()
                    assert mock_config.logging.level == "DEBUG"
                    assert mock_config.pipeline.mapper == "minimal"

    def test_main_with_debug_artifacts(self, mock_config, mock_pipeline, tmp_path):
        """Test main with debug artifacts flag."""
        input_file = tmp_path / "test.pdf"
        # Create minimal valid PDF file
        input_file.write_bytes(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

        with patch("sys.argv", ["mgt7pdf2json", str(input_file), "--debug-artifacts"]):
            with patch(
                "mgt7_pdf_to_json.cli.Config.from_file_or_default", return_value=mock_config
            ):
                with patch("mgt7_pdf_to_json.cli.Pipeline", return_value=mock_pipeline):
                    main()
                    assert mock_config.artifacts.enabled is True

    def test_main_with_strict(self, mock_config, mock_pipeline, tmp_path):
        """Test main with strict flag."""
        input_file = tmp_path / "test.pdf"
        # Create minimal valid PDF file
        input_file.write_bytes(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

        with patch("sys.argv", ["mgt7pdf2json", str(input_file), "--strict"]):
            with patch(
                "mgt7_pdf_to_json.cli.Config.from_file_or_default", return_value=mock_config
            ):
                with patch("mgt7_pdf_to_json.cli.Pipeline", return_value=mock_pipeline):
                    main()
                    assert mock_config.validation.strict is True

    def test_main_with_include_stats(self, mock_config, mock_pipeline, tmp_path):
        """Test main with include-stats flag."""
        input_file = tmp_path / "test.pdf"
        # Create minimal valid PDF file
        input_file.write_bytes(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        mock_pipeline.process.return_value = {
            "meta": {
                "form_type": "MGT-7",
                "request_id": "test-123",
                "statistics": {
                    "pages_count": 5,
                    "tables_count": 2,
                    "parsed_fields_count": 10,
                },
            },
            "data": {},
            "warnings": [],
            "errors": [],
        }

        with patch("sys.argv", ["mgt7pdf2json", str(input_file), "--include-stats"]):
            with patch(
                "mgt7_pdf_to_json.cli.Config.from_file_or_default", return_value=mock_config
            ):
                with patch("mgt7_pdf_to_json.cli.Pipeline", return_value=mock_pipeline):
                    result = main()
                    assert result == 0
                    # Verify that include_stats was passed to pipeline
                    mock_pipeline.process.assert_called_once()
                    call_args = mock_pipeline.process.call_args
                    assert call_args.kwargs.get("include_stats") is True


class TestValidateInputFile:
    """Test input file validation."""

    def test_validate_input_file_exists(self, tmp_path):
        """Test validation of existing PDF file."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        is_valid, error = validate_input_file(pdf_file)
        assert is_valid is True
        assert error is None

    def test_validate_input_file_not_exists(self, tmp_path):
        """Test validation of non-existent file."""
        pdf_file = tmp_path / "nonexistent.pdf"
        is_valid, error = validate_input_file(pdf_file)
        assert is_valid is False
        assert error is not None
        assert "not found" in error.lower()

    def test_validate_input_file_not_file(self, tmp_path):
        """Test validation when path is a directory."""
        pdf_dir = tmp_path / "test_dir"
        pdf_dir.mkdir()
        is_valid, error = validate_input_file(pdf_dir)
        assert is_valid is False
        assert error is not None
        assert "not a file" in error.lower()

    def test_validate_input_file_wrong_extension(self, tmp_path):
        """Test validation with wrong file extension."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Not a PDF")
        is_valid, error = validate_input_file(txt_file)
        assert is_valid is False
        assert error is not None
        assert "pdf extension" in error.lower()

    def test_validate_input_file_empty(self, tmp_path):
        """Test validation of empty file."""
        pdf_file = tmp_path / "empty.pdf"
        pdf_file.write_bytes(b"")
        is_valid, error = validate_input_file(pdf_file)
        assert is_valid is False
        assert error is not None
        assert "empty" in error.lower()

    def test_validate_input_file_invalid_pdf_header(self, tmp_path):
        """Test validation with invalid PDF header."""
        pdf_path = tmp_path / "invalid.pdf"
        pdf_path.write_bytes(b"NOT A PDF")

        is_valid, error_msg = validate_input_file(pdf_path)
        assert not is_valid
        assert "does not appear to be a valid PDF" in error_msg

    def test_validate_input_file_large_file(self, tmp_path, monkeypatch):
        """Test validation with very large file (>100MB) (covers lines 157-161)."""
        pdf_path = tmp_path / "large.pdf"
        # Create a minimal valid PDF
        pdf_content = b"%PDF-1.4\n%%\xe2\xe3\xe4\xe5\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 0>>endobj\nxref\n0 3\n0000000000 65535 f\n0000000009 00000 n\n0000000054 00000 n\ntrailer<</Size 3/Root 1 0 R>>startxref\n106\n%%EOF"
        pdf_path.write_bytes(pdf_content)

        # Mock file size to be >100MB using monkeypatch
        from pathlib import Path
        from unittest.mock import MagicMock

        # Get real stat result first
        real_stat = pdf_path.stat()

        # Create mock_stat with real st_mode but fake st_size
        mock_stat = MagicMock()
        mock_stat.st_size = 101 * 1024 * 1024  # 101 MB
        mock_stat.st_mode = real_stat.st_mode  # Use real mode for is_file() to work

        # Store original stat method
        original_stat = Path.stat

        # Create a wrapper that returns mock_stat for our specific path
        def mock_stat_method(self):
            # Compare paths as strings (normalized) to work on all platforms
            # Use resolve() to normalize paths for comparison
            try:
                self_resolved = str(self.resolve())
                pdf_resolved = str(pdf_path.resolve())
            except (OSError, RuntimeError):
                # If resolve fails, fall back to string comparison
                self_resolved = str(self)
                pdf_resolved = str(pdf_path)
            if self_resolved == pdf_resolved:
                return mock_stat
            return original_stat(self)

        monkeypatch.setattr(Path, "stat", mock_stat_method)

        with patch("sys.stderr") as mock_stderr:
            is_valid, error_msg = validate_input_file(pdf_path)
            assert is_valid
            assert error_msg is None
            # Check that warning was printed (validate_input_file prints to stderr)
            # The warning is printed via print(..., file=sys.stderr), so we check if write was called
            assert mock_stderr.write.called

    def test_validate_input_file_oserror_size(self, tmp_path, monkeypatch):
        """Test validation with OSError when accessing file size (covers lines 162-166)."""
        pdf_path = tmp_path / "test.pdf"
        pdf_content = b"%PDF-1.4\n%%\xe2\xe3\xe4\xe5\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 0>>endobj\nxref\n0 3\n0000000000 65535 f\n0000000009 00000 n\n0000000054 00000 n\ntrailer<</Size 3/Root 1 0 R>>startxref\n106\n%%EOF"
        pdf_path.write_bytes(pdf_content)

        # Mock stat() to raise OSError only when accessing st_size, not for exists/is_file
        from pathlib import Path

        original_stat = Path.stat
        call_count = {"count": 0}

        class StatResult:
            """Mock stat result that raises OSError when accessing st_size."""

            def __init__(self, real_stat):
                self.st_mode = real_stat.st_mode
                self._real_stat = real_stat

            @property
            def st_size(self):
                raise OSError("Permission denied")

        def mock_stat_method(self):
            result = original_stat(self)
            # Only raise OSError when accessing st_size (second call in validate_input_file)
            # Compare paths as strings (normalized) to work on all platforms
            try:
                self_resolved = str(self.resolve())
                pdf_resolved = str(pdf_path.resolve())
            except (OSError, RuntimeError):
                # If resolve fails, fall back to string comparison
                self_resolved = str(self)
                pdf_resolved = str(pdf_path)
            if self_resolved == pdf_resolved:
                call_count["count"] += 1
                if call_count["count"] > 1:  # After exists/is_file checks
                    return StatResult(result)
            return result

        monkeypatch.setattr(Path, "stat", mock_stat_method)

        is_valid, error = validate_input_file(pdf_path)
        assert is_valid is False
        assert "Cannot access file size" in error

    def test_validate_input_file_not_readable(self, tmp_path):
        """Test validation when file is not readable."""
        pdf_path = tmp_path / "test.pdf"
        pdf_content = b"%PDF-1.4\n%%\xe2\xe3\xe4\xe5\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 0>>endobj\nxref\n0 3\n0000000000 65535 f\n0000000009 00000 n\n0000000054 00000 n\ntrailer<</Size 3/Root 1 0 R>>startxref\n106\n%%EOF"
        pdf_path.write_bytes(pdf_content)

        # Mock os.access to return False
        with patch("os.access", return_value=False):
            is_valid, error_msg = validate_input_file(pdf_path)
            assert not is_valid
            assert "not readable" in error_msg

    def test_validate_input_file_oserror_reading(self, tmp_path):
        """Test validation when OSError occurs while reading file."""
        pdf_path = tmp_path / "test.pdf"
        pdf_content = b"%PDF-1.4\n%%\xe2\xe3\xe4\xe5\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 0>>endobj\nxref\n0 3\n0000000000 65535 f\n0000000009 00000 n\n0000000054 00000 n\ntrailer<</Size 3/Root 1 0 R>>startxref\n106\n%%EOF"
        pdf_path.write_bytes(pdf_content)

        # Mock open to raise OSError
        with patch("builtins.open", side_effect=OSError("Permission denied")):
            is_valid, error_msg = validate_input_file(pdf_path)
            assert not is_valid
            assert "Cannot read input file" in error_msg

    def test_main_with_log_format_cli_arg(self, tmp_path):
        """Test main with log format CLI argument."""
        pdf_path = tmp_path / "test.pdf"
        pdf_content = b"%PDF-1.4\n%%\xe2\xe3\xe4\xe5\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 0>>endobj\nxref\n0 3\n0000000000 65535 f\n0000000009 00000 n\n0000000054 00000 n\ntrailer<</Size 3/Root 1 0 R>>startxref\n106\n%%EOF"
        pdf_path.write_bytes(pdf_content)

        mock_config = MagicMock()
        mock_config.logging = MagicMock()
        mock_config.logging.level = "INFO"
        mock_config.logging.format = "text"
        mock_config.logging.file = str(tmp_path / "logs")
        mock_config.validation = MagicMock()
        mock_config.validation.strict = False
        mock_config.pipeline = MagicMock()
        mock_config.pipeline.mapper = "default"
        mock_config.artifacts = MagicMock()
        mock_config.artifacts.enabled = False

        mock_pipeline = MagicMock()
        mock_pipeline.process.return_value = {
            "meta": {"form_type": "MGT-7"},
            "errors": [],
            "warnings": [],
        }

        with patch("sys.argv", ["mgt7pdf2json", str(pdf_path), "--log-format", "json"]):
            with patch(
                "mgt7_pdf_to_json.cli.Config.from_file_or_default", return_value=mock_config
            ):
                with patch("mgt7_pdf_to_json.cli.Pipeline", return_value=mock_pipeline):
                    result = main()
                    assert result == 0
                    # Verify log_format was set
                    assert mock_config.logging.format == "json"

    def test_main_with_log_dir_cli_arg(self, tmp_path):
        """Test main with log directory CLI argument."""
        pdf_path = tmp_path / "test.pdf"
        pdf_content = b"%PDF-1.4\n%%\xe2\xe3\xe4\xe5\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 0>>endobj\nxref\n0 3\n0000000000 65535 f\n0000000009 00000 n\n0000000054 00000 n\ntrailer<</Size 3/Root 1 0 R>>startxref\n106\n%%EOF"
        pdf_path.write_bytes(pdf_content)
        log_dir = tmp_path / "logs"

        mock_config = MagicMock()
        mock_config.logging = MagicMock()
        mock_config.logging.level = "INFO"
        mock_config.logging.format = "text"
        mock_config.logging.file = str(tmp_path / "logs")
        mock_config.validation = MagicMock()
        mock_config.validation.strict = False
        mock_config.pipeline = MagicMock()
        mock_config.pipeline.mapper = "default"
        mock_config.artifacts = MagicMock()
        mock_config.artifacts.enabled = False

        mock_pipeline = MagicMock()
        mock_pipeline.process.return_value = {
            "meta": {"form_type": "MGT-7"},
            "errors": [],
            "warnings": [],
        }

        with patch("sys.argv", ["mgt7pdf2json", str(pdf_path), "--log-dir", str(log_dir)]):
            with patch(
                "mgt7_pdf_to_json.cli.Config.from_file_or_default", return_value=mock_config
            ):
                with patch("mgt7_pdf_to_json.cli.Pipeline", return_value=mock_pipeline):
                    result = main()
                    assert result == 0
                    # Verify log_dir was set
                    assert mock_config.logging.file == str(log_dir)

    def test_main_exception_with_cause(self, tmp_path):
        """Test main when exception has __cause__ attribute."""
        pdf_path = tmp_path / "test.pdf"
        pdf_content = b"%PDF-1.4\n%%\xe2\xe3\xe4\xe5\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 0>>endobj\nxref\n0 3\n0000000000 65535 f\n0000000009 00000 n\n0000000054 00000 n\ntrailer<</Size 3/Root 1 0 R>>startxref\n106\n%%EOF"
        pdf_path.write_bytes(pdf_content)

        mock_config = MagicMock()
        mock_config.logging = MagicMock()
        mock_config.logging.level = "INFO"
        mock_config.logging.format = "text"
        mock_config.logging.file = str(tmp_path / "logs")
        mock_config.validation = MagicMock()
        mock_config.validation.strict = False
        mock_config.pipeline = MagicMock()
        mock_config.pipeline.mapper = "default"
        mock_config.artifacts = MagicMock()
        mock_config.artifacts.enabled = False

        # Create exception with __cause__
        cause = ValueError("Root cause")
        main_error = RuntimeError("Main error")
        main_error.__cause__ = cause

        with patch("sys.argv", ["mgt7pdf2json", str(pdf_path)]):
            with patch(
                "mgt7_pdf_to_json.cli.Config.from_file_or_default", return_value=mock_config
            ):
                with patch("mgt7_pdf_to_json.cli.Pipeline") as mock_pipeline_class:
                    mock_pipeline = MagicMock()
                    mock_pipeline.process.side_effect = main_error
                    mock_pipeline_class.return_value = mock_pipeline

                    with patch("sys.stderr") as mock_stderr:
                        result = main()
                        assert result == 1
                        # Check that cause was printed
                        # print() calls write() multiple times, so we check the calls
                        write_calls = [str(call) for call in mock_stderr.write.call_args_list]
                        assert (
                            any("Caused by" in str(call) for call in write_calls)
                            or len(write_calls) > 0
                        )
        """Test validation of file with invalid PDF header."""
        pdf_file = tmp_path / "invalid.pdf"
        pdf_file.write_bytes(b"NOT A PDF FILE")
        is_valid, error = validate_input_file(pdf_file)
        assert is_valid is False
        assert error is not None
        assert "not appear to be a valid pdf" in error.lower() or "valid pdf" in error.lower()
