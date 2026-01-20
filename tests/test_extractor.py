"""Tests for PDF extractor."""

import pytest
from mgt7_pdf_to_json.extractor import PdfPlumberExtractor


class TestPdfPlumberExtractor:
    """Test PDF extraction."""

    def test_extract_nonexistent_file(self):
        """Test extraction from nonexistent file raises error."""
        extractor = PdfPlumberExtractor()

        with pytest.raises(FileNotFoundError):
            extractor.extract("nonexistent.pdf")

    def test_extract_real_pdf(self, mgt7_pdf_path):
        """Test extraction from real PDF file."""
        extractor = PdfPlumberExtractor()

        result = extractor.extract(mgt7_pdf_path)

        assert result.text
        assert len(result.pages) > 0
        assert "metadata" in result.model_dump()

    def test_extract_mgt7a_pdf(self, mgt7a_pdf_path):
        """Test extraction from MGT-7A PDF file."""
        extractor = PdfPlumberExtractor()

        result = extractor.extract(mgt7a_pdf_path)

        assert result.text
        assert len(result.pages) > 0
