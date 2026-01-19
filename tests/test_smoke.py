"""Smoke tests for CLI."""

import json
import subprocess

import pytest


@pytest.mark.smoke
class TestSmoke:
    """Smoke tests for CLI with real PDFs."""

    def test_cli_mgt7_pdf(self, mgt7_pdf_path, tmp_path):
        """Test CLI with MGT-7 PDF."""
        output_path = tmp_path / "output.json"

        result = subprocess.run(
            ["mgt7pdf2json", str(mgt7_pdf_path), "-o", str(output_path)],
            capture_output=True,
            text=True,
        )

        # Check exit code
        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        # Check output file exists
        assert output_path.exists()

        # Validate JSON structure
        with open(output_path) as f:
            output = json.load(f)

            assert "meta" in output
            assert "data" in output
            assert output["meta"]["request_id"]
            assert output["meta"]["schema_version"] == "1.0"

    def test_cli_mgt7a_pdf(self, mgt7a_pdf_path, tmp_path):
        """Test CLI with MGT-7A PDF."""
        output_path = tmp_path / "output.json"

        result = subprocess.run(
            ["mgt7pdf2json", str(mgt7a_pdf_path), "-o", str(output_path)],
            capture_output=True,
            text=True,
        )

        # Check exit code
        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        # Check output file exists
        assert output_path.exists()

        # Validate JSON
        with open(output_path) as f:
            output = json.load(f)
            assert output["meta"]["request_id"]
