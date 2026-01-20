"""Document parsing components."""

from __future__ import annotations

import re
from typing import Any

from mgt7_pdf_to_json.date_utils import parse_date
from mgt7_pdf_to_json.logging_ import LoggerFactory
from mgt7_pdf_to_json.models import NormalizedDocument, ParsedDocument

logger = LoggerFactory.get_logger("parser")


class SectionSplitter:
    """Split document into sections."""

    def split(self, doc: NormalizedDocument) -> dict[str, str]:
        """
        Split normalized document into sections.

        Args:
            doc: Normalized document

        Returns:
            Dictionary mapping section names to their content
        """
        text_length = len(doc.text)
        logger.debug(f"Splitting document into sections: {text_length} characters")

        sections: dict[str, str] = {}
        text = doc.text

        # Common patterns for sections
        # MGT-7 and MGT-7A forms typically have sections marked with Roman numerals or numbers
        # Pattern: Section markers like "I.", "II.", "III." or "1.", "2.", etc.
        section_patterns = [
            r"(?i)(?:Section|Part)\s*([IVX]+|[0-9]+)[\.:]?\s*(.+?)(?=(?:Section|Part)\s*(?:[IVX]+|[0-9]+)[\.:]|$)",
            r"(?:^|\n)([IVX]+)[\.:]?\s+(.+?)(?=\n(?:[IVX]+|$))",
        ]

        # Try to extract sections using patterns
        for pattern_idx, pattern in enumerate(section_patterns):
            matches = list(re.finditer(pattern, text, re.MULTILINE | re.DOTALL))
            logger.debug(f"Pattern {pattern_idx + 1}: found {len(matches)} section(s)")
            for match in matches:
                num_groups = len(match.groups())
                section_num = match.group(1) if num_groups >= 1 else "unknown"
                section_content = match.group(2) if num_groups >= 2 else match.group(0)
                section_length = len(section_content.strip())
                logger.debug(f"Section '{section_num}': {section_length} characters")
                sections[section_num] = section_content.strip()

        # If no sections found, use full text as single section
        if not sections:
            logger.warning("No sections found, using full text")
            sections["full"] = text
        else:
            logger.debug(f"Section split complete: {len(sections)} section(s) identified")

        return sections

    def _detect_form_type(self, text: str) -> str:
        """
        Detect form type from text.

        Args:
            text: Document text

        Returns:
            Form type: "MGT-7" or "MGT-7A"
        """
        text_upper = text.upper()

        # Check for MGT-7A markers
        if "MGT-7A" in text_upper or "MGT 7A" in text_upper or "ABRIDGED" in text_upper:
            return "MGT-7A"

        # Default to MGT-7
        if "MGT-7" in text_upper or "MGT 7" in text_upper:
            return "MGT-7"

        # Try to infer from content structure
        # MGT-7A is typically shorter and simpler
        # For now, default to MGT-7
        logger.warning("Could not detect form type, defaulting to MGT-7")
        return "MGT-7"


