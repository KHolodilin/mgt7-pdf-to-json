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
                    page_num = i + 1
                    logger.debug(f"Processing page {page_num}/{total_pages}")

                    try:
                        # Extract text
                        text = page.extract_text()
                        text_length = len(text) if text else 0
                        logger.debug(f"Page {page_num}: extracted {text_length} characters of text")

                        if not text:
                            logger.warning(
                                f"No text found on page {page_num}/{total_pages} "
                                f"in PDF '{pdf_path.name}'. "
                                "This may indicate a scanned page or image-only content."
                            )
                            # In strict mode, this would be an error
                            # For now, we'll treat it as a warning
                            text = ""

                        pages_text.append({"page": page_num, "text": text})

                        # Extract tables
                        try:
                            tables = page.extract_tables()
                            if tables:
                                logger.debug(f"Page {page_num}: found {len(tables)} table(s)")
                                for table_idx, table in enumerate(tables):
                                    rows = len(table) if table else 0
                                    cols = len(table[0]) if table and table[0] else 0
                                    logger.debug(
                                        f"Page {page_num}, Table {table_idx + 1}: "
                                        f"{rows} rows x {cols} columns"
                                    )
                                pages_tables.extend(
                                    [{"page": page_num, "table": table} for table in tables]
                                )
                            else:
                                logger.debug(f"Page {page_num}: no tables found")
                        except Exception as table_error:
                            error_type = type(table_error).__name__
                            logger.warning(
                                f"Error extracting tables from page {page_num}/{total_pages} "
                                f"in PDF '{pdf_path.name}': {error_type}: {table_error}. "
                                "Continuing with text extraction only."
                            )
                            # Continue processing other pages
                    except Exception as page_error:
                        error_type = type(page_error).__name__
                        logger.error(
                            f"Error processing page {page_num}/{total_pages} "
                            f"in PDF '{pdf_path.name}': {error_type}: {page_error}. "
                            f"Error type: extraction failure on page {page_num}.",
                            exc_info=True,
                        )
                        # Continue processing other pages, but log the error
                        pages_text.append({"page": page_num, "text": ""})

                # Combine all text
                full_text = "\n\n".join([str(p["text"]) for p in pages_text if p.get("text")])
                full_text_length = len(full_text)
                logger.debug(f"Combined text length: {full_text_length} characters")

                # Check if we have any extractable text
                if not full_text.strip():
                    pages_without_text = [
                        p["page"] for p in pages_text if not p.get("text", "").strip()
                    ]
                    error_msg = (
                        f"No extractable text found in PDF '{pdf_path.name}' "
                        f"(total pages: {total_pages}, file size: {file_size / 1024:.2f} KB). "
                        f"Pages without text: {pages_without_text if pages_without_text else 'all'}. "
                        f"Tables found: {len(pages_tables)}. "
                        "This may be a scanned/image-only PDF. OCR is required."
                    )
                    logger.error(error_msg)
                    logger.debug(
                        f"Pages processed: {len(pages_text)}, Tables found: {len(pages_tables)}"
                    )
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
        except pdfplumber.exceptions.PDFSyntaxError as e:
            error_msg = (
                f"PDF syntax error in file '{pdf_path.name}': {e}. "
                "The PDF file may be corrupted or not a valid PDF. "
                f"File size: {file_size / 1024:.2f} KB. "
                "Please verify the file integrity."
            )
            logger.error(error_msg, exc_info=True)
            from mgt7_pdf_to_json.exceptions import ExtractionError

            raise ExtractionError(error_msg) from e
        except Exception as e:
            error_type = type(e).__name__
            error_msg = (
                f"Failed to extract PDF '{pdf_path.name}': {error_type}: {e}. "
                f"File size: {file_size / 1024:.2f} KB. "
                "Please check if the file is a valid PDF and not corrupted."
            )
            logger.error(error_msg, exc_info=True)
            from mgt7_pdf_to_json.exceptions import ExtractionError

            raise ExtractionError(error_msg) from e
