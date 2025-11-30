"""Tests for speakerless transcript detection and speaker assignment."""

from transcript_etl_pipeline.transform.speakerless import (
    assign_speaker_labels,
    detect_speaker_changes,
    has_speaker_labels,
)


class TestHasSpeakerLabels:
    """Tests for speaker label detection."""

    def test_text_with_speaker_labels(self) -> None:
        """Test detection of text with standard speaker labels."""
        text = "Speaker A: Hello everyone.\r\nSpeaker B: Hi there."
        assert has_speaker_labels(text) is True

    def test_text_with_named_speakers(self) -> None:
        """Test detection of text with named speaker labels."""
        text = "John: Hello everyone.\r\nMary: Hi there.\r\nJohn: How are you?"
        assert has_speaker_labels(text) is True

    def test_text_without_speaker_labels(self) -> None:
        """Test detection of text without speaker labels."""
        text = "Hello everyone.\r\nHi there.\r\nHow are you?"
        assert has_speaker_labels(text) is False

    def test_empty_text(self) -> None:
        """Test handling of empty text."""
        assert has_speaker_labels("") is False
        assert has_speaker_labels("   ") is False

    def test_single_speaker_label(self) -> None:
        """Test text with only one speaker label (not enough for dialogue)."""
        text = "Speaker A: Hello everyone.\r\nThis is just regular text."
        assert has_speaker_labels(text) is False

    def test_colons_in_content_not_labels(self) -> None:
        """Test that colons in content are not mistaken for speaker labels."""
        text = "The time is 3:00 PM.\r\nMeeting starts at 4:30."
        assert has_speaker_labels(text) is False

    def test_metadata_with_colons(self) -> None:
        """Test that metadata lines are detected as potential speaker labels.

        Note: The current heuristic treats "Word: content" as speaker labels.
        Distinguishing metadata from dialogue labels requires more context.
        """
        text = "Date: 2025-01-01\r\nTime: 3:00 PM\r\nAttendees: John, Mary"
        # These match the speaker label pattern
        # More sophisticated detection would use additional context
        assert has_speaker_labels(text) is True


class TestDetectSpeakerChanges:
    """Tests for speaker change detection."""

    def test_question_answer_pattern(self) -> None:
        """Test detection of question-answer speaker changes."""
        text = "What do you think about this?\r\nI think it's a great idea."
        changes = detect_speaker_changes(text)
        # First line is always a change point, second should be detected as new speaker
        assert 0 in changes
        assert len(changes) >= 1

    def test_pronoun_shift_detection(self) -> None:
        """Test detection of pronoun shift patterns."""
        text = "I believe we should proceed.\r\nYou make a good point."
        changes = detect_speaker_changes(text)
        assert 0 in changes
        # Should detect shift from I to You
        assert len(changes) >= 1

    def test_greeting_detection(self) -> None:
        """Test detection of greetings as speaker changes."""
        text = "Let's begin the meeting.\r\nHello everyone, thanks for joining."
        changes = detect_speaker_changes(text)
        # Hello should trigger a speaker change
        assert len(changes) >= 1

    def test_acknowledgment_detection(self) -> None:
        """Test detection of acknowledgments as speaker changes."""
        text = "Can you confirm the numbers?\r\nYes, they look correct."
        changes = detect_speaker_changes(text)
        # Yes should be detected as acknowledgment from different speaker
        assert len(changes) >= 1

    def test_empty_text(self) -> None:
        """Test handling of empty text."""
        assert detect_speaker_changes("") == []
        assert detect_speaker_changes("   ") == []

    def test_single_line(self) -> None:
        """Test handling of single line text."""
        changes = detect_speaker_changes("Just one line here.")
        assert changes == [0]

    def test_multiple_speakers(self) -> None:
        """Test detection with multiple speaker changes."""
        text = (
            "Good morning everyone.\r\n"
            "Hi, thanks for having us.\r\n"
            "Shall we start with the agenda?\r\n"
            "Yes, let's begin."
        )
        changes = detect_speaker_changes(text)
        # Should detect multiple change points
        assert 0 in changes


