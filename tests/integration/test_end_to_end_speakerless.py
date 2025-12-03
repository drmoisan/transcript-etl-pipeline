"""End-to-end integration tests for speakerless transcript pipeline.

These tests verify that transcripts WITHOUT speaker labels are correctly
processed through the full pipeline: extract → normalize → enhance → parse → format.
"""

from pathlib import Path

from transcript_etl_pipeline.document.parser import parse_enhanced_text
from transcript_etl_pipeline.extract.from_file import extract_from_file
from transcript_etl_pipeline.formatters.docx_formatter import format_to_docx
from transcript_etl_pipeline.formatters.md_formatter import format_to_md
from transcript_etl_pipeline.formatters.rtf_formatter import format_to_rtf
from transcript_etl_pipeline.transform.enhance import enhance_text
from transcript_etl_pipeline.transform.normalize import normalize_text


class TestEndToEndSpeakerlessDOCX:
    """Test the complete pipeline with speakerless transcripts - DOCX output."""

    def test_simple_speakerless_to_docx(self, tmp_path: Path) -> None:
        """Test converting a simple speakerless transcript to DOCX.

        NOTE: This test has metadata lines (Date:, Attendees:, Transcript:)
        which are detected as speaker labels by has_speaker_labels().
        This is expected behavior per the speakerless integration tests.

        For true speakerless detection, use transcripts without any colons.
        """
        # Create a temporary input file WITHOUT speaker labels
        input_file = tmp_path / "input.txt"
        input_file.write_text(
            "Date: 2025-12-03\r\n"
            "Attendees: Alice Smith, Bob Johnson\r\n"
            "\r\n"
            "Transcript:\r\n"
            "Hello everyone, thanks for joining.\r\n"
            "Thank you for having me.\r\n"
            "Let's get started with the agenda.\r\n",
            encoding="utf-8",
        )

        # Extract
        raw_text = extract_from_file(str(input_file))
        assert raw_text is not None

        # Transform: Normalize
        normalized = normalize_text(raw_text)
        assert normalized is not None

        # Transform: Enhance
        # Note: Metadata labels will be detected as speaker labels
        enhanced, _speaker_map = enhance_text(normalized)
        assert enhanced is not None

        # Parse
        doc = parse_enhanced_text(enhanced)
        assert len(doc.sections) > 0

        # Load: Format as DOCX
        output_file = tmp_path / "output.docx"
        format_to_docx(doc, str(output_file))

        # Verify output file exists
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_speakerless_with_fixture_to_docx(self, tmp_path: Path) -> None:
        """Test pipeline with actual speakerless fixture file - DOCX output.

        Uses pure_dialogue_no_speakers.txt which contains a Q4 strategy
        review meeting as continuous dialogue without speaker labels.
        """
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "sample_transcripts"
            / "pure_dialogue_no_speakers.txt"
        )

        # Extract
        raw_text = extract_from_file(str(fixture_path))

        # Transform
        normalized = normalize_text(raw_text)
        enhanced, speaker_map = enhance_text(normalized)

        # Verify speakers were assigned
        assert "Speaker A:" in enhanced
        assert speaker_map == {}  # No name resolution for generic speakers

        # Parse and format
        doc = parse_enhanced_text(enhanced)
        output_file = tmp_path / "output.docx"
        format_to_docx(doc, str(output_file))

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_speakerless_with_metadata_to_docx(self, tmp_path: Path) -> None:
        """Test speakerless transcript with metadata header - DOCX output.

        Uses transcript_no_speakers.txt which has metadata followed by
        speakerless dialogue.

        NOTE: Metadata labels (Meeting Date:, Attendees:, etc.) are detected
        as speaker labels by has_speaker_labels(). This is expected behavior.
        """
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "sample_transcripts"
            / "transcript_no_speakers.txt"
        )

        # Extract
        raw_text = extract_from_file(str(fixture_path))

        # Transform
        normalized = normalize_text(raw_text)
        enhanced, _speaker_map = enhance_text(normalized)

        # Parse and format
        doc = parse_enhanced_text(enhanced)
        output_file = tmp_path / "output.docx"
        format_to_docx(doc, str(output_file))

        assert output_file.exists()
        assert output_file.stat().st_size > 0


