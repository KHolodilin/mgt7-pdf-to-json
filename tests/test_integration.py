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

    def test_process_with_parsed_fields_count_else_branch(self, mgt7_pdf_path, tmp_path):
        """Test processing with parsed_fields_count else branch (non-dict, non-list)."""
        from unittest.mock import patch

        config = Config.default()
        config.artifacts.enabled = False
        pipeline = Pipeline(config)

        # Mock parser to return ParsedDocument with non-dict, non-list values in data
        # This will trigger the else branch in parsed_fields_count calculation
        original_parse = pipeline.parser.parse

        def mock_parse(doc, raw_tables):
            parsed = original_parse(doc, raw_tables)
            # Add a non-dict, non-list value to data
            parsed.data["simple_string"] = "test_value"
            return parsed

        with patch.object(pipeline.parser, "parse", side_effect=mock_parse):
            output_path = tmp_path / "output.json"
            result = pipeline.process(str(mgt7_pdf_path), str(output_path), include_stats=True)

            # This should cover the else branch in parsed_fields_count calculation
            assert "meta" in result
            if "statistics" in result["meta"]:
                assert "parsed_fields_count" in result["meta"]["statistics"]

    def test_process_with_validation_errors(self, mgt7_pdf_path, tmp_path):
        """Test processing with validation errors (covers logger.debug for errors, line 257)."""
        from unittest.mock import patch

        from mgt7_pdf_to_json.mappers import get_mapper

        config = Config.default()
        config.artifacts.enabled = False
        pipeline = Pipeline(config)

        # Mock mapper to return output that will trigger validation errors
        # by removing required fields
        original_get_mapper = get_mapper

        def mock_get_mapper(mapper_name):
            mapper = original_get_mapper(mapper_name)

            original_map = mapper.map

            def mock_map(parsed_doc, request_id, pdf_name):
                output = original_map(parsed_doc, request_id, pdf_name)
                # Remove required fields to trigger validation errors
                if "meta" in output and "form_type" in output["meta"]:
                    del output["meta"]["form_type"]
                return output

            mapper.map = mock_map
            return mapper

        with patch("mgt7_pdf_to_json.pipeline.get_mapper", side_effect=mock_get_mapper):
            output_path = tmp_path / "output.json"
            result = pipeline.process(str(mgt7_pdf_path), str(output_path))

            # This should cover logger.debug for errors path (line 257)
            assert "errors" in result
            assert len(result["errors"]) > 0

    def test_process_without_meta_in_output(self, mgt7_pdf_path, tmp_path):
        """Test processing when meta doesn't exist in output (covers line 328)."""
        from unittest.mock import patch

        from mgt7_pdf_to_json.mappers import get_mapper

        config = Config.default()
        config.artifacts.enabled = False
        pipeline = Pipeline(config)

        # Mock mapper to return output without meta
        original_get_mapper = get_mapper

        def mock_get_mapper(mapper_name):
            mapper = original_get_mapper(mapper_name)

            original_map = mapper.map

            def mock_map(parsed_doc, request_id, pdf_name):
                output = original_map(parsed_doc, request_id, pdf_name)
                # Remove meta to test the "if 'meta' not in output" branch (line 328)
                if "meta" in output:
                    del output["meta"]
                return output

            mapper.map = mock_map
            return mapper

        with patch("mgt7_pdf_to_json.pipeline.get_mapper", side_effect=mock_get_mapper):
            output_path = tmp_path / "output.json"
            result = pipeline.process(str(mgt7_pdf_path), str(output_path), include_stats=True)

            # This should cover the "if 'meta' not in output" branch (line 328)
            assert "meta" in result
            assert "statistics" in result["meta"]

    def test_process_with_artifacts_cleanup(self, mgt7_pdf_path, tmp_path):
        """Test processing with artifacts enabled (covers cleanup call)."""
        config = Config.default()
        config.artifacts.enabled = True
        config.logging.file = str(tmp_path / "logs")
        pipeline = Pipeline(config)

        output_path = tmp_path / "output.json"
        result = pipeline.process(str(mgt7_pdf_path), str(output_path))

        # This should cover the cleanup call when artifacts are enabled
        assert "meta" in result
