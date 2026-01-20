"""Tests for mappers."""

from uuid import uuid4

import pytest

from mgt7_pdf_to_json.mappers import DbMapper, DefaultMapper, MinimalMapper, get_mapper
from mgt7_pdf_to_json.models import ParsedDocument


class TestMappers:
    """Test output mappers."""

    @pytest.fixture
    def sample_parsed(self):
        """Create sample parsed document."""
        return ParsedDocument(
            form_type="MGT-7",
            company={
                "cin": "U17120DL2013PTC262515",
                "name": "TEST COMPANY",
            },
            financial_year={
                "from": "01/04/2024",
                "to": "31/03/2025",
            },
            data={
                "turnover_and_net_worth": {
                    "turnover_inr": 1000000,
                    "net_worth_inr": 500000,
                },
            },
        )

    def test_default_mapper(self, sample_parsed):
        """Test default mapper."""
        mapper = DefaultMapper()
        request_id = str(uuid4())

        result = mapper.map(sample_parsed, request_id, "test.pdf")

        assert result["meta"]["request_id"] == request_id
        assert result["meta"]["form_type"] == "MGT-7"
        assert result["data"]["company"]["cin"] == "U17120DL2013PTC262515"
        assert "turnover_and_net_worth" in result["data"]

    def test_minimal_mapper(self, sample_parsed):
        """Test minimal mapper."""
        mapper = MinimalMapper()
        request_id = str(uuid4())

        result = mapper.map(sample_parsed, request_id, "test.pdf")

        assert result["meta"]["request_id"] == request_id
        assert result["data"]["company"]["cin"] == "U17120DL2013PTC262515"
        assert "turnover_and_net_worth" in result["data"]

    def test_db_mapper(self, sample_parsed):
        """Test DB mapper."""
        mapper = DbMapper()
        request_id = str(uuid4())

        result = mapper.map(sample_parsed, request_id, "test.pdf")

        assert result["meta"]["request_id"] == request_id
        assert "generated_at" in result["meta"]["source"]
        assert "facts" in result["data"]
        assert "turnover_inr" in result["data"]["facts"]

    def test_get_mapper(self):
        """Test mapper factory."""
        mapper = get_mapper("default")
        assert isinstance(mapper, DefaultMapper)

        mapper = get_mapper("minimal")
        assert isinstance(mapper, MinimalMapper)

        mapper = get_mapper("db")
        assert isinstance(mapper, DbMapper)

        with pytest.raises(ValueError):
            get_mapper("unknown")

    def test_db_mapper_with_tables(self, sample_parsed):
        """Test DB mapper with table data."""
        mapper = DbMapper()
        request_id = str(uuid4())

        # Add table data to parsed document
        sample_parsed.data["directors"] = [
            {"name": "Director 1", "din": "12345678"},
            {"name": "Director 2", "din": "87654321"},
        ]

        result = mapper.map(sample_parsed, request_id, "test.pdf")

        assert "tables" in result["data"]
        assert "directors" in result["data"]["tables"]
        assert len(result["data"]["tables"]["directors"]) == 2
        # Check that request_id was added to each row
        for row in result["data"]["tables"]["directors"]:
            assert row["request_id"] == request_id
            assert "name" in row
            assert "din" in row

    def test_db_mapper_with_non_list_table_data(self, sample_parsed):
        """Test DB mapper when table data is not a list."""
        mapper = DbMapper()
        request_id = str(uuid4())

        # Add non-list data (should be skipped)
        sample_parsed.data["some_dict"] = {"key": "value"}

        result = mapper.map(sample_parsed, request_id, "test.pdf")

        # Non-list data should not appear in tables
        assert "some_dict" not in result["data"]["tables"]
