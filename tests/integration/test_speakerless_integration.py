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
        """Verify speaker changes detection for single-line continuous dialogue.

        The pure_dialogue_no_speakers.txt fixture contains a continuous block
        of dialogue on a single line. Since detect_speaker_changes operates
        on a line-by-line basis, it will only detect the start of the first
        (and only) line as a change point.
        """
        fixture_path = FIXTURES_DIR / "pure_dialogue_no_speakers.txt"
        text = fixture_path.read_text()

        # Verify this is indeed a single-line fixture
        lines = [line for line in text.split("\n") if line.strip()]
        assert len(lines) == 1, f"Expected single-line fixture, got {len(lines)} lines"

        changes = detect_speaker_changes(text)

        # For a single-line text, expect exactly one change point at index 0
        expected_changes = [0]
        assert (
            changes == expected_changes
        ), f"Expected exactly {expected_changes} for single-line input, got {changes}"

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
        """Test simple question-answer dialogue produces expected speaker changes.

        Input (4 lines):
        0: What time is the meeting?  (question)
        1: It starts at 3 PM.         (no change triggers)
        2: Where is it being held?    (no change triggers)
        3: Conference room B.         (no change triggers)

        Expected changes at: [0, 3] - start, then after two non-triggering lines
        """
        text = (
            "What time is the meeting?\n"
            "It starts at 3 PM.\n"
            "Where is it being held?\n"
            "Conference room B."
        )

        changes = detect_speaker_changes(text)

        # Verify exact expected speaker change points
        expected_changes = [0, 3]
        assert (
            changes == expected_changes
        ), f"Expected speaker changes at {expected_changes}, got {changes}"

        # Also verify labeling produces valid output
        result = assign_speaker_labels(text)
        lines = [line for line in result.split("\r\n") if line.strip()]
        assert len(lines) == 4, f"Expected 4 lines, got {len(lines)}"
        assert all("Speaker" in line for line in lines)

    def test_acknowledgment_pattern(self) -> None:
        """Test that acknowledgments trigger speaker changes at exact positions.

        Input (4 lines):
        0: Can you confirm the project status?  (question)
        1: Yes, everything is on track.         (acknowledgment triggers change)
        2: What about the budget?               (no trigger)
        3: No issues there either.              (acknowledgment triggers change)

        Expected changes at: [0, 1, 3]
        """
        text = (
            "Can you confirm the project status?\n"
            "Yes, everything is on track.\n"
            "What about the budget?\n"
            "No issues there either."
        )

        changes = detect_speaker_changes(text)

        # Verify exact expected speaker change points
        expected_changes = [0, 1, 3]
        assert (
            changes == expected_changes
        ), f"Expected speaker changes at {expected_changes}, got {changes}"

        # Verify content preserved in output
        result = assign_speaker_labels(text)
        assert "project status" in result
        assert "on track" in result
        assert "budget" in result

    def test_greeting_pattern(self) -> None:
        """Test that greetings are detected as speaker changes at exact positions.

        Input (4 lines):
        0: Let's start the meeting.              (start)
        1: Hello everyone, thanks for joining.   (greeting triggers change)
        2: Hi there, glad to be here.            (greeting triggers change)
        3: Great, let's begin.                   (no trigger)

        Expected changes at: [0, 1, 2]
        """
        text = (
            "Let's start the meeting.\n"
            "Hello everyone, thanks for joining.\n"
            "Hi there, glad to be here.\n"
            "Great, let's begin."
        )

        changes = detect_speaker_changes(text)

        # Verify exact expected speaker change points
        expected_changes = [0, 1, 2]
        assert (
            changes == expected_changes
        ), f"Expected speaker changes at {expected_changes}, got {changes}"

        # Verify greetings preserved in output
        result = assign_speaker_labels(text)
        assert "Hello everyone" in result
        assert "Hi there" in result

    def test_pronoun_shift_detection(self) -> None:
        """Test that pronoun shifts (I/you) are detected at exact positions.

        Input (4 lines):
        0: I think we should proceed with the plan.  (start, first-person)
        1: You make an excellent point.              (I->you shift triggers change)
        2: I agree with your assessment.             (you->I shift triggers change)
        3: You've done great work on this.           (I->you shift triggers change)

        Expected changes at: [0, 1, 2, 3] - every line due to I/you alternation
        """
        text = (
            "I think we should proceed with the plan.\n"
            "You make an excellent point.\n"
            "I agree with your assessment.\n"
            "You've done great work on this."
        )

        changes = detect_speaker_changes(text)

        # Verify exact expected speaker change points
        expected_changes = [0, 1, 2, 3]
        assert (
            changes == expected_changes
        ), f"Expected speaker changes at {expected_changes}, got {changes}"

        # Verify all lines get labeled
        result = assign_speaker_labels(text)
        lines = [line for line in result.split("\r\n") if line.strip()]
        assert len(lines) == 4
        assert all("Speaker" in line for line in lines)

    def test_multi_speaker_meeting(self) -> None:
        """Test multi-speaker meeting scenario with complex dialogue.

        Input (6 lines):
        0: Good morning everyone.                     (start, greeting)
        1: Thanks for organizing this meeting.        (no trigger)
        2: What's the first agenda item?              (question)
        3: Yes, let's discuss the Q3 results.         (acknowledgment triggers change)
        4: I've prepared a summary of the data.       (no trigger)
        5: That's helpful. What are the key takeaways? (no trigger)

        Expected changes at: [0, 3]
        """
        text = (
            "Good morning everyone.\n"
            "Thanks for organizing this meeting.\n"
            "What's the first agenda item?\n"
            "Yes, let's discuss the Q3 results.\n"
            "I've prepared a summary of the data.\n"
            "That's helpful. What are the key takeaways?"
        )

        changes = detect_speaker_changes(text)

        # Verify exact expected speaker change points
        expected_changes = [0, 3]
        assert (
            changes == expected_changes
        ), f"Expected speaker changes at {expected_changes}, got {changes}"

        # Verify all lines get labeled
        result = assign_speaker_labels(text)
        lines = [line for line in result.split("\r\n") if line.strip()]
        assert len(lines) == 6
        assert all("Speaker" in line for line in lines)

        # Content should be preserved
        assert "agenda item" in result
        assert "Q3 results" in result
        assert "summary" in result
