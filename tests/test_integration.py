"""Integration tests with real PDF files."""

import json

import pytest

from mgt7_pdf_to_json import Config, Pipeline


@pytest.mark.integration
class TestIntegration:
    """Integration tests with real PDFs."""

    def test_process_mgt7_pdf(self, mgt7_pdf_path, tmp_path):
        """Test processing MGT-7 PDF."""
        config = Config.default()
        config.artifacts.enabled = False  # Disable artifacts for tests
        pipeline = Pipeline(config)

        output_path = tmp_path / "output.json"
        result = pipeline.process(str(mgt7_pdf_path), str(output_path))

        # Validate structure
        assert "meta" in result
        assert "data" in result
        assert "warnings" in result
        assert "errors" in result

        # Validate meta
        meta = result["meta"]
        assert meta["request_id"]
        assert meta["schema_version"] == "1.0"
        assert meta["form_type"] in ["MGT-7", "MGT-7A"]
        assert "financial_year" in meta

        # Validate output file exists
        assert output_path.exists()

        # Validate JSON can be loaded and has same structure
        with open(output_path) as f:
            loaded = json.load(f)
            assert loaded["meta"]["schema_version"] == result["meta"]["schema_version"]
            assert loaded["meta"]["form_type"] == result["meta"]["form_type"]
            assert "data" in loaded
            assert "warnings" in loaded
            assert "errors" in loaded

    def test_process_mgt7a_pdf(self, mgt7a_pdf_path, tmp_path):
        """Test processing MGT-7A PDF."""
        config = Config.default()
        config.artifacts.enabled = False
        pipeline = Pipeline(config)

        output_path = tmp_path / "output.json"
        result = pipeline.process(str(mgt7a_pdf_path), str(output_path))

        # Validate structure
        assert "meta" in result
        meta = result["meta"]
        assert meta["form_type"] == "MGT-7A" or meta["form_type"] == "MGT-7"
        assert output_path.exists()
