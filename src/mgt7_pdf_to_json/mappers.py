"""Mappers for converting ParsedDocument to output JSON schemas."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any
from uuid import UUID

from mgt7_pdf_to_json.date_utils import format_date_for_output
from mgt7_pdf_to_json.logging_ import LoggerFactory
from mgt7_pdf_to_json.models import ParsedDocument

logger = LoggerFactory.get_logger("mappers")


class BaseMapper(ABC):
    """Base class for output mappers."""

    @abstractmethod
    def map(
        self, parsed: ParsedDocument, request_id: str | UUID, input_file: str
    ) -> dict[str, Any]:
        """
        Map ParsedDocument to output JSON schema.

        Args:
            parsed: Parsed document
            request_id: Request ID
            input_file: Input PDF file name

        Returns:
            Output JSON dictionary
        """
        pass

    def _format_date(self, date_str: str, use_iso: bool = False) -> str:
        """
        Format date string to DD/MM/YYYY or ISO format.

        Args:
            date_str: Date string
            use_iso: Use ISO format if True

        Returns:
            Formatted date string
        """
        return format_date_for_output(date_str, use_iso)


class DefaultMapper(BaseMapper):
    """Default mapper - full JSON output."""

    def map(
        self, parsed: ParsedDocument, request_id: str | UUID, input_file: str
    ) -> dict[str, Any]:
        """
        Map to default (full) JSON schema.

        Args:
            parsed: Parsed document
            request_id: Request ID
            input_file: Input PDF file name

        Returns:
            Default JSON output
        """
        logger.debug("Mapping to default schema")

        output: dict[str, Any] = {
            "meta": {
                "request_id": str(request_id),
                "schema_version": "1.0",
                "form_type": parsed.form_type,
                "financial_year": {
                    "from": self._format_date(parsed.financial_year.get("from", "")),
                    "to": self._format_date(parsed.financial_year.get("to", "")),
                },
                "source": {
                    "input_file": input_file,
                },
            },
            "data": {
                "company": parsed.company,
                **parsed.data,
            },
            "warnings": [],
            "errors": [],
        }

        return output


class MinimalMapper(BaseMapper):
    """Minimal mapper - minimal JSON output."""

    def map(
        self, parsed: ParsedDocument, request_id: str | UUID, input_file: str
    ) -> dict[str, Any]:
        """
        Map to minimal JSON schema.

        Args:
            parsed: Parsed document
            request_id: Request ID
            input_file: Input PDF file name

        Returns:
            Minimal JSON output
        """
        logger.debug("Mapping to minimal schema")

        # Extract only essential fields
        essential_data: dict[str, Any] = {
            "company": parsed.company,
        }

        # Include turnover_and_net_worth if available
        if "turnover_and_net_worth" in parsed.data:
            essential_data["turnover_and_net_worth"] = parsed.data["turnover_and_net_worth"]

        output: dict[str, Any] = {
            "meta": {
                "request_id": str(request_id),
                "schema_version": "1.0",
                "form_type": parsed.form_type,
                "financial_year": {
                    "from": self._format_date(parsed.financial_year.get("from", "")),
                    "to": self._format_date(parsed.financial_year.get("to", "")),
                },
                "source": {
                    "input_file": input_file,
                },
            },
            "data": essential_data,
            "warnings": [],
            "errors": [],
        }

        return output


class DbMapper(BaseMapper):
    """DB/ETL-friendly mapper."""

    def map(
        self, parsed: ParsedDocument, request_id: str | UUID, input_file: str
    ) -> dict[str, Any]:
        """
        Map to DB/ETL-friendly JSON schema.

        Args:
            parsed: Parsed document
            request_id: Request ID
            input_file: Input PDF file name

        Returns:
            DB-friendly JSON output
        """
        logger.debug("Mapping to DB schema")

        # Flatten structure for DB/ETL
        facts: dict[str, Any] = {}

        # Extract turnover and net worth
        if "turnover_and_net_worth" in parsed.data:
            tw_data = parsed.data["turnover_and_net_worth"]
            facts["turnover_inr"] = tw_data.get("turnover_inr", 0)
            facts["net_worth_inr"] = tw_data.get("net_worth_inr", 0)

        # Process tables with request_id
        tables: dict[str, Any] = {}
        for table_type, table_rows in parsed.data.items():
            if table_type == "turnover_and_net_worth":
                continue
            if isinstance(table_rows, list):
                # Add request_id to each row
                enriched_rows = []
                for row in table_rows:
                    enriched_row = {"request_id": str(request_id), **row}
                    enriched_rows.append(enriched_row)
                tables[table_type] = enriched_rows

        output: dict[str, Any] = {
            "meta": {
                "request_id": str(request_id),
                "schema_version": "1.0",
                "form_type": parsed.form_type,
                "source": {
                    "input_file": input_file,
                    "generated_at": datetime.utcnow().isoformat() + "Z",
                },
            },
            "data": {
                "company": parsed.company,
                "facts": facts,
                "tables": tables,
            },
            "warnings": [],
            "errors": [],
        }

        # Note: DB mapper doesn't include financial_year in meta (as per example)
        # But we can add it if needed

        return output


def get_mapper(mapper_name: str) -> BaseMapper:
    """
    Get mapper by name.

    Args:
        mapper_name: Mapper name (default, minimal, db)

    Returns:
        Mapper instance

    Raises:
        ValueError: If mapper name is unknown
    """
    mappers: dict[str, type[BaseMapper]] = {
        "default": DefaultMapper,
        "minimal": MinimalMapper,
        "db": DbMapper,
    }

    mapper_class = mappers.get(mapper_name.lower())
    if not mapper_class:
        raise ValueError(f"Unknown mapper: {mapper_name}. Available: {list(mappers.keys())}")

    return mapper_class()
