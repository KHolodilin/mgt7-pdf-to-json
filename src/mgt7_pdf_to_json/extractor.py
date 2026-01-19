"""PDF text and table extraction."""

from __future__ import annotations

from pathlib import Path

import pdfplumber

from mgt7_pdf_to_json.logging_ import LoggerFactory
from mgt7_pdf_to_json.models import RawDocument

logger = LoggerFactory.get_logger("extractor")


class PdfPlumberExtractor:
    """Extract text and tables from PDF using pdfplumber."""

    def extract(self, pdf_path: str | Path) -> RawDocument:
        """
        Extract text and tables from PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            RawDocument with extracted content

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If PDF cannot be processed (e.g., scanned/image-only)
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        logger.debug(f"Extracting from PDF: {pdf_path}")
        file_size = pdf_path.stat().st_size
        logger.debug(f"PDF file size: {file_size} bytes ({file_size / 1024:.2f} KB)")

        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                logger.debug(f"PDF opened successfully: {total_pages} page(s)")

                # Extract text from all pages
                pages_text = []
                pages_tables = []

                for i, page in enumerate(pdf.pages):
                    logger.debug(f"Processing page {i + 1}/{total_pages}")

                    # Extract text
                    text = page.extract_text()
                    text_length = len(text) if text else 0
                    logger.debug(f"Page {i + 1}: extracted {text_length} characters of text")

                    if not text:
                        logger.warning(f"No text found on page {i + 1}")
                        # In strict mode, this would be an error
                        # For now, we'll treat it as a warning
                        text = ""

                    pages_text.append({"page": i + 1, "text": text})

                    # Extract tables
                    tables = page.extract_tables()
                    if tables:
                        logger.debug(f"Page {i + 1}: found {len(tables)} table(s)")
                        for table_idx, table in enumerate(tables):
                            rows = len(table) if table else 0
                            cols = len(table[0]) if table and table[0] else 0
                            logger.debug(
                                f"Page {i + 1}, Table {table_idx + 1}: {rows} rows x {cols} columns"
                            )
                        pages_tables.extend([{"page": i + 1, "table": table} for table in tables])
                    else:
                        logger.debug(f"Page {i + 1}: no tables found")

                # Combine all text
                full_text = "\n\n".join([str(p["text"]) for p in pages_text if p.get("text")])
                full_text_length = len(full_text)
                logger.debug(f"Combined text length: {full_text_length} characters")

                # Check if we have any extractable text
                if not full_text.strip():
                    error_msg = (
                        "No extractable text found in PDF. "
                        "This may be a scanned/image-only PDF. OCR is required."
                    )
                    logger.error(error_msg)
                    logger.debug(f"Pages processed: {len(pages_text)}, Tables found: {len(pages_tables)}")
                    from mgt7_pdf_to_json.exceptions import UnsupportedFormatError

                    raise UnsupportedFormatError(error_msg)

                metadata = {
                    "total_pages": total_pages,
                    "total_tables": len(pages_tables),
                    "file_size": file_size,
                }

                logger.debug(
                    f"Extraction complete: {total_pages} pages, {len(pages_tables)} tables, "
                    f"{full_text_length} characters"
                )

                return RawDocument(
                    text=full_text,
                    pages=pages_text,
                    tables=pages_tables,
                    metadata=metadata,
                )

        except UnsupportedFormatError:
            # Re-raise our custom exception
            raise
        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error extracting PDF: {e}", exc_info=True)
            from mgt7_pdf_to_json.exceptions import ExtractionError

            raise ExtractionError(f"Failed to extract PDF: {e}") from e