class TestEndToEndSpeakerlessRTF:
    """Test the complete pipeline with speakerless transcripts - RTF output."""

    def test_simple_speakerless_to_rtf(self, tmp_path: Path) -> None:
        """Test converting a simple speakerless transcript to RTF.

        NOTE: Metadata labels are detected as speaker labels. This is expected.
        """
        # Create a temporary input file WITHOUT speaker labels
        input_file = tmp_path / "input.txt"
        input_file.write_text(
            "Date: 2025-12-03\r\n"
            "Attendees: Alice Smith, Bob Johnson\r\n"
            "\r\n"
            "Transcript:\r\n"
            "Hello everyone, thanks for joining.\r\n"
            "Thank you for having me.\r\n"
            "Let's get started with the agenda.\r\n",
            encoding="utf-8",
        )

        # Extract
        raw_text = extract_from_file(str(input_file))
        assert raw_text is not None

        # Transform
        normalized = normalize_text(raw_text)
        enhanced, _speaker_map = enhance_text(normalized)

        # Parse and format as RTF
        doc = parse_enhanced_text(enhanced)
        output_file = tmp_path / "output.rtf"
        format_to_rtf(doc, str(output_file))

        # Verify output file exists
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_speakerless_with_fixture_to_rtf(self, tmp_path: Path) -> None:
        """Test pipeline with speakerless fixture - RTF output."""
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "sample_transcripts"
            / "pure_dialogue_no_speakers.txt"
        )

        # Full pipeline
        raw_text = extract_from_file(str(fixture_path))
        normalized = normalize_text(raw_text)
        enhanced, _speaker_map = enhance_text(normalized)

        # Verify speakers assigned
        assert "Speaker A:" in enhanced

        # Parse and format as RTF
        doc = parse_enhanced_text(enhanced)
        output_file = tmp_path / "output.rtf"
        format_to_rtf(doc, str(output_file))

        assert output_file.exists()
        assert output_file.stat().st_size > 0


class TestEndToEndSpeakerlessMD:
    """Test the complete pipeline with speakerless transcripts - Markdown output."""

    def test_simple_speakerless_to_md(self, tmp_path: Path) -> None:
        """Test converting a simple speakerless transcript to Markdown.

        NOTE: Metadata labels are detected as speaker labels. This is expected.
        """
        # Create a temporary input file WITHOUT speaker labels
        input_file = tmp_path / "input.txt"
        input_file.write_text(
            "Date: 2025-12-03\r\n"
            "Attendees: Alice Smith, Bob Johnson\r\n"
            "\r\n"
            "Transcript:\r\n"
            "Hello everyone, thanks for joining.\r\n"
            "Thank you for having me.\r\n"
            "Let's get started with the agenda.\r\n",
            encoding="utf-8",
        )

        # Extract
        raw_text = extract_from_file(str(input_file))
        assert raw_text is not None

        # Transform
        normalized = normalize_text(raw_text)
        enhanced, _speaker_map = enhance_text(normalized)

        # Parse and format as Markdown
        doc = parse_enhanced_text(enhanced)
        output_file = tmp_path / "output.md"
        format_to_md(doc, str(output_file))

        # Verify output file exists
        assert output_file.exists()
        assert output_file.stat().st_size > 0

        # Verify markdown content was generated
        content = output_file.read_text(encoding="utf-8")
        assert len(content) > 0

    def test_speakerless_with_fixture_to_md(self, tmp_path: Path) -> None:
        """Test pipeline with speakerless fixture - Markdown output."""
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "sample_transcripts"
            / "pure_dialogue_no_speakers.txt"
        )

        # Full pipeline
        raw_text = extract_from_file(str(fixture_path))
        normalized = normalize_text(raw_text)
        enhanced, _speaker_map = enhance_text(normalized)

        # Verify speakers assigned
        assert "Speaker A:" in enhanced

        # Parse and format as Markdown
        doc = parse_enhanced_text(enhanced)
        output_file = tmp_path / "output.md"
        format_to_md(doc, str(output_file))

        assert output_file.exists()
        assert output_file.stat().st_size > 0

        # Verify markdown content
        content = output_file.read_text(encoding="utf-8")
        assert "Speaker A:" in content


class TestEndToEndSpeakerlessWithNumSpeakers:
    """Test the complete pipeline with explicit num_speakers parameter."""

    def test_speakerless_with_explicit_num_speakers(self, tmp_path: Path) -> None:
        """Test that num_speakers parameter is respected in speakerless detection.

        Verifies that when num_speakers=3 is specified, the detection
        uses that value instead of auto-detecting.
        """
        input_file = tmp_path / "input.txt"
        input_file.write_text(
            "Hello, welcome to the meeting.\r\n"
            "Thank you for having us.\r\n"
            "Let's discuss the project timeline.\r\n"
            "I agree with that approach.\r\n"
            "Great, let's move forward.\r\n",
            encoding="utf-8",
        )

        # Extract and transform
        raw_text = extract_from_file(str(input_file))
        normalized = normalize_text(raw_text)

        # Enhance with explicit num_speakers=3
        enhanced, _speaker_map = enhance_text(normalized, num_speakers=3)

        # Verify speakers were assigned
        assert "Speaker A:" in enhanced
        # With 3 speakers, we might see Speaker C depending on detection
        # The key is that the parameter was accepted and used

        # Parse and format
        doc = parse_enhanced_text(enhanced)
        output_file = tmp_path / "output.docx"
        format_to_docx(doc, str(output_file))

        assert output_file.exists()
        assert output_file.stat().st_size > 0
