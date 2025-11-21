"""Tests for file extraction."""

import tempfile
from pathlib import Path

import pytest

from transcript_etl_pipeline.extract.from_file import detect_encoding, extract_from_file


class TestDetectEncoding:
    """Tests for encoding detection."""

    def test_detect_utf8_no_bom(self) -> None:
        """Test detecting UTF-8 without BOM."""
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as f:
            f.write("Hello world")
            temp_path = f.name

        try:
            encoding = detect_encoding(Path(temp_path))
            assert encoding == "utf-8"
        finally:
            Path(temp_path).unlink()

    def test_detect_utf8_with_bom(self) -> None:
        """Test detecting UTF-8 with BOM."""
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8-sig", delete=False) as f:
            f.write("Hello world")
            temp_path = f.name

        try:
            encoding = detect_encoding(Path(temp_path))
            assert encoding == "utf-8-sig"
        finally:
            Path(temp_path).unlink()

    def test_detect_utf16_le(self) -> None:
        """Test detecting UTF-16 with BOM."""
        # Python's utf-16 adds BOM automatically
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-16", delete=False) as f:
            f.write("Hello world")
            temp_path = f.name

        try:
            encoding = detect_encoding(Path(temp_path))
            # Should detect utf-16 (which handles BOM automatically)
            assert encoding == "utf-16"
        finally:
            Path(temp_path).unlink()

    def test_detect_utf16_be(self) -> None:
        """Test detecting UTF-16 Big Endian with BOM by writing raw bytes."""
        # Write a file with explicit UTF-16 BE BOM
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
            # UTF-16 BE BOM + "Hi" encoded in UTF-16 BE
            f.write(b"\xfe\xff\x00H\x00i")
            temp_path = f.name

        try:
            encoding = detect_encoding(Path(temp_path))
            assert encoding == "utf-16"
        finally:
            Path(temp_path).unlink()


class TestExtractFromFile:
    """Tests for file extraction."""

    def test_extract_txt_file_utf8(self) -> None:
        """Test extracting content from UTF-8 text file."""
        content = "This is a test transcript.\nWith multiple lines."

        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".txt", delete=False
        ) as f:
            f.write(content)
            temp_path = f.name

        try:
            extracted = extract_from_file(temp_path)
            assert extracted == content
        finally:
            Path(temp_path).unlink()

    def test_extract_md_file(self) -> None:
        """Test extracting content from markdown file."""
        content = "# Meeting Notes\n\nThis is the transcript."

        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".md", delete=False
        ) as f:
            f.write(content)
            temp_path = f.name

        try:
            extracted = extract_from_file(temp_path)
            assert extracted == content
        finally:
            Path(temp_path).unlink()

    def test_extract_utf16_file(self) -> None:
        """Test extracting content from UTF-16 encoded file."""
        content = "Transcript with UTF-16 encoding"

        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-16", suffix=".txt", delete=False
        ) as f:
            f.write(content)
            temp_path = f.name

        try:
            extracted = extract_from_file(temp_path)
            assert extracted == content
        finally:
            Path(temp_path).unlink()

    def test_file_not_found(self) -> None:
        """Test that FileNotFoundError is raised for non-existent file."""
        with pytest.raises(FileNotFoundError, match="File not found"):
            extract_from_file("/nonexistent/file.txt")

    def test_unsupported_file_type(self) -> None:
        """Test that ValueError is raised for unsupported file types."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Unsupported file type"):
                extract_from_file(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_directory_path_raises_error(self) -> None:
        """Test that passing a directory path raises ValueError."""
        with (
            tempfile.TemporaryDirectory() as temp_dir,
            pytest.raises(ValueError, match="not a file"),
        ):
            extract_from_file(temp_dir)

    def test_empty_file(self) -> None:
        """Test extracting from an empty file returns empty string."""
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".txt", delete=False
        ) as f:
            temp_path = f.name

        try:
            extracted = extract_from_file(temp_path)
            assert extracted == ""
        finally:
            Path(temp_path).unlink()
