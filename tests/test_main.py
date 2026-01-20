"""Tests for __main__ module."""

from unittest.mock import patch


def test_main_module_entry_point():
    """Test __main__ module entry point."""
    # Test that __main__ can be imported and executed

    with patch("sys.argv", ["mgt7pdf2json", "--help"]):
        with patch("sys.exit"):
            # Import and execute __main__
            import mgt7_pdf_to_json.__main__  # noqa: F401

            # The module should call main() when executed
            # We can't easily test the actual execution, but we can verify it's importable
            assert hasattr(mgt7_pdf_to_json.__main__, "main")