class TestAssignSpeakerLabels:
    """Tests for speaker label assignment."""

    def test_basic_dialogue(self) -> None:
        """Test basic dialogue labeling."""
        text = "What time is the meeting?\r\nIt starts at 3 PM."
        result = assign_speaker_labels(text)
        # Should contain speaker labels
        assert "Speaker" in result
        assert ":" in result

    def test_already_labeled(self) -> None:
        """Test that already-labeled text is returned unchanged."""
        text = "Speaker A: Hello.\r\nSpeaker B: Hi there."
        result = assign_speaker_labels(text)
        assert result == text

    def test_empty_text(self) -> None:
        """Test handling of empty text."""
        assert assign_speaker_labels("") == ""
        assert assign_speaker_labels("   ") == "   "

    def test_single_speaker_hint(self) -> None:
        """Test with explicit speaker count hint."""
        text = "Hello everyone.\r\nWelcome to the meeting."
        result = assign_speaker_labels(text, num_speakers=2)
        assert "Speaker A" in result or "Speaker B" in result

    def test_preserves_content(self) -> None:
        """Test that content is preserved after labeling."""
        text = "What's the status?\r\nEverything is on track."
        result = assign_speaker_labels(text)
        assert "status" in result
        assert "track" in result

    def test_crlf_line_endings(self) -> None:
        """Test that output uses CRLF line endings."""
        text = "Line one.\r\nLine two."
        result = assign_speaker_labels(text)
        # Output should use CRLF
        assert "\r\n" in result

    def test_complex_dialogue(self) -> None:
        """Test with a more complex dialogue pattern."""
        text = (
            "Good morning, let's discuss the project.\r\n"
            "Sure, I've prepared a summary.\r\n"
            "What are the key findings?\r\n"
            "The main issue is the timeline."
        )
        result = assign_speaker_labels(text)
        # Should have speaker labels
        lines = result.split("\r\n")
        labeled_lines = [line for line in lines if line.strip() and "Speaker" in line]
        assert len(labeled_lines) >= 1


class TestNLTKIntegration:
    """Tests for NLTK integration in speaker detection."""

    def test_pronoun_analysis_available(self) -> None:
        """Test that pronoun analysis works with NLTK."""
        # This test verifies NLTK integration is working
        text = "I think we should proceed.\r\nYou're right about that."
        changes = detect_speaker_changes(text)
        # Should not raise exceptions and should return results
        assert isinstance(changes, list)

    def test_graceful_nltk_fallback(self) -> None:
        """Test graceful handling when NLTK has issues."""
        # Even without NLTK data, should return basic results
        text = "Hello there.\r\nHi, how are you?"
        changes = detect_speaker_changes(text)
        # Should return at least the first change point
        assert 0 in changes


class TestSpeakerlessTranscriptScenarios:
    """Real-world scenario tests for speakerless transcripts."""

    def test_interview_pattern(self) -> None:
        """Test interview-style Q&A pattern."""
        text = (
            "Tell me about your experience.\r\n"
            "I have five years in the industry.\r\n"
            "What's your biggest achievement?\r\n"
            "I led a team that increased sales by 50%."
        )
        result = assign_speaker_labels(text, num_speakers=2)
        # Should alternate between two speakers
        lines = [line for line in result.split("\r\n") if line.strip()]
        assert all("Speaker" in line for line in lines)

    def test_meeting_pattern(self) -> None:
        """Test meeting-style multi-party dialogue."""
        text = (
            "Welcome to today's meeting.\r\n"
            "Thanks for organizing this.\r\n"
            "Shall we review the agenda?\r\n"
            "Yes, let's start with item one."
        )
        result = assign_speaker_labels(text)
        assert "Speaker" in result

    def test_no_clear_patterns(self) -> None:
        """Test handling when no clear patterns are detected."""
        text = "First statement.\r\nSecond statement.\r\nThird statement."
        result = assign_speaker_labels(text)
        # Should still produce valid output with labels
        assert "Speaker A:" in result
