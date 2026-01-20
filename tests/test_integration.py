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

    def test_process_with_statistics(self, mgt7_pdf_path, tmp_path):
        """Test processing with statistics enabled."""
        config = Config.default()
        config.artifacts.enabled = False
        pipeline = Pipeline(config)

        output_path = tmp_path / "output.json"
        result = pipeline.process(str(mgt7_pdf_path), str(output_path), include_stats=True)

        # Validate statistics in output
        assert "meta" in result
        assert "statistics" in result["meta"]
        stats = result["meta"]["statistics"]
        assert "processing_start_time" in stats
        assert "processing_end_time" in stats
        assert "pages_count" in stats
        assert "tables_count" in stats
        assert "parsed_fields_count" in stats
        assert "processing_total_duration_ms" in stats
        assert stats["pages_count"] > 0

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

    def test_process_without_statistics(self, mgt7_pdf_path, tmp_path):
        """Test processing without statistics (default)."""
        config = Config.default()
        config.artifacts.enabled = False
        pipeline = Pipeline(config)

        output_path = tmp_path / "output.json"
        result = pipeline.process(str(mgt7_pdf_path), str(output_path), include_stats=False)

        # Validate statistics NOT in output
        assert "meta" in result
        assert "statistics" not in result["meta"]

    def test_process_error_handling(self, tmp_path):
        """Test error handling in pipeline."""
        config = Config.default()
        config.artifacts.enabled = False
        pipeline = Pipeline(config)

        # Use non-existent file to trigger error
        with pytest.raises(FileNotFoundError):
            pipeline.process("nonexistent.pdf", str(tmp_path / "output.json"))
