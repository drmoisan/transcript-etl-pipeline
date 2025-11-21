"""Extract stage - input from file and clipboard."""

from transcript_etl_pipeline.extract.from_clipboard import extract_from_clipboard
from transcript_etl_pipeline.extract.from_file import extract_from_file

__all__ = ["extract_from_file", "extract_from_clipboard"]
