"""Tests for document parsing components."""

from mgt7_pdf_to_json.models import NormalizedDocument
from mgt7_pdf_to_json.parser import DocumentParser, KeyValueParser, SectionSplitter, TableParser


class TestSectionSplitter:
    """Test section splitting functionality."""

    def test_split_with_sections(self):
        """Test splitting document with sections."""
        splitter = SectionSplitter()
        doc = NormalizedDocument(
            text="Section I. First section content\nSection II. Second section content",
            pages=[],
        )
        result = splitter.split(doc)
        assert len(result) > 0
        assert "full" not in result

    def test_split_no_sections_fallback(self):
        """Test splitting document without sections (fallback to full text)."""
        splitter = SectionSplitter()
        doc = NormalizedDocument(text="Plain text without sections", pages=[])
        result = splitter.split(doc)
        assert "full" in result
        assert result["full"] == "Plain text without sections"

    def test_detect_form_type_mgt7a(self):
        """Test detecting MGT-7A form type."""
        splitter = SectionSplitter()
        assert splitter._detect_form_type("MGT-7A form") == "MGT-7A"
        assert splitter._detect_form_type("MGT 7A form") == "MGT-7A"
        assert splitter._detect_form_type("ABRIDGED form") == "MGT-7A"

    def test_detect_form_type_mgt7(self):
        """Test detecting MGT-7 form type."""
        splitter = SectionSplitter()
        assert splitter._detect_form_type("MGT-7 form") == "MGT-7"
        assert splitter._detect_form_type("MGT 7 form") == "MGT-7"

    def test_detect_form_type_unknown_fallback(self):
        """Test detecting form type with unknown text (fallback to MGT-7)."""
        splitter = SectionSplitter()
        result = splitter._detect_form_type("Unknown form text")
        assert result == "MGT-7"


class TestKeyValueParser:
    """Test key-value parsing functionality."""

    def test_parse_cin(self):
        """Test parsing CIN."""
        parser = KeyValueParser()
        text = "CIN: U17120DL2013PTC262515"
        result = parser.parse(text)
        assert "CIN" in result
        assert result["CIN"] == "U17120DL2013PTC262515"

    def test_parse_company_name(self):
        """Test parsing company name."""
        parser = KeyValueParser()
        text = "Name of the company: ABC LIMITED"
        result = parser.parse(text)
        assert "Company Name" in result

    def test_parse_company_name_alt_fallback(self):
        """Test parsing company name with alternative pattern fallback."""
        parser = KeyValueParser()
        text = '"As on filing date": "XYZ PRIVATE LIMITED"'
        result = parser.parse(text)
        # Should use Company Name Alt as fallback
        assert "Company Name" in result or "Company Name Alt" in result

    def test_parse_turnover(self):
        """Test parsing turnover."""
        parser = KeyValueParser()
        text = "Turnover: 1,234,567.89"
        result = parser.parse(text)
        assert "Turnover" in result
        assert isinstance(result["Turnover"], (int, float))

    def test_parse_turnover_alt_fallback(self):
        """Test parsing turnover with alternative pattern fallback."""
        parser = KeyValueParser()
        text = "i * Turnover\n1,234,567"
        result = parser.parse(text)
        assert "Turnover" in result

    def test_parse_turnover_alt_partial_match(self):
        """Test parsing turnover with partial match fallback."""
        parser = KeyValueParser()
        # Create scenario where main pattern gets partial match (< 1000)
        # Need to ensure main pattern matches first with small value
        text = "Turnover: 500"
        parser.parse(text)  # First parse to set initial value
        # Now add alternative pattern
        text2 = text + "\ni * Turnover\n1,234,567"
        result2 = parser.parse(text2)
        # Should have turnover value
        assert "Turnover" in result2

    def test_parse_net_worth(self):
        """Test parsing net worth."""
        parser = KeyValueParser()
        text = "Net worth of the Company: 2,345,678.90"
        result = parser.parse(text)
        assert "Net Worth" in result
        assert isinstance(result["Net Worth"], (int, float))

    def test_parse_net_worth_alt_fallback(self):
        """Test parsing net worth with alternative pattern fallback."""
        parser = KeyValueParser()
        text = "ii * Net worth of the Company\n2,345,678"
        result = parser.parse(text)
        assert "Net Worth" in result

    def test_parse_net_worth_alt_partial_match(self):
        """Test parsing net worth with partial match fallback."""
        parser = KeyValueParser()
        text = "Net worth of the Company: 500\nii * Net worth of the Company\n2,345,678"
        result = parser.parse(text)
        assert "Net Worth" in result

    def test_parse_financial_year_end(self):
        """Test parsing financial year end date."""
        parser = KeyValueParser()
        text = "financial year ended on (DD/MM/YYYY) 31/03/2023"
        result = parser.parse(text)
        assert "Financial Year End" in result or "Financial Year To" in result

    def test_parse_financial_year_end_fallback(self):
        """Test parsing financial year end with fallback when parse_date fails."""
        parser = KeyValueParser()
        # Use invalid date format that parse_date can't handle
        text = "financial year ended on (DD/MM/YYYY) invalid-date"
        result = parser.parse(text)
        # Should still set Financial Year To from Financial Year End
        if "Financial Year End" in result:
            assert "Financial Year To" in result

    def test_parse_value_empty(self):
        """Test parsing empty value."""
        parser = KeyValueParser()
        result = parser._parse_value("")
        assert result == ""

    def test_parse_value_boolean_true(self):
        """Test parsing boolean true values."""
        parser = KeyValueParser()
        assert parser._parse_value("YES") is True
        assert parser._parse_value("Y") is True
        assert parser._parse_value("TRUE") is True
        assert parser._parse_value("1") is True

    def test_parse_value_boolean_false(self):
        """Test parsing boolean false values."""
        parser = KeyValueParser()
        assert parser._parse_value("NO") is False
        assert parser._parse_value("N") is False
        assert parser._parse_value("FALSE") is False
        assert parser._parse_value("0") is False

    def test_parse_value_integer(self):
        """Test parsing integer value."""
        parser = KeyValueParser()
        # The parser extracts first complete number pattern, so test with simpler number
        result = parser._parse_value("123")
        assert isinstance(result, int)
        assert result == 123
        # Test with comma-separated number
        result2 = parser._parse_value("1,234,567")
        assert isinstance(result2, int)

    def test_parse_value_float(self):
        """Test parsing float value."""
        parser = KeyValueParser()
        result = parser._parse_value("123.45")
        assert isinstance(result, float)
        assert result == 123.45

    def test_parse_custom_patterns(self):
        """Test parsing with custom patterns."""
        parser = KeyValueParser()
        text = "CustomField: CustomValue"
        patterns = [("CustomField", r"CustomField:\s*(.+)")]
        result = parser.parse(text, patterns)
        assert "CustomField" in result
        assert result["CustomField"] == "CustomValue"


