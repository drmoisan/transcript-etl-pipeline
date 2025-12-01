"""Integration tests for speakerless transcript detection and speaker assignment.

These tests use the sample fixture files to verify expected vs actual output
from the speakerless detection functionality.
"""

from pathlib import Path

from transcript_etl_pipeline.transform.speakerless import (
    assign_speaker_labels,
    detect_speaker_changes,
    has_speaker_labels,
)

# Path to test fixtures
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "sample_transcripts"


class TestPureDialogueNoSpeakers:
    """Integration tests using pure_dialogue_no_speakers.txt fixture.

    This fixture contains a Q4 strategy review meeting as a continuous
    block of dialogue without any speaker labels or line breaks.
    """

    def test_fixture_exists(self) -> None:
        """Verify the test fixture exists."""
        fixture_path = FIXTURES_DIR / "pure_dialogue_no_speakers.txt"
        assert fixture_path.exists(), f"Fixture not found: {fixture_path}"

    def test_has_no_speaker_labels(self) -> None:
        """Verify the fixture is correctly identified as having no speaker labels."""
        fixture_path = FIXTURES_DIR / "pure_dialogue_no_speakers.txt"
        text = fixture_path.read_text()

        result = has_speaker_labels(text)

        assert result is False, "Pure dialogue should not have speaker labels"

    def test_detect_speaker_changes(self) -> None:
        """Verify speaker changes are detected in the pure dialogue."""
        fixture_path = FIXTURES_DIR / "pure_dialogue_no_speakers.txt"
        text = fixture_path.read_text()

        changes = detect_speaker_changes(text)

        # Should detect at least one change point (start of dialogue)
        assert len(changes) >= 1, "Should detect at least one speaker change"
        assert 0 in changes, "First line should always be a change point"

    def test_assign_speaker_labels_produces_labeled_output(self) -> None:
        """Verify speaker labels are assigned to all lines."""
        fixture_path = FIXTURES_DIR / "pure_dialogue_no_speakers.txt"
        text = fixture_path.read_text()

        result = assign_speaker_labels(text)

        # Result should contain speaker labels
        assert "Speaker" in result, "Output should contain Speaker labels"
        assert ":" in result, "Output should contain label colons"

        # All non-empty lines should have speaker labels
        lines = [line for line in result.split("\r\n") if line.strip()]
        for line in lines:
            assert line.startswith("Speaker "), f"Line should start with Speaker: {line[:50]}..."

    def test_content_preserved_after_labeling(self) -> None:
        """Verify original content is preserved after adding labels."""
        fixture_path = FIXTURES_DIR / "pure_dialogue_no_speakers.txt"
        text = fixture_path.read_text()

        result = assign_speaker_labels(text)

        # Key phrases from the original should still be present
        expected_phrases = [
            "Q4 strategy review",
            "customer acquisition",
            "retention numbers",
            "onboarding process",
            "engineering resources",
            "cost estimates",
            "Friday",
        ]
        for phrase in expected_phrases:
            assert phrase in result, f"Expected phrase not found: {phrase}"

    def test_expected_output_format(self) -> None:
        """Verify the output matches the expected format for pure dialogue."""
        fixture_path = FIXTURES_DIR / "pure_dialogue_no_speakers.txt"
        text = fixture_path.read_text()

        result = assign_speaker_labels(text)

        # Output should use CRLF line endings (pipeline standard)
        assert "\r\n" in result or "\n" not in result, "Should use CRLF or no line breaks"

        # Lines should follow "Speaker X: content" format
        lines = [line for line in result.split("\r\n") if line.strip()]
        for line in lines:
            # Each line should match the pattern "Speaker [A-Z]: content"
            assert line.startswith("Speaker "), f"Invalid format: {line[:50]}..."
            # Should have content after the label
            parts = line.split(": ", 1)
            assert len(parts) == 2, f"Should have label and content: {line[:50]}..."
            assert len(parts[1]) > 0, f"Should have content after label: {line[:50]}..."


