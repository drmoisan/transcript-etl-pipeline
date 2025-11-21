"""Extract transcript text from files.

This module handles reading transcript text from files with automatic encoding detection.
Supports .txt and .md files in UTF-8 or UTF-16 encoding.
"""

from __future__ import annotations

from pathlib import Path


def detect_encoding(file_path: Path) -> str:
    """Detect file encoding by checking for BOM markers.

    Args:
        file_path: Path to the file to check

    Returns:
        Encoding name that handles BOM appropriately
    """
    with open(file_path, "rb") as f:
        raw = f.read(4)

    # Check for UTF-16 BOM - use utf-16 which handles BOM automatically
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return "utf-16"
    # Check for UTF-8 BOM
    if raw.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"

    # Default to UTF-8
    return "utf-8"


def extract_from_file(file_path: str) -> str:
    """Extract text content from a file.

    Args:
        file_path: Path to the text file (.txt or .md)

    Returns:
        The text content of the file

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file type is not supported
        OSError: If there's an error reading the file
    """
    path = Path(file_path)

    # Validate file exists
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Validate file is a file, not directory
    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    # Validate supported file extension
    ext = path.suffix.lower()
    if ext not in [".txt", ".md"]:
        raise ValueError(f"Unsupported file type: {ext}. Only .txt and .md are supported.")

    # Detect encoding and read file
    try:
        encoding = detect_encoding(path)
        with open(path, encoding=encoding) as f:
            content = f.read()
        return content
    except UnicodeDecodeError as e:
        raise OSError(f"Failed to decode file {file_path}: {e}") from e
    except Exception as e:
        raise OSError(f"Error reading file {file_path}: {e}") from e
