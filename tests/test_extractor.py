"""Tests for PDF extractor."""

from unittest.mock import MagicMock, patch

import pytest

from mgt7_pdf_to_json.exceptions import ExtractionError, UnsupportedFormatError
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

    def test_extract_table_extraction_error(self, tmp_path):
        """Test extraction when table extraction fails on a page."""
        extractor = PdfPlumberExtractor()

        # Use real PDF and mock extract_tables to raise an exception
        pdf_path = tmp_path / "test.pdf"
        pdf_content = b"%PDF-1.4\n%%\xe2\xe3\xe4\xe5\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Contents 4 0 R>>endobj 4 0 obj<</Length 44>>stream\nBT\n/F1 12 Tf\n100 700 Td\n(Test) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000054 00000 n\n0000000120 00000 n\n0000000220 00000 n\ntrailer<</Size 5/Root 1 0 R>>startxref\n280\n%%EOF"
        pdf_path.write_bytes(pdf_content)

        # Mock pdfplumber.open to return a PDF with pages that have extract_tables raising exception
        with patch("mgt7_pdf_to_json.extractor.pdfplumber.open") as mock_open:
            mock_pdf = MagicMock()
            mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
            mock_pdf.__exit__ = MagicMock(return_value=False)
            mock_open.return_value = mock_pdf

            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Some text"
            mock_page.extract_tables.side_effect = Exception("Table extraction error")
            mock_pdf.pages = [mock_page]

            # Should continue processing despite table extraction error
            result = extractor.extract(str(pdf_path))
            assert result is not None
            assert result.text == "Some text"

    def test_extract_page_processing_error(self, tmp_path):
        """Test extraction when page processing fails."""
        extractor = PdfPlumberExtractor()

        # Create a minimal PDF
        pdf_path = tmp_path / "test.pdf"
        pdf_content = b"%PDF-1.4\n%%\xe2\xe3\xe4\xe5\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Contents 4 0 R>>endobj 4 0 obj<</Length 44>>stream\nBT\n/F1 12 Tf\n100 700 Td\n(Test) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000054 00000 n\n0000000120 00000 n\n0000000220 00000 n\ntrailer<</Size 5/Root 1 0 R>>startxref\n280\n%%EOF"
        pdf_path.write_bytes(pdf_content)

        # Mock page to raise exception during processing, but have another page with text
        with patch("mgt7_pdf_to_json.extractor.pdfplumber.open") as mock_open:
            mock_pdf = MagicMock()
            mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
            mock_pdf.__exit__ = MagicMock(return_value=False)
            mock_open.return_value = mock_pdf

            # First page raises exception, second page has text
            mock_page1 = MagicMock()
            mock_page1.extract_text.side_effect = Exception("Page processing error")
            mock_page2 = MagicMock()
            mock_page2.extract_text.return_value = "Some text"
            mock_page2.extract_tables.return_value = []
            mock_pdf.pages = [mock_page1, mock_page2]

            # Should continue processing and add empty text for failed page
            result = extractor.extract(str(pdf_path))
            assert result is not None
            # Failed page should have empty text, but we should have text from second page
            assert result.text == "Some text"
            # Check that we have 2 pages, one with empty text
            assert len(result.pages) == 2
            assert any(p.get("text") == "" for p in result.pages)

    def test_extract_no_extractable_text(self, tmp_path):
        """Test extraction when PDF has no extractable text."""
        extractor = PdfPlumberExtractor()

        # Create a minimal PDF with no text
        pdf_path = tmp_path / "no_text.pdf"
        pdf_content = b"%PDF-1.4\n%%\xe2\xe3\xe4\xe5\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000054 00000 n\n0000000120 00000 n\ntrailer<</Size 4/Root 1 0 R>>startxref\n180\n%%EOF"
        pdf_path.write_bytes(pdf_content)

        with patch("mgt7_pdf_to_json.extractor.pdfplumber.open") as mock_open:
            mock_pdf = MagicMock()
            mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
            mock_pdf.__exit__ = MagicMock(return_value=False)
            mock_open.return_value = mock_pdf

            mock_page = MagicMock()
            mock_page.extract_text.return_value = ""  # No text
            mock_page.extract_tables.return_value = []  # No tables
            mock_pdf.pages = [mock_page]

            with pytest.raises(UnsupportedFormatError, match="No extractable text"):
                extractor.extract(str(pdf_path))

    def test_extract_pdf_syntax_error(self, tmp_path):
        """Test extraction when PDF has syntax error (covers lines 173-180)."""
        from unittest.mock import patch

        extractor = PdfPlumberExtractor()

        # Create a minimal PDF
        pdf_path = tmp_path / "invalid.pdf"
        pdf_content = b"%PDF-1.4\n%%\xe2\xe3\xe4\xe5\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Contents 4 0 R>>endobj 4 0 obj<</Length 44>>stream\nBT /F1 12 Tf 100 700 Td (Test) Tj ET\nendstream endobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000054 00000 n\n0000000120 00000 n\n0000000200 00000 n\ntrailer<</Size 5/Root 1 0 R>>startxref\n280\n%%EOF"
        pdf_path.write_bytes(pdf_content)

        # Mock pdfplumber.open to raise an exception with "PDFSyntaxError" in the name
        class PDFSyntaxError(Exception):
            pass

        with patch(
            "mgt7_pdf_to_json.extractor.pdfplumber.open",
            side_effect=PDFSyntaxError("PDF syntax error"),
        ):
            with pytest.raises(ExtractionError, match="PDF syntax error"):
                extractor.extract(str(pdf_path))

    def test_extract_file_not_found_re_raise(self, tmp_path):
        """Test extraction re-raises FileNotFoundError (covers line 168)."""
        extractor = PdfPlumberExtractor()
        nonexistent_path = tmp_path / "nonexistent.pdf"

        # Ensure file doesn't exist
        assert not nonexistent_path.exists()
        with pytest.raises(FileNotFoundError):
            extractor.extract(str(nonexistent_path))

    def test_extract_generic_exception(self, tmp_path):
        """Test extraction when generic exception occurs."""
        extractor = PdfPlumberExtractor()

        pdf_path = tmp_path / "test.pdf"
        pdf_content = b"%PDF-1.4\n%%\xe2\xe3\xe4\xe5\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000054 00000 n\n0000000120 00000 n\ntrailer<</Size 4/Root 1 0 R>>startxref\n180\n%%EOF"
        pdf_path.write_bytes(pdf_content)

        with patch(
            "mgt7_pdf_to_json.extractor.pdfplumber.open", side_effect=Exception("Generic error")
        ):
            with pytest.raises(ExtractionError, match="Failed to extract"):
                extractor.extract(str(pdf_path))
