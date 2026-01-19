"""MGT-7 and MGT-7A PDF to JSON converter."""

__version__ = "0.1.0"

from mgt7_pdf_to_json.config import Config
from mgt7_pdf_to_json.pipeline import Pipeline

__all__ = ["Pipeline", "Config", "__version__"]