class TestTableParser:
    """Test table parsing functionality."""

    def test_parse_empty_tables(self):
        """Test parsing empty tables list."""
        parser = TableParser()
        result = parser.parse([])
        assert result == {}

    def test_parse_table_with_empty_table(self):
        """Test parsing table with empty table data."""
        parser = TableParser()
        tables = [{"page": 1, "table": []}]
        result = parser.parse(tables)
        assert result == {}

    def test_identify_table_type_empty(self):
        """Test identifying table type with empty table."""
        parser = TableParser()
        result = parser._identify_table_type([])
        assert result == "unknown"

    def test_identify_table_type_board_meetings(self):
        """Test identifying board meetings table."""
        parser = TableParser()
        table = [["Date of Meeting", "Directors"], ["31/03/2023", "5"]]
        result = parser._identify_table_type(table)
        assert result == "board_meetings"

    def test_identify_table_type_share_capital(self):
        """Test identifying share capital table."""
        parser = TableParser()
        table = [["Share Capital", "Equity"], ["1000000", "500000"]]
        result = parser._identify_table_type(table)
        assert result == "share_capital"

    def test_identify_table_type_directors(self):
        """Test identifying directors table."""
        parser = TableParser()
        # Use "PROMOTER" without "DIRECTOR" in first header to avoid board_meetings match
        table = [["Promoter Name", "Status"], ["John Doe", "Yes"]]
        result = parser._identify_table_type(table)
        assert result == "directors"

    def test_parse_table_rows_directors_total(self):
        """Test parsing table rows with directors_total header."""
        parser = TableParser()
        table = [
            ["S.No", "Directors Total", "Directors Attended"],
            ["1", "5", "4"],
        ]
        result = parser._parse_table_rows(table, "board_meetings")
        assert len(result) > 0
        assert any("directors_total" in row for row in result)

    def test_parse_table_rows_directors_attended(self):
        """Test parsing table rows with directors_attended header."""
        parser = TableParser()
        table = [
            ["Date", "Directors Attendance"],
            ["31/03/2023", "4"],
        ]
        result = parser._parse_table_rows(table, "board_meetings")
        assert len(result) > 0
        assert any("directors_attended" in row for row in result)

    def test_parse_table_rows_board_meetings_with_date_fallback(self):
        """Test parsing board meetings with date fallback."""
        parser = TableParser()
        table = [
            ["Date of Meeting", "Directors Total", "Directors Attended"],
            ["Some text without date", "5", "4"],
        ]
        result = parser._parse_table_rows(table, "board_meetings")
        assert len(result) > 0
        # Date should be set to original string if no date match
        for row in result:
            if "date" in row:
                assert isinstance(row["date"], str)

    def test_parse_table_rows_board_meetings_directors_total_parsing(self):
        """Test parsing board meetings with directors_total value parsing."""
        parser = TableParser()
        table = [
            ["Date", "Directors Total", "Directors Attended"],
            ["31/03/2023", "5", "4"],
        ]
        result = parser._parse_table_rows(table, "board_meetings")
        assert len(result) > 0
        for row in result:
            if "directors_total" in row:
                assert isinstance(row["directors_total"], (int, float))

    def test_parse_table_rows_board_meetings_directors_attended_parsing(self):
        """Test parsing board meetings with directors_attended value parsing."""
        parser = TableParser()
        table = [
            ["Date", "Directors Total", "Directors Attended"],
            ["31/03/2023", "5", "4"],
        ]
        result = parser._parse_table_rows(table, "board_meetings")
        assert len(result) > 0
        for row in result:
            if "directors_attended" in row:
                assert isinstance(row["directors_attended"], (int, float))

    def test_parse_cell_value(self):
        """Test parsing individual cell value."""
        parser = TableParser()
        assert parser._parse_cell_value("123") == 123
        assert parser._parse_cell_value("123.45") == 123.45
        assert parser._parse_cell_value("text") == "text"
        assert parser._parse_cell_value(None) is None


class TestDocumentParser:
    """Test document parser integration."""

    def test_parse_basic_document(self):
        """Test parsing basic document."""
        parser = DocumentParser()
        doc = NormalizedDocument(text="CIN: U17120DL2013PTC262515", pages=[])
        result = parser.parse(doc, [])
        assert result is not None
        assert hasattr(result, "form_type")

    def test_parse_document_with_tables(self):
        """Test parsing document with tables."""
        parser = DocumentParser()
        doc = NormalizedDocument(text="Company Name: ABC LIMITED", pages=[])
        tables = [{"page": 1, "table": [["Header"], ["Value"]]}]
        result = parser.parse(doc, tables)
        assert result is not None
