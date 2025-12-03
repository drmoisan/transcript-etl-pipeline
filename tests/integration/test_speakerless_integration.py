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
        """Verify speaker changes detection for continuous dialogue text.

        The pure_dialogue_no_speakers.txt fixture contains a continuous block
        of dialogue WITHOUT line breaks. The detection now uses NLTK sentence
        tokenization to identify speaker changes based on semantic cues, not
        just newlines.

        Expected speaker changes based on semantic analysis:
        - Sentence 0: Start of dialogue
        - Sentence 2: "Thank you." - gratitude indicates speaker change
        - Sentence 3: "I've analyzed..." - first person after second person
        - Sentence 5: "That's an important observation." - response pattern
        - Sentence 7: "Yes!" - acknowledgment
        - Sentence 11: "What are your thoughts..." - question
        - Sentence 12: "From a technical standpoint..." - answer to question
        - Sentence 15: "Can you provide..." - question
        - Sentence 16: "Absolutely." - acknowledgment
        - Sentence 21: "Just one thing..." - turn-taking
        - Sentence 25: "Thanks everyone..." - gratitude
        - Sentence 27: "Will do." - acknowledgment
        """
        fixture_path = FIXTURES_DIR / "pure_dialogue_no_speakers.txt"
        text = fixture_path.read_text()

        # Verify this is a single-line fixture (no newlines in text)
        lines = [line for line in text.split("\n") if line.strip()]
        assert len(lines) == 1, f"Expected single-line fixture, got {len(lines)} lines"

        changes = detect_speaker_changes(text)

        # With sentence-based detection, we now detect multiple speaker changes
        # based on semantic cues even in continuous text
        assert (
            len(changes) >= 10
        ), f"Expected at least 10 speaker changes in this dialogue, got {len(changes)}"
        assert 0 in changes, "First sentence should always be a change point"

        # Verify some key change points are detected
        # Index 2 should be "Thank you." - a gratitude marker
        assert 2 in changes, "Expected change at 'Thank you.' (sentence 2)"
        # Index 7 should be "Yes!" - an acknowledgment
        assert 7 in changes, "Expected change at 'Yes!' (sentence 7)"

    def test_assign_speaker_labels_produces_labeled_output(self) -> None:
        """Verify speaker labels are assigned to all sentences in continuous text."""
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
        0: What time is the meeting?  (question - Speaker A)
        1: It starts at 3 PM.         (answer - Speaker B, triggered by Q&A)
        2: Where is it being held?    (follow-up question - same speaker B continues)
        3: Conference room B.         (answer - Speaker A, triggered by Q&A)

        Expected changes at: [0, 1, 3] - Q&A pattern with follow-up question
        """
        text = (
            "What time is the meeting?\n"
            "It starts at 3 PM.\n"
            "Where is it being held?\n"
            "Conference room B."
        )

        changes = detect_speaker_changes(text)

        # Verify expected speaker change points for Q&A dialogue
        # Question-answer triggers change, but follow-up question may not
        expected_changes = [0, 1, 3]
        assert (
            changes == expected_changes
        ), f"Expected speaker changes at {expected_changes}, got {changes}"

        # Also verify labeling produces valid output
        result = assign_speaker_labels(text)
        lines = [line for line in result.split("\r\n") if line.strip()]
        # With Q&A pattern, we expect 3 lines
        assert len(lines) == 3, f"Expected 3 lines (Q&A pattern), got {len(lines)}"
        assert all("Speaker" in line for line in lines)
        assert "What time" in lines[0]
        assert "It starts" in lines[1]
        assert "Where is" in lines[1]
        assert "Conference room" in lines[2]

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
        3: Great, let's begin.                   (acknowledgment triggers change)

        Expected changes at: [0, 1, 2, 3]
        """
        text = (
            "Let's start the meeting.\n"
            "Hello everyone, thanks for joining.\n"
            "Hi there, glad to be here.\n"
            "Great, let's begin."
        )

        changes = detect_speaker_changes(text)

        # Verify exact expected speaker change points
        expected_changes = [0, 1, 2, 3]
        assert (
            changes == expected_changes
        ), f"Expected speaker changes at {expected_changes}, got {changes}"

        # Verify greetings preserved in output
        result = assign_speaker_labels(text)
        assert "Hello everyone" in result
        assert "Hi there" in result

    def test_pronoun_shift_detection(self) -> None:
        """Test that pronoun shifts (I/you) are detected with discontinuity check.

        Input (4 lines):
        0: I think we should proceed with the plan.  (start, first-person only)
        1: You make an excellent point.           (I->You shift: prev has I, curr has You but not I)
        2: I agree with your assessment.          (has both I and your - continuity, NO change)
        3: You've done great work on this.        (I->You shift: prev has I, curr has You but not I)

        Expected changes at: [0, 1, 3] - sentence 2 is NOT a change due to pronoun continuity

        This reflects the fixed logic where "I + your" doesn't trigger a change because
        it could be the same speaker continuing to address the other person.
        """
        text = (
            "I think we should proceed with the plan.\n"
            "You make an excellent point.\n"
            "I agree with your assessment.\n"
            "You've done great work on this."
        )

        changes = detect_speaker_changes(text)

        # Verify exact expected speaker change points
        expected_changes = [0, 1, 3]
        assert (
            changes == expected_changes
        ), f"Expected speaker changes at {expected_changes}, got {changes}"

        # Verify output formatting
        result = assign_speaker_labels(text)
        lines = [line for line in result.split("\r\n") if line.strip()]

        # With changes at [0, 1, 3], we expect 3 speaker segments:
        # - Speaker A: sentence 0
        # - Speaker B: sentences 1-2 (grouped due to no change at 2)
        # - Speaker C: sentence 3
        assert len(lines) == 3

        # Verify each segment starts with a speaker label
        assert all(line.startswith("Speaker ") for line in lines)
        assert all("Speaker" in line for line in lines)

    def test_multi_speaker_meeting(self) -> None:
        """Test multi-speaker meeting scenario with complex dialogue.

        Input (6 lines, but sentence tokenizer produces 7 sentences):
        0: Good morning everyone.                     (start, greeting)
        1: Thanks for organizing this meeting.        (thanks triggers change)
        2: What's the first agenda item?              (question)
        3: Yes, let's discuss the Q3 results.         (acknowledgment triggers change)
        4: I've prepared a summary of the data.       (no trigger)
        5: That's helpful.                            (That's triggers change)
        6: What are the key takeaways?                (no trigger - continuation)

        Expected changes at: [0, 1, 3, 5]
        - 0: Start of dialogue
        - 1: "Thanks" is a gratitude marker indicating speaker change
        - 3: "Yes" is an acknowledgment
        - 5: "That's helpful" is a response pattern
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

        # Verify expected speaker change points with new heuristics
        expected_changes = [0, 1, 3, 5]
        assert (
            changes == expected_changes
        ), f"Expected speaker changes at {expected_changes}, got {changes}"

        # Verify all sentences get labeled (7 sentences due to tokenization)
        result = assign_speaker_labels(text)
        lines = [line for line in result.split("\r\n") if line.strip()]
        # With grouping based on changes [0, 1, 3, 5]:
        # Line 0 (Sent 0): Speaker A
        # Line 1 (Sent 1, 2): Speaker B
        # Line 2 (Sent 3, 4): Speaker C
        # Line 3 (Sent 5, 6): Speaker D
        assert len(lines) == 4, f"Expected 4 grouped lines, got {len(lines)}"
        assert all("Speaker" in line for line in lines)

        # Content should be preserved
        assert "agenda item" in result
        assert "Q3 results" in result
        assert "summary" in result
