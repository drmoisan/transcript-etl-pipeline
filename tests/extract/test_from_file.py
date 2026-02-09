"""Tests for file extraction."""

import io
from pathlib import Path

import pytest

from transcript_etl_pipeline.extract.from_file import detect_encoding, extract_from_file


class TestDetectEncoding:
    """Tests for encoding detection."""

    def test_detect_utf8_no_bom(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test detecting UTF-8 without BOM."""
        file_content = b"Hello world"
        mock_file = io.BytesIO(file_content)

        def mock_open_func(path: Path, mode: str) -> io.BytesIO:
            return mock_file

        monkeypatch.setattr("builtins.open", mock_open_func)

        encoding = detect_encoding(Path("test.txt"))
        assert encoding == "utf-8"

    def test_detect_utf8_with_bom(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test detecting UTF-8 with BOM."""
        # UTF-8 BOM (EF BB BF) + content
        file_content = b"\xef\xbb\xbfHello world"
        mock_file = io.BytesIO(file_content)

        def mock_open_func(path: Path, mode: str) -> io.BytesIO:
            return mock_file

        monkeypatch.setattr("builtins.open", mock_open_func)

        encoding = detect_encoding(Path("test.txt"))
        assert encoding == "utf-8-sig"

    def test_detect_utf16_le_with_bom(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test detecting UTF-16 LE with BOM."""
        # UTF-16 LE BOM (FF FE) + "Hi" in UTF-16 LE
        file_content = b"\xff\xfeH\x00i\x00"
        mock_file = io.BytesIO(file_content)

        def mock_open_func(path: Path, mode: str) -> io.BytesIO:
            return mock_file

        monkeypatch.setattr("builtins.open", mock_open_func)

        encoding = detect_encoding(Path("test.txt"))
        assert encoding == "utf-16"

    def test_detect_utf16_be_with_bom(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test detecting UTF-16 BE with BOM."""
        # UTF-16 BE BOM (FE FF) + "Hi" in UTF-16 BE
        file_content = b"\xfe\xff\x00H\x00i"
        mock_file = io.BytesIO(file_content)

        def mock_open_func(path: Path, mode: str) -> io.BytesIO:
            return mock_file

        monkeypatch.setattr("builtins.open", mock_open_func)

        encoding = detect_encoding(Path("test.txt"))
        assert encoding == "utf-16"

    def test_detect_encoding_short_file(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test detecting encoding on file with less than 4 bytes."""
        file_content = b"Hi"
        mock_file = io.BytesIO(file_content)

        def mock_open_func(path: Path, mode: str) -> io.BytesIO:
            return mock_file

        monkeypatch.setattr("builtins.open", mock_open_func)

        encoding = detect_encoding(Path("test.txt"))
        assert encoding == "utf-8"

    def test_detect_encoding_empty_file(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test detecting encoding on empty file."""
        file_content = b""
        mock_file = io.BytesIO(file_content)

        def mock_open_func(path: Path, mode: str) -> io.BytesIO:
            return mock_file

        monkeypatch.setattr("builtins.open", mock_open_func)

        encoding = detect_encoding(Path("test.txt"))
        assert encoding == "utf-8"


class TestExtractFromFile:
    """Tests for file extraction."""

    @staticmethod
    def _mock_path_exists(_self: Path) -> bool:
        """Helper to mock Path.exists as True."""
        return True

    @staticmethod
    def _mock_path_is_file(_self: Path) -> bool:
        """Helper to mock Path.is_file as True."""
        return True

    @staticmethod
    def _mock_path_is_not_file(_self: Path) -> bool:
        """Helper to mock Path.is_file as False."""
        return False

    def test_extract_txt_file_utf8(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test extracting content from UTF-8 text file."""
        content = "This is a test transcript.\nWith multiple lines."
        file_bytes = content.encode("utf-8")

        # Mock Path methods
        def mock_exists(_self: Path) -> bool:
            return True

        def mock_is_file(_self: Path) -> bool:
            return True

        monkeypatch.setattr(Path, "exists", mock_exists)
        monkeypatch.setattr(Path, "is_file", mock_is_file)
        monkeypatch.setattr(Path, "suffix", ".txt")

        # Mock file operations
        mock_binary = io.BytesIO(file_bytes)
        mock_text = io.StringIO(content)

        call_count = {"count": 0}

        def mock_open_func(path: Path, mode: str = "r", encoding: str | None = None) -> io.IOBase:
            call_count["count"] += 1
            if mode == "rb":
                return mock_binary
            return mock_text

        monkeypatch.setattr("builtins.open", mock_open_func)

        extracted = extract_from_file("test.txt")
        assert extracted == content

    def test_extract_md_file(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test extracting content from markdown file."""
        content = "# Meeting Notes\n\nThis is the transcript."
        file_bytes = content.encode("utf-8")

        # Mock Path methods
        monkeypatch.setattr(Path, "exists", self._mock_path_exists)
        monkeypatch.setattr(Path, "is_file", self._mock_path_is_file)
        monkeypatch.setattr(Path, "suffix", ".md")

        # Mock file operations
        mock_binary = io.BytesIO(file_bytes)
        mock_text = io.StringIO(content)

        def mock_open_func(path: Path, mode: str = "r", encoding: str | None = None) -> io.IOBase:
            if mode == "rb":
                return mock_binary
            return mock_text

        monkeypatch.setattr("builtins.open", mock_open_func)

        extracted = extract_from_file("test.md")
        assert extracted == content

    def test_extract_utf16_file(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test extracting content from UTF-16 encoded file."""
        content = "Transcript with UTF-16 encoding"
        # UTF-16 LE BOM + content
        file_bytes = b"\xff\xfe" + content.encode("utf-16-le")

        # Mock Path methods
        monkeypatch.setattr(Path, "exists", self._mock_path_exists)
        monkeypatch.setattr(Path, "is_file", self._mock_path_is_file)
        monkeypatch.setattr(Path, "suffix", ".txt")

        # Mock file operations
        mock_binary = io.BytesIO(file_bytes)
        mock_text = io.StringIO(content)

        def mock_open_func(path: Path, mode: str = "r", encoding: str | None = None) -> io.IOBase:
            if mode == "rb":
                return mock_binary
            return mock_text

        monkeypatch.setattr("builtins.open", mock_open_func)

        extracted = extract_from_file("test.txt")
        assert extracted == content

    def test_extract_utf8_with_bom(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test extracting content from UTF-8 file with BOM."""
        content = "Content with BOM"
        # UTF-8 BOM + content
        file_bytes = b"\xef\xbb\xbf" + content.encode("utf-8")

        # Mock Path methods
        monkeypatch.setattr(Path, "exists", self._mock_path_exists)
        monkeypatch.setattr(Path, "is_file", self._mock_path_is_file)
        monkeypatch.setattr(Path, "suffix", ".txt")

        # Mock file operations
        mock_binary = io.BytesIO(file_bytes)
        mock_text = io.StringIO(content)

        def mock_open_func(path: Path, mode: str = "r", encoding: str | None = None) -> io.IOBase:
            if mode == "rb":
                return mock_binary
            return mock_text

        monkeypatch.setattr("builtins.open", mock_open_func)

        extracted = extract_from_file("test.txt")
        assert extracted == content

    def test_file_not_found(self) -> None:
        """Test that FileNotFoundError is raised for non-existent file."""
        with pytest.raises(FileNotFoundError, match="File not found"):
            extract_from_file("/nonexistent/file.txt")

    def test_unsupported_file_type(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that ValueError is raised for unsupported file types."""
        # Mock Path to make file exist
        monkeypatch.setattr(Path, "exists", self._mock_path_exists)
        monkeypatch.setattr(Path, "is_file", self._mock_path_is_file)
        monkeypatch.setattr(Path, "suffix", ".pdf")

        with pytest.raises(ValueError, match="Unsupported file type"):
            extract_from_file("test.pdf")

    def test_directory_path_raises_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that passing a directory path raises ValueError."""
        # Mock Path to make directory exist but not be a file
        monkeypatch.setattr(Path, "exists", self._mock_path_exists)
        monkeypatch.setattr(Path, "is_file", self._mock_path_is_not_file)

        with pytest.raises(ValueError, match="not a file"):
            extract_from_file("/some/directory")

    def test_empty_file(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test extracting from an empty file returns empty string."""
        content = ""
        file_bytes = b""

        # Mock Path methods
        monkeypatch.setattr(Path, "exists", self._mock_path_exists)
        monkeypatch.setattr(Path, "is_file", self._mock_path_is_file)
        monkeypatch.setattr(Path, "suffix", ".txt")

        # Mock file operations
        mock_binary = io.BytesIO(file_bytes)
        mock_text = io.StringIO(content)

        def mock_open_func(path: Path, mode: str = "r", encoding: str | None = None) -> io.IOBase:
            if mode == "rb":
                return mock_binary
            return mock_text

        monkeypatch.setattr("builtins.open", mock_open_func)

        extracted = extract_from_file("test.txt")
        assert extracted == ""

    def test_unicode_decode_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that UnicodeDecodeError is wrapped in OSError."""
        # Mock Path methods
        monkeypatch.setattr(Path, "exists", self._mock_path_exists)
        monkeypatch.setattr(Path, "is_file", self._mock_path_is_file)
        monkeypatch.setattr(Path, "suffix", ".txt")

        # Mock encoding detection to return utf-8
        file_bytes = b"\x00\x00\x00\x00"
        mock_binary = io.BytesIO(file_bytes)

        def mock_open_func(path: Path, mode: str = "r", encoding: str | None = None) -> io.IOBase:
            if mode == "rb":
                return mock_binary
            # Simulate UnicodeDecodeError on text read
            raise UnicodeDecodeError("utf-8", b"\xff\xfe", 0, 1, "invalid start byte")

        monkeypatch.setattr("builtins.open", mock_open_func)

        with pytest.raises(OSError, match="Failed to decode file"):
            extract_from_file("test.txt")

    def test_generic_exception_during_read(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that generic exceptions during read are wrapped in OSError."""
        # Mock Path methods
        monkeypatch.setattr(Path, "exists", self._mock_path_exists)
        monkeypatch.setattr(Path, "is_file", self._mock_path_is_file)
        monkeypatch.setattr(Path, "suffix", ".txt")

        # Mock encoding detection
        file_bytes = b"content"
        mock_binary = io.BytesIO(file_bytes)

        def mock_open_func(path: Path, mode: str = "r", encoding: str | None = None) -> io.IOBase:
            if mode == "rb":
                return mock_binary
            # Simulate generic exception
            raise PermissionError("Permission denied")

        monkeypatch.setattr("builtins.open", mock_open_func)

        with pytest.raises(OSError, match="Error reading file"):
            extract_from_file("test.txt")

    def test_file_with_special_characters(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test extracting file with Unicode special characters and emojis."""
        content = "Hello 世界 🌍 café"
        file_bytes = content.encode("utf-8")

        # Mock Path methods
        monkeypatch.setattr(Path, "exists", self._mock_path_exists)
        monkeypatch.setattr(Path, "is_file", self._mock_path_is_file)
        monkeypatch.setattr(Path, "suffix", ".txt")

        # Mock file operations
        mock_binary = io.BytesIO(file_bytes)
        mock_text = io.StringIO(content)

        def mock_open_func(path: Path, mode: str = "r", encoding: str | None = None) -> io.IOBase:
            if mode == "rb":
                return mock_binary
            return mock_text

        monkeypatch.setattr("builtins.open", mock_open_func)

        extracted = extract_from_file("test.txt")
        assert extracted == content

    def test_file_with_mixed_line_endings(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test extracting file with mixed line endings (CRLF and LF)."""
        content = "Line 1\r\nLine 2\nLine 3\r\nLine 4"
        file_bytes = content.encode("utf-8")

        # Mock Path methods
        monkeypatch.setattr(Path, "exists", self._mock_path_exists)
        monkeypatch.setattr(Path, "is_file", self._mock_path_is_file)
        monkeypatch.setattr(Path, "suffix", ".txt")

        # Mock file operations
        mock_binary = io.BytesIO(file_bytes)
        mock_text = io.StringIO(content)

        def mock_open_func(path: Path, mode: str = "r", encoding: str | None = None) -> io.IOBase:
            if mode == "rb":
                return mock_binary
            return mock_text

        monkeypatch.setattr("builtins.open", mock_open_func)

        extracted = extract_from_file("test.txt")
        assert extracted == content

    def test_case_insensitive_extension(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that file extensions are case-insensitive."""
        content = "Content"
        file_bytes = content.encode("utf-8")

        # Mock Path methods
        monkeypatch.setattr(Path, "exists", self._mock_path_exists)
        monkeypatch.setattr(Path, "is_file", self._mock_path_is_file)
        monkeypatch.setattr(Path, "suffix", ".TXT")

        # Mock file operations
        mock_binary = io.BytesIO(file_bytes)
        mock_text = io.StringIO(content)

        def mock_open_func(path: Path, mode: str = "r", encoding: str | None = None) -> io.IOBase:
            if mode == "rb":
                return mock_binary
            return mock_text

        monkeypatch.setattr("builtins.open", mock_open_func)

        extracted = extract_from_file("test.TXT")
        assert extracted == content
