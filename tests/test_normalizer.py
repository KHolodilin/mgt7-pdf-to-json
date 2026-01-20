"""Tests for document normalizer."""

from mgt7_pdf_to_json.models import RawDocument
from mgt7_pdf_to_json.normalizer import DocumentNormalizer


class TestDocumentNormalizer:
    """Test document normalization."""

    def test_normalize(self):
        """Test basic normalization."""
        normalizer = DocumentNormalizer()

        raw_doc = RawDocument(
            text="  Some   text\n\n\nwith    extra   spaces  ",
            pages=[],
            tables=[],
        )

        result = normalizer.normalize(raw_doc)

        assert result.text
        assert "normalized_length" in result.metadata
        assert len(result.text) <= len(raw_doc.text)

    def test_clean_text(self):
        """Test text cleaning."""
        normalizer = DocumentNormalizer()

        dirty_text = "  Line 1  \n\n\n  Line 2  \r\n  Line 3  "
        clean_text = normalizer._clean_text(dirty_text)

        assert clean_text
        assert "\n\n\n" not in clean_text
        assert "  " not in clean_text.strip()
