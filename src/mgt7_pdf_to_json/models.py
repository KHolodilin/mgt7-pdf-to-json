"""Data models for pipeline stages."""

from typing import Any

from pydantic import BaseModel


class RawDocument(BaseModel):
    """Raw extracted document from PDF."""

    text: str
    pages: list[dict[str, Any]]
    tables: list[dict[str, Any]]
    metadata: dict[str, Any] = {}


class NormalizedDocument(BaseModel):
    """Normalized document after cleaning."""

    text: str
    sections: dict[str, str] = {}
    metadata: dict[str, Any] = {}


class ParsedDocument(BaseModel):
    """Parsed document with structured data."""

    form_type: str  # "MGT-7" or "MGT-7A"
    company: dict[str, Any] = {}
    financial_year: dict[str, Any] = {}
    data: dict[str, Any] = {}
    metadata: dict[str, Any] = {}
