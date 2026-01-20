"""Date parsing utilities."""

from __future__ import annotations

import re
from datetime import datetime


def parse_date(date_str: str, default_format: str = "DD/MM/YYYY") -> str | None:
    """
    Parse date string and normalize to DD/MM/YYYY format.

    Supports multiple input formats including DD/MM/YYYY, DD-MM-YYYY,
    and YYYY-MM-DD (ISO). Handles 2-digit years by inferring century.

    Args:
        date_str: Date string to parse
        default_format: Default format hint (not used currently)

    Returns:
        Normalized date string in DD/MM/YYYY format or None if cannot parse

    Example:
        >>> parse_date("31/03/2023")
        '31/03/2023'
        >>> parse_date("31-03-2023")
        '31/03/2023'
        >>> parse_date("2023-03-31")
        '31/03/2023'
        >>> parse_date("31/03/23")
        '31/03/2023'
    """
    if not date_str or not date_str.strip():
        return None

    date_str = date_str.strip()

    # Common date patterns
    patterns = [
        (r"(\d{1,2})/(\d{1,2})/(\d{2,4})", "%d/%m/%Y"),  # DD/MM/YYYY or DD/MM/YY
        (r"(\d{1,2})-(\d{1,2})-(\d{2,4})", "%d-%m-%Y"),  # DD-MM-YYYY
        (r"(\d{4})-(\d{1,2})-(\d{1,2})", "%Y-%m-%d"),  # YYYY-MM-DD (ISO)
    ]

    for pattern, fmt in patterns:
        match = re.match(pattern, date_str)
        if match:
            try:
                # Reconstruct for parsing
                parts = match.groups()
                if fmt == "%d/%m/%Y":
                    day, month, year = parts
                    year_int = int(year)
                    if len(year) == 2:
                        year_int = 2000 + year_int if year_int < 50 else 1900 + year_int
                    normalized = f"{int(day):02d}/{int(month):02d}/{year_int}"
                elif fmt == "%d-%m-%Y":
                    day, month, year = parts
                    year_int = int(year)
                    if len(year) == 2:
                        year_int = 2000 + year_int if year_int < 50 else 1900 + year_int
                    normalized = f"{int(day):02d}/{int(month):02d}/{year_int}"
                elif fmt == "%Y-%m-%d":
                    year, month, day = parts
                    normalized = f"{int(day):02d}/{int(month):02d}/{int(year)}"
                else:
                    normalized = date_str

                # Validate date
                try:
                    datetime.strptime(normalized, "%d/%m/%Y")
                    return normalized
                except ValueError:
                    continue

            except (ValueError, IndexError):
                continue

    # If no pattern matches, try to extract date-like substring
    date_match = re.search(r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", date_str)
    if date_match:
        return parse_date(date_match.group(1))

    return None


def format_date_for_output(date_str: str | None, use_iso: bool = False) -> str:
    """
    Format date string for output.

    Converts date from DD/MM/YYYY format to either the same format
    or ISO format (YYYY-MM-DDTHH:MM:SSZ) if requested.

    Args:
        date_str: Date string in DD/MM/YYYY format
        use_iso: Use ISO format if True

    Returns:
        Formatted date string (empty string if input is None)

    Example:
        >>> format_date_for_output("31/03/2023")
        '31/03/2023'
        >>> format_date_for_output("31/03/2023", use_iso=True)
        '2023-03-31T00:00:00Z'
        >>> format_date_for_output(None)
        ''
    """
    if not date_str:
        return ""

    if use_iso:
        # Convert DD/MM/YYYY to ISO format
        parsed = parse_date(date_str)
        if parsed:
            try:
                dt = datetime.strptime(parsed, "%d/%m/%Y")
                return dt.isoformat() + "Z"
            except ValueError:
                pass

    return date_str