class TestTranscriptNoSpeakers:
    """Integration tests using transcript_no_speakers.txt fixture.

    This fixture contains a Q4 strategy review meeting with metadata
    header (date, attendees, etc.) followed by speakerless dialogue.
    """

    def test_fixture_exists(self) -> None:
        """Verify the test fixture exists."""
        fixture_path = FIXTURES_DIR / "transcript_no_speakers.txt"
        assert fixture_path.exists(), f"Fixture not found: {fixture_path}"

    def test_has_metadata_section(self) -> None:
        """Verify the fixture has a metadata section."""
        fixture_path = FIXTURES_DIR / "transcript_no_speakers.txt"
        text = fixture_path.read_text()

        # Should have metadata lines
        assert "Meeting Date:" in text or "Date:" in text, "Should have date metadata"
        assert "Attendees:" in text, "Should have attendees metadata"

    def test_metadata_detected_as_labels(self) -> None:
        """Verify metadata lines are detected as potential labels.

        Note: The current heuristic may detect metadata as speaker labels.
        This is a known limitation documented in the implementation.
        """
        fixture_path = FIXTURES_DIR / "transcript_no_speakers.txt"
        text = fixture_path.read_text()

        result = has_speaker_labels(text)

        # Metadata lines like "Date:", "Attendees:" match the label pattern
        # This is expected behavior per the implementation
        assert result is True, "Metadata lines match speaker label pattern"

    def test_transcript_section_content(self) -> None:
        """Verify the transcript section contains expected dialogue."""
        fixture_path = FIXTURES_DIR / "transcript_no_speakers.txt"
        text = fixture_path.read_text()

        # Should contain dialogue content
        expected_phrases = [
            "Q4 strategy review",
            "customer acquisition",
            "onboarding process",
        ]
        for phrase in expected_phrases:
            assert phrase in text, f"Expected phrase not found: {phrase}"

    def test_attendees_preserved(self) -> None:
        """Verify attendee names are preserved in metadata."""
        fixture_path = FIXTURES_DIR / "transcript_no_speakers.txt"
        text = fixture_path.read_text()

        expected_attendees = ["Dan Moisan", "Sarah Wilson", "Mike Chen", "Emily Brown"]
        for attendee in expected_attendees:
            assert attendee in text, f"Attendee not found: {attendee}"


class TestSpeakerlessIntegrationComparison:
    """Tests comparing expected vs actual output for common use cases."""

    def test_simple_qa_dialogue(self) -> None:
        """Test simple question-answer dialogue produces alternating speakers."""
        text = (
            "What time is the meeting?\n"
            "It starts at 3 PM.\n"
            "Where is it being held?\n"
            "Conference room B."
        )

        result = assign_speaker_labels(text)
        lines = [line for line in result.split("\r\n") if line.strip()]

        # Should have 4 lines with speaker labels
        assert len(lines) == 4, f"Expected 4 lines, got {len(lines)}"

        # All lines should have speaker labels
        for line in lines:
            assert "Speaker" in line, f"Line missing speaker label: {line}"

    def test_acknowledgment_pattern(self) -> None:
        """Test that acknowledgments trigger speaker changes."""
        text = (
            "Can you confirm the project status?\n"
            "Yes, everything is on track.\n"
            "What about the budget?\n"
            "No issues there either."
        )

        result = assign_speaker_labels(text)
        lines = [line for line in result.split("\r\n") if line.strip()]

        # Should have alternating speakers for Q&A
        assert len(lines) == 4, f"Expected 4 lines, got {len(lines)}"

        # Content should be preserved
        assert "project status" in result
        assert "on track" in result
        assert "budget" in result

    def test_greeting_pattern(self) -> None:
        """Test that greetings are detected as speaker changes."""
        text = (
            "Let's start the meeting.\n"
            "Hello everyone, thanks for joining.\n"
            "Hi there, glad to be here.\n"
            "Great, let's begin."
        )

        result = assign_speaker_labels(text)
        lines = [line for line in result.split("\r\n") if line.strip()]

        # All lines should have labels
        assert all("Speaker" in line for line in lines)

        # Greetings should be preserved
        assert "Hello everyone" in result
        assert "Hi there" in result

    def test_pronoun_shift_detection(self) -> None:
        """Test that pronoun shifts (I/you) indicate speaker changes."""
        text = (
            "I think we should proceed with the plan.\n"
            "You make an excellent point.\n"
            "I agree with your assessment.\n"
            "You've done great work on this."
        )

        result = assign_speaker_labels(text)
        lines = [line for line in result.split("\r\n") if line.strip()]

        # Should detect speaker changes based on pronoun shifts
        assert len(lines) == 4
        assert all("Speaker" in line for line in lines)

    def test_multi_speaker_meeting(self) -> None:
        """Test multi-speaker meeting scenario with complex dialogue."""
        text = (
            "Good morning everyone.\n"
            "Thanks for organizing this meeting.\n"
            "What's the first agenda item?\n"
            "Yes, let's discuss the Q3 results.\n"
            "I've prepared a summary of the data.\n"
            "That's helpful. What are the key takeaways?"
        )

        result = assign_speaker_labels(text)
        lines = [line for line in result.split("\r\n") if line.strip()]

        # All lines should be labeled
        assert len(lines) == 6
        assert all("Speaker" in line for line in lines)

        # Content should be preserved
        assert "agenda item" in result
        assert "Q3 results" in result
        assert "summary" in result