class KeyValueParser:
    """Parse key-value pairs from text."""

    def parse(self, text: str, patterns: list[tuple[str, str]] | None = None) -> dict[str, Any]:
        """
        Parse key-value pairs from text.

        Args:
            text: Text to parse
            patterns: Optional list of (key, pattern) tuples

        Returns:
            Dictionary of parsed key-value pairs
        """
        result: dict[str, Any] = {}
        text_length = len(text)
        logger.debug(f"Parsing key-value pairs from text: {text_length} characters")

        if not patterns:
            # Default patterns for common fields
            patterns = [
                # CIN - Corporate Identity Number (21 chars: U17120DL2013PTC262515)
                (
                    "CIN",
                    r"(?:CIN|Corporate\s+Identity\s+Number)[\s:]*([A-Z][0-9]{5}[A-Z]{2}[0-9]{4}[A-Z]{3}[0-9]{6})",
                ),
                # Try to find CIN in filename if present
                ("CIN_Filename", r"([A-Z][0-9]{5}[A-Z]{2}[0-9]{4}[A-Z]{3}[0-9]{6})"),
                # Company Name - improved pattern to stop at first field
                (
                    "Company Name",
                    r"(?:Name\s+of\s+the\s+company|Company\s+Name|Name\s+of\s+the\s+Company)[\s:]*([A-Z][A-Z\s&,\.]+(?:LIMITED|LTD|PRIVATE|PVT)[^\n]*)",
                ),
                # Alternative: extract from table if available
                (
                    "Company Name Alt",
                    r"(?:\"As on filing date\"|As on filing date)[\s:]*\"?([A-Z][A-Z\s&,\.]+(?:LIMITED|LTD|PRIVATE|PVT))",
                ),
                # Financial Year - try multiple patterns
                (
                    "Financial Year End",
                    r"financial\s+year\s+ended\s+on\s*\(DD/MM/YYYY\)\s*(\d{1,2}/\d{1,2}/\d{2,4})",
                ),
                (
                    "Financial Year To",
                    r"(?:Financial\s+Year\s+To|To\s+Date|closure of\s+financial\s+year)[\s:]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                ),
                (
                    "Financial Year From",
                    r"(?:Financial\s+Year\s+From|From\s+Date)[\s:]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                ),
                # Turnover - improved pattern to capture full number
                (
                    "Turnover",
                    r"(?:\*\s*)?Turnover[\s:]*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)",
                ),
                # Alternative turnover pattern
                (
                    "Turnover_Alt",
                    r"i\s*\*\s*Turnover[\s\n]*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)",
                ),
                # Net Worth - improved pattern to capture full number
                (
                    "Net Worth",
                    r"(?:\*\s*)?Net\s+worth\s+of\s+the\s+Company[\s:]*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)",
                ),
                # Alternative net worth pattern
                (
                    "Net Worth_Alt",
                    r"ii\s*\*\s*Net\s+worth\s+of\s+the\s+Company[\s\n]*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)",
                ),
            ]

        for key, pattern in patterns:
            try:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    value = match.group(1).strip()
                    # Clean company name
                    if "Company Name" in key:
                        # Remove extra text after company name
                        value = re.split(r"\s+(?:Registered|Latitude|Page|\()", value, maxsplit=1)[
                            0
                        ]
                        value = re.sub(r"\s+", " ", value).strip()
                        # Remove duplicates (sometimes company name is repeated)
                        words = value.split()
                        seen = set()
                        unique_words = []
                        for word in words:
                            if (
                                word.lower() not in seen or word.upper() == word
                            ):  # Keep uppercase words
                                unique_words.append(word)
                                seen.add(word.lower())
                        value = " ".join(unique_words)
                    # Try to convert to number if applicable
                    if "Turnover" in key or "Net Worth" in key:
                        value = self._parse_value(value)
                    # Don't overwrite existing values unless this is a fallback pattern
                    if key not in result or not result[key]:
                        result[key] = value
            except Exception as e:
                error_type = type(e).__name__
                logger.warning(
                    f"Error parsing field '{key}' from text: {error_type}: {e}. "
                    f"Pattern used: {pattern[:50]}... "
                    "This field may be missing or in an unexpected format. "
                    "Continuing with other fields."
                )

        # Handle CIN fallback - use filename pattern if main pattern failed
        if "CIN" not in result or not result["CIN"]:
            if "CIN_Filename" in result:
                result["CIN"] = result.pop("CIN_Filename")

        # Handle company name fallback
        if "Company Name" not in result or not result["Company Name"]:
            if "Company Name Alt" in result:
                result["Company Name"] = result.pop("Company Name Alt")

        # Handle turnover/net worth fallbacks
        if "Turnover_Alt" in result and "Turnover" not in result:
            result["Turnover"] = result.pop("Turnover_Alt")
        elif (
            "Turnover_Alt" in result
            and isinstance(result.get("Turnover"), (int, float))
            and result["Turnover"] < 1000
        ):
            # Use alternative if main pattern got partial match
            result["Turnover"] = result.pop("Turnover_Alt")

        if "Net Worth_Alt" in result and "Net Worth" not in result:
            result["Net Worth"] = result.pop("Net Worth_Alt")
        elif (
            "Net Worth_Alt" in result
            and isinstance(result.get("Net Worth"), (int, float))
            and result["Net Worth"] < 1000
        ):
            # Use alternative if main pattern got partial match
            result["Net Worth"] = result.pop("Net Worth_Alt")

        # Handle financial year - infer from end date if only end date found
        if "Financial Year End" in result and "Financial Year To" not in result:
            # Normalize date format
            normalized_date = parse_date(result["Financial Year End"])
            if normalized_date:
                result["Financial Year To"] = normalized_date
                # Try to infer from date (usually ends on 31/03/YYYY, starts on 01/04/YYYY-1)
                date_match = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", normalized_date)
                if date_match:
                    day, month, year = date_match.groups()
                    year_int = int(year)
                    if month == "03" and day == "31":
                        # Financial year ends 31/03/YYYY, starts 01/04/(YYYY-1)
                        prev_year = year_int - 1
                        result["Financial Year From"] = f"01/04/{prev_year}"
            else:
                result["Financial Year To"] = result["Financial Year End"]

        # Normalize all date fields
        for key in ["Financial Year From", "Financial Year To", "Financial Year End"]:
            if key in result and result[key]:
                try:
                    normalized = parse_date(result[key])
                    if normalized:
                        result[key] = normalized
                    else:
                        logger.warning(
                            f"Could not parse date for field '{key}': "
                            f"'{result[key]}'. "
                            "Date format may be unexpected. "
                            "Expected formats: DD/MM/YYYY, DD-MM-YYYY, or similar."
                        )
                except Exception as e:
                    error_type = type(e).__name__
                    logger.warning(
                        f"Error parsing date for field '{key}': {error_type}: {e}. "
                        f"Raw value: '{result[key]}'. "
                        "Date format may be invalid or unexpected."
                    )

        return result

    def _parse_value(self, value: str) -> Any:
        """
        Parse and convert value to appropriate type.

        Args:
            value: Raw value string

        Returns:
            Parsed value (int, float, bool, or str)
        """
        if not value:
            return value

        # Try boolean
        if value.upper() in ["YES", "Y", "TRUE", "1"]:
            return True
        if value.upper() in ["NO", "N", "FALSE", "0"]:
            return False

        # Try number
        # Remove commas and whitespace, handle Indian number format
        clean_value = value.replace(",", "").replace(" ", "").strip()

        # Handle cases where number is part of text (e.g., "891114630" in longer text)
        # Extract first complete number
        number_match = re.search(r"(\d{1,3}(?:,\d{3})*(?:\.\d+)?)", value.replace(",", ""))
        if number_match:
            clean_value = number_match.group(1).replace(",", "")

        try:
            # Try as float first (handles decimals)
            float_val = float(clean_value)
            # Return as int if no decimal part
            if float_val.is_integer():
                return int(float_val)
            return float_val
        except ValueError as e:
            logger.debug(
                f"Could not parse numeric value '{value}': {e}. "
                "Returning as string. "
                "Possible reasons: value contains non-numeric characters or unexpected format."
            )

        # Return as string
        return value


class TableParser:
    """Parse tables from extracted table data."""

    def parse(self, tables: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Parse tables from extracted table data.

        Args:
            tables: List of table dictionaries with 'page' and 'table' keys

        Returns:
            Dictionary of parsed table data
        """
        result: dict[str, Any] = {}
        total_tables = len(tables)
        logger.debug(f"Parsing {total_tables} table(s)")

        for table_idx, table_data in enumerate(tables):
            table = table_data.get("table", [])
            page = table_data.get("page", 0)

            if not table:
                logger.debug(f"Table {table_idx + 1} is empty, skipping")
                continue

            rows = len(table)
            cols = len(table[0]) if table else 0
            logger.debug(f"Table {table_idx + 1} (page {page}): {rows} rows x {cols} columns")

            # Try to identify table type from headers
            table_type = self._identify_table_type(table)
            logger.debug(f"Table {table_idx + 1} identified as type: {table_type}")

            # Parse table rows
            parsed_rows = self._parse_table_rows(table, table_type)
            logger.debug(f"Table {table_idx + 1}: parsed {len(parsed_rows)} row(s)")

            if table_type not in result:
                result[table_type] = []

            result[table_type].extend(parsed_rows)

        if result:
            total_parsed = sum(len(rows) for rows in result.values())
            logger.debug(
                f"Table parsing complete: {total_parsed} total row(s) across {len(result)} table type(s)"
            )

        return result

    def _identify_table_type(self, table: list[list[Any]]) -> str:
        """
        Identify table type from headers.

        Args:
            table: Table data (list of rows)

        Returns:
            Table type identifier
        """
        if not table:
            return "unknown"

        # Get first row as header
        header = [str(cell).strip().upper() if cell else "" for cell in table[0]]

        header_text = " ".join(header)

        # Check for common table types
        if any(word in header_text for word in ["BOARD", "MEETING", "DIRECTOR"]):
            return "board_meetings"

        if any(word in header_text for word in ["SHARE", "CAPITAL", "EQUITY"]):
            return "share_capital"

        if any(word in header_text for word in ["DIRECTOR", "PROMOTER"]):
            return "directors"

        return "unknown"

    def _parse_table_rows(self, table: list[list[Any]], table_type: str) -> list[dict[str, Any]]:
        """
        Parse table rows based on table type.

        Args:
            table: Table data
            table_type: Type of table

        Returns:
            List of parsed row dictionaries
        """
        if not table or len(table) < 2:
            return []

        header = [str(cell).strip() if cell else "" for cell in table[0]]
        rows = []

        # Normalize header names for better matching
        normalized_header = []
        for h in header:
            h_lower = h.lower().replace("\n", " ").strip()
            # Map common variations
            if "date" in h_lower and "meeting" in h_lower:
                normalized_header.append("date")
            elif "directors" in h_lower and "total" in h_lower:
                normalized_header.append("directors_total")
            elif "directors" in h_lower and ("attended" in h_lower or "attendance" in h_lower):
                normalized_header.append("directors_attended")
            elif "s.no" in h_lower or "serial" in h_lower:
                normalized_header.append("s_no")
            else:
                normalized_header.append(h)

        for row_data in table[1:]:
            row_dict = {}
            for i, cell in enumerate(row_data):
                if i < len(header) and header[i]:
                    value = self._parse_cell_value(cell)
                    # Use normalized header if available, otherwise original
                    key = normalized_header[i] if i < len(normalized_header) else header[i]
                    row_dict[key] = value

            # Post-process board_meetings rows
            if table_type == "board_meetings" and row_dict:
                # Normalize date format
                if "date" in row_dict:
                    date_str = str(row_dict["date"])
                    # Extract date in DD/MM/YYYY format
                    date_match = re.search(r"(\d{1,2}/\d{1,2}/\d{2,4})", date_str)
                    if date_match:
                        row_dict["date"] = date_match.group(1)
                    else:
                        row_dict["date"] = date_str

                # Ensure numeric fields are numbers
                if "directors_total" in row_dict:
                    row_dict["directors_total"] = self._parse_cell_value(
                        row_dict["directors_total"]
                    )
                if "directors_attended" in row_dict:
                    row_dict["directors_attended"] = self._parse_cell_value(
                        row_dict["directors_attended"]
                    )

                # Keep only relevant fields
                filtered_row = {}
                for key in ["date", "directors_total", "directors_attended", "s_no"]:
                    if key in row_dict:
                        filtered_row[key] = row_dict[key]
                if filtered_row:
                    rows.append(filtered_row)
            elif row_dict:
                rows.append(row_dict)

        return rows

    def _parse_cell_value(self, cell: Any) -> Any:
        """
        Parse individual cell value.

        Args:
            cell: Cell value

        Returns:
            Parsed value
        """
        if cell is None:
            return None

        value_str = str(cell).strip()

        # Try to convert to number
        clean_value = value_str.replace(",", "").strip()
        try:
            if "." in clean_value:
                return float(clean_value)
            return int(clean_value)
        except ValueError:
            pass

        return value_str


class DocumentParser:
    """Main document parser."""

    def __init__(self):
        """Initialize parser with sub-components."""
        self.section_splitter = SectionSplitter()
        self.key_value_parser = KeyValueParser()
        self.table_parser = TableParser()

    def parse(self, doc: NormalizedDocument, raw_tables: list[dict[str, Any]]) -> ParsedDocument:
        """
        Parse normalized document into structured data.

        Args:
            doc: Normalized document
            raw_tables: Raw table data from extractor

        Returns:
            Parsed document with structured data

        Raises:
            ParsingError: If critical parsing fails
        """
        logger.debug("Parsing document")

        try:
            # Split into sections
            sections = self.section_splitter.split(doc)

            # Detect form type
            form_type = self.section_splitter._detect_form_type(doc.text)

            # Parse key-value pairs from full text
            kv_data = self.key_value_parser.parse(doc.text)

            # Parse tables
            table_data = self.table_parser.parse(raw_tables)

            # Validate critical fields and provide helpful error messages
            missing_fields = []
            if not kv_data.get("CIN"):
                missing_fields.append("CIN (Corporate Identity Number)")
            if not kv_data.get("Company Name"):
                missing_fields.append("Company Name")
            if not kv_data.get("Financial Year From") and not kv_data.get("Financial Year To"):
                missing_fields.append("Financial Year (From/To)")

            if missing_fields:
                logger.warning(
                    f"Missing critical fields during parsing: {', '.join(missing_fields)}. "
                    "These fields may be missing from the PDF or in an unexpected format. "
                    "Please verify the PDF content."
                )

            # Build parsed document
            parsed = ParsedDocument(
                form_type=form_type,
                company={
                    "cin": kv_data.get("CIN", ""),
                    "name": kv_data.get("Company Name", ""),
                },
                financial_year={
                    "from": kv_data.get("Financial Year From", ""),
                    "to": kv_data.get("Financial Year To", ""),
                },
                data={
                    "turnover_and_net_worth": {
                        "turnover_inr": kv_data.get("Turnover", 0),
                        "net_worth_inr": kv_data.get("Net Worth", 0),
                    },
                    **table_data,
                },
                metadata={
                    "sections": list(sections.keys()),
                },
            )

            return parsed
        except Exception as e:
            error_type = type(e).__name__
            from mgt7_pdf_to_json.exceptions import ParsingError

            error_msg = (
                f"Failed to parse document: {error_type}: {e}. "
                "Possible reasons: "
                "document structure is unexpected, "
                "required fields are missing or in wrong format, "
                "or document is corrupted. "
                f"Document text length: {len(doc.text)} characters."
            )
            logger.error(error_msg, exc_info=True)
            raise ParsingError(error_msg) from e
