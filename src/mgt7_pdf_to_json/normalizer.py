"""Document text normalization and cleaning."""

import re

from mgt7_pdf_to_json.logging_ import LoggerFactory
from mgt7_pdf_to_json.models import NormalizedDocument, RawDocument

logger = LoggerFactory.get_logger("normalizer")


class DocumentNormalizer:
    """Normalize and clean extracted document text."""

    def normalize(self, raw_doc: RawDocument) -> NormalizedDocument:
        """
        Normalize raw document text.

        Args:
            raw_doc: Raw document from extractor

        Returns:
            Normalized document with cleaned text
        """
        original_length = len(raw_doc.text)
        logger.debug(f"Normalizing document: {original_length} characters input")

        # Clean text
        normalized_text = self._clean_text(raw_doc.text)
        normalized_length = len(normalized_text)
        reduction_pct = ((original_length - normalized_length) / original_length * 100) if original_length > 0 else 0
        logger.debug(
            f"Text normalization complete: {normalized_length} characters output "
            f"({reduction_pct:.1f}% reduction)"
        )

        # TODO: Split into sections (will be implemented in SectionSplitter)
        sections: dict[str, str] = {}

        metadata = {
            "original_length": len(raw_doc.text),
            "normalized_length": len(normalized_text),
            **raw_doc.metadata,
        }

        return NormalizedDocument(
            text=normalized_text,
            sections=sections,
            metadata=metadata,
        )

    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text.

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove special characters that might interfere with parsing
        # But keep line breaks for structure
        text = re.sub(r"\r\n", "\n", text)
        text = re.sub(r"\r", "\n", text)

        # Normalize multiple newlines
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join(lines)

        # Remove leading/trailing whitespace from entire text
        text = text.strip()

        return text
