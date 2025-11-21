"""End-to-end integration tests for DOCX output."""

import tempfile
from pathlib import Path

import pytest

from transcript_etl_pipeline.document.parser import parse_enhanced_text
from transcript_etl_pipeline.extract.from_file import extract_from_file
from transcript_etl_pipeline.formatters.docx_formatter import format_to_docx
from transcript_etl_pipeline.transform.enhance import enhance_text
from transcript_etl_pipeline.transform.normalize import normalize_text


class TestEndToEndDocx:
    """Test the complete pipeline with DOCX output."""

    def test_simple_transcript_to_docx(self, tmp_path: Path) -> None:
        """Test converting a simple transcript to DOCX."""
        # Create a temporary input file
        input_file = tmp_path / "input.txt"
        input_file.write_text(
            "Date: 2025-11-21\n"
            "Attendees: Alice Smith, Bob Johnson\n"
            "\n"
            "Transcript:\n"
            "Alice: Hello everyone.\n"
            "Bob: Thanks for the meeting.\n"
        )

        # Extract
        raw_text = extract_from_file(str(input_file))
        assert raw_text is not None

        # Transform: Normalize
        normalized = normalize_text(raw_text)
        assert normalized is not None

        # Transform: Enhance (no UI callback for test)
        enhanced, speaker_map = enhance_text(normalized)
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

    def test_complex_transcript_to_docx(self, tmp_path: Path) -> None:
        """Test converting a more complex transcript to DOCX."""
        # Create a temporary input file with more complex content
        input_file = tmp_path / "complex_input.txt"
        input_file.write_text(
            "Date: 2025-11-20\n"
            "Time: 2:00 PM - 3:30 PM\n"
            "Attendees: Alice Smith, Bob Johnson, Carol White\n"
            "Location: Conference Room B\n"
            "\n"
            "Transcript:\n"
            "Alice: Welcome everyone to our Q4 review. Let's start with the numbers.\n"
            "\n"
            "Bob: Thank you Alice. Our revenue is up 15% compared to Q3. "
            "This is primarily driven by new customer acquisition.\n"
            "\n"
            "Carol: That's great news. What about retention rates?\n"
            "\n"
            "Bob: Retention has improved by 8%. We've seen positive results "
            "from the new onboarding program.\n"
            "\n"
            "Alice: Excellent work team. Let's continue this momentum into Q1.\n"
        )

        # Run full pipeline
        raw_text = extract_from_file(str(input_file))
        normalized = normalize_text(raw_text)
        enhanced, speaker_map = enhance_text(normalized)
        doc = parse_enhanced_text(enhanced)

        # Format as DOCX
        output_file = tmp_path / "complex_output.docx"
        format_to_docx(doc, str(output_file))

        # Verify output
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_transcript_from_fixture_to_docx(self) -> None:
        """Test converting sample fixture transcript to DOCX."""
        # Use the fixture file if it exists
        fixture_path = (
            Path(__file__).parent.parent / "fixtures" / "sample_transcripts" / "simple_meeting.txt"
        )

        if not fixture_path.exists():
            pytest.skip("Fixture file not found")

        # Run full pipeline
        raw_text = extract_from_file(str(fixture_path))
        normalized = normalize_text(raw_text)
        enhanced, speaker_map = enhance_text(normalized)
        doc = parse_enhanced_text(enhanced)

        # Format as DOCX
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            output_file = tmp.name

        try:
            format_to_docx(doc, output_file)

            # Verify output
            assert Path(output_file).exists()
            assert Path(output_file).stat().st_size > 0
        finally:
            # Clean up
            Path(output_file).unlink(missing_ok=True)

    def test_empty_transcript_to_docx(self, tmp_path: Path) -> None:
        """Test handling empty transcript."""
        # Create empty input
        input_file = tmp_path / "empty.txt"
        input_file.write_text("")

        # Run pipeline
        raw_text = extract_from_file(str(input_file))
        normalized = normalize_text(raw_text)
        enhanced, speaker_map = enhance_text(normalized)
        doc = parse_enhanced_text(enhanced)

        # Should have no sections
        assert len(doc.sections) == 0

        # Format should still work
        output_file = tmp_path / "empty_output.docx"
        format_to_docx(doc, str(output_file))

        # File should be created even if empty
        assert output_file.exists()
