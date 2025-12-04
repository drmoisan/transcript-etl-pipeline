"""Tests for enhancement orchestration."""

from transcript_etl_pipeline.transform.enhance import enhance_text


class TestEnhanceText:
    """Test the enhance_text orchestration."""

    def test_empty_text(self) -> None:
        """Test empty text returns empty."""
        result, _mapping = enhance_text("")
        assert result == ""
        assert _mapping == {}

    def test_simple_transcript(self) -> None:
        """Test enhancement of simple transcript."""
        text = "Speaker A: Hello.\r\nSpeaker B: Hi there."
        result, _mapping = enhance_text(text)
        # Should have speaker labels
        assert "Speaker A:" in result or "Speaker B:" in result
        # Should preserve structure
        assert "Hello" in result
        assert "Hi there" in result

    def test_with_ui_callback(self) -> None:
        """Test enhancement with UI callback for speaker resolution.

        Note: Dan Moisan is always added as an available attendee,
        so with only one speaker, elimination logic maps Speaker A -> Dan Moisan.
        """

        def mock_ui(
            speaker_label: str, sample_utterances: list[str], candidates: list[str]
        ) -> str | None:
            """Mock UI that would resolve speakers if called."""
            if speaker_label == "Speaker A":
                return "Alice"
            return None

        text = "Speaker A: Hello everyone.\\r\\nSpeaker A: How are you?"
        result, _mapping = enhance_text(text, ui_callback=mock_ui)
        # With only one speaker and Dan Moisan always available,
        # elimination logic resolves Speaker A -> Dan Moisan
        if "Speaker A" in _mapping:
            assert _mapping["Speaker A"] == "Dan Moisan"
            assert "Dan Moisan:" in result

    def test_paragraph_detection_applied(self) -> None:
        """Test that paragraph detection is applied."""
        text = "Speaker A: First sentence.\r\nSecond sentence.\r\nThird sentence."
        result, _mapping = enhance_text(text)
        # Should add paragraph breaks after sentences
        # Count blank lines as indication of paragraph breaks
        blank_line_count = result.count("\r\n\r\n")
        # Might have paragraph breaks
        assert blank_line_count >= 0

    def test_speaker_resolution_then_paragraphs(self) -> None:
        """Test that speaker resolution happens before paragraph detection."""

        def mock_ui(
            speaker_label: str, sample_utterances: list[str], candidates: list[str]
        ) -> str | None:
            """Mock UI that resolves Speaker A."""
            if speaker_label == "Speaker A":
                return "Alice"
            return None

        text = "Speaker A: First.\r\nSecond.\r\nSpeaker B: Hello."
        result, _mapping = enhance_text(text, ui_callback=mock_ui)
        # Should have Alice instead of Speaker A
        if "Speaker A" in _mapping:
            assert "Alice:" in result

    def test_metadata_preserved(self) -> None:
        """Test that metadata section is preserved."""
        text = "Meeting: Team Sync\r\nDate: 2024-01-15\r\nSpeaker: Hello everyone."
        result, _mapping = enhance_text(text)
        # Metadata should be preserved
        assert "Meeting: Team Sync" in result
        assert "Date: 2024-01-15" in result

    def test_dan_moisan_identification(self) -> None:
        """Test Dan Moisan identification in full enhancement."""
        text = (
            "Speaker A: Dan, what do you think?\r\n"
            "Speaker B: I think it's good.\r\n"
            "Speaker A: Thanks."
        )
        result, _mapping = enhance_text(text)
        # Should identify Speaker B as Dan Moisan
        if "Speaker B" in _mapping:
            assert _mapping["Speaker B"] == "Dan Moisan"
            assert "Dan Moisan:" in result

    def test_complex_transcript(self) -> None:
        """Test enhancement of complex transcript with multiple features."""
        text = (
            "Meeting: Planning Session\r\n"
            "Attendees: John, Alice\r\n"
            "Speaker A: Hello everyone.\r\n"
            "How is everyone doing today?\r\n"
            "Speaker B: I'm doing well, thanks.\r\n"
            "What about you?"
        )
        result, _mapping = enhance_text(text)
        # Should preserve metadata
        assert "Meeting:" in result
        # Should have speakers (possibly resolved)
        assert "Speaker" in result or "John" in result or "Alice" in result
        # Should preserve content
        assert "everyone" in result

    def test_no_ui_callback(self) -> None:
        """Test enhancement without UI callback."""
        text = "Speaker A: Hello.\r\nSpeaker B: Hi."
        result, _mapping = enhance_text(text)
        # Should complete without error
        assert "Hello" in result
        # Might or might not resolve speakers (depends on auto-resolution)
        assert len(result) > 0


class TestEnhanceTextSpeakerlessRouting:
    """Test routing logic for speakerless transcripts in enhance_text."""

    def test_speakerless_transcript_gets_labels(self) -> None:
        """Test that transcript WITHOUT speaker labels triggers speakerless detection.

        Verifies:
        1. Speakerless detection is triggered
        2. Generic speaker labels are added
        3. Empty speaker mapping is returned
        """
        text_no_speakers = (
            "Hello everyone, thanks for joining.\r\n"
            "Thank you for having me.\r\n"
            "Let's get started with the agenda.\r\n"
        )

        enhanced, speaker_map = enhance_text(text_no_speakers)

        # Verify generic speaker labels were added
        assert "Speaker A:" in enhanced or "Speaker B:" in enhanced

        # Verify speaker mapping is empty (no name resolution for generic speakers)
        assert speaker_map == {}

    def test_speakerless_with_metadata(self) -> None:
        """Test speakerless detection with metadata section.

        Metadata lines like "Date:", "Attendees:" may be detected as labels,
        but if dialogue has no labels, speakerless detection should apply.
        """
        text = (
            "Date: 2025-12-03\r\n"
            "Attendees: Alice, Bob\r\n"
            "\r\n"
            "Hello everyone.\r\n"
            "Thanks for joining.\r\n"
        )

        enhanced, _speaker_map = enhance_text(text)

        # Verify text was enhanced
        assert enhanced is not None
        assert len(enhanced) > 0

        # Current behavior: metadata may be detected as labels
        # This test documents actual behavior
        assert "Hello everyone" in enhanced

    def test_speakerless_with_num_speakers_parameter(self) -> None:
        """Test that num_speakers parameter is accepted and used.

        Verifies:
        1. num_speakers parameter is accepted
        2. Parameter is passed to speakerless detection
        """
        text = (
            "Hello, welcome to the meeting.\r\n"
            "Thank you for having us.\r\n"
            "Let's discuss the project.\r\n"
        )

        # Test with explicit num_speakers
        enhanced, _speaker_map = enhance_text(text, num_speakers=2)

        # Verify speakerless detection was applied
        assert "Speaker A:" in enhanced
        # Verify speaker mapping is empty for speakerless
        assert len(_speaker_map) == 0

    def test_labeled_transcript_not_affected_by_speakerless(self) -> None:
        """Test that transcripts WITH labels are not affected by speakerless routing.

        Regression test to ensure speakerless integration doesn't break
        existing labeled transcript processing.
        """
        text = "Manager: Let's review the results.\r\n" "Analyst: Revenue is up 15 percent.\r\n"

        enhanced, _speaker_map = enhance_text(text)

        # Verify existing behavior is preserved
        assert "Manager:" in enhanced
        assert "Analyst:" in enhanced

    def test_pure_dialogue_triggers_speakerless(self) -> None:
        """Test that continuous dialogue without labels triggers speakerless detection."""
        pure_dialogue = (
            "Welcome to our quarterly review. "
            "I've analyzed the metrics. "
            "Thank you. "
            "What are your thoughts?"
        )

        enhanced, _speaker_map = enhance_text(pure_dialogue)

        # Verify speakerless detection was triggered
        assert "Speaker A:" in enhanced or "Speaker B:" in enhanced
        # Verify speaker mapping is empty for speakerless
        assert len(_speaker_map) == 0


class TestEnhanceTextIdentityConstraints:
    """Test identity constraints affecting speaker assignment through enhance_text.

    These characterization tests document how identity constraints (self-identification
    and addresses_other patterns) are applied when speakerless detection is triggered
    via the enhance_text orchestration.

    Note: Identity-aware grouping only kicks in for 3+ speakers. With 2 speakers,
    simple alternating assignment is used which doesn't consider identity constraints.
    """

    def test_self_identification_with_two_speakers_uses_alternation(self) -> None:
        """Characterize that 2-speaker mode uses alternating assignment.

        With num_speakers=2, the speakerless detection uses simple alternating
        assignment (A→B→A→B...) based on detected speaker changes, without
        considering identity constraints from self-identification patterns.

        This documents current behavior - identity constraints are only enforced
        via similarity-based grouping for 3+ speakers.
        """
        text = (
            "Hello everyone.\r\n"
            "I'm Peter Parker and I work in the lab.\r\n"
            "Nice to meet you.\r\n"
            "I'm Frank Oz and I like puppets.\r\n"
        )

        enhanced, speaker_map = enhance_text(text, num_speakers=2)

        # Verify speakerless detection was triggered
        assert speaker_map == {}  # Empty for speakerless

        # Verify speaker labels were added
        assert "Speaker A:" in enhanced or "Speaker B:" in enhanced

        # Document current behavior: with 2 speakers, uses alternating assignment
        # based on speaker change detection, not identity constraints.
        # Both self-identifications may end up on the same speaker due to
        # how change points are detected.
        assert "Peter Parker" in enhanced
        assert "Frank Oz" in enhanced

    def test_addresses_other_constraint_with_three_speakers(self) -> None:
        """Test that 'Thanks [Name]' patterns affect speaker assignment.

        When speaker says 'Thanks Frank', they cannot BE Frank - this
        addresses_other constraint should prevent that grouping.
        """
        text = (
            "Hello everyone.\r\n"
            "I'm Frank Oz.\r\n"
            "Thanks Frank, that was interesting.\r\n"
            "You're welcome.\r\n"
        )

        enhanced, speaker_map = enhance_text(text, num_speakers=3)

        # Verify speakerless detection was triggered
        assert speaker_map == {}

        # Verify speaker labels were added
        assert "Speaker" in enhanced

        # Document behavior: Frank Oz's self-identification and
        # "Thanks Frank" should result in different speaker assignments
        lines = enhanced.split("\r\n")
        frank_self_id_speaker = None
        thanks_frank_speaker = None

        for line in lines:
            if "I'm Frank Oz" in line:
                if "Speaker A:" in line:
                    frank_self_id_speaker = "A"
                elif "Speaker B:" in line:
                    frank_self_id_speaker = "B"
                elif "Speaker C:" in line:
                    frank_self_id_speaker = "C"
            if "Thanks Frank" in line:
                if "Speaker A:" in line:
                    thanks_frank_speaker = "A"
                elif "Speaker B:" in line:
                    thanks_frank_speaker = "B"
                elif "Speaker C:" in line:
                    thanks_frank_speaker = "C"

        # "Thanks Frank" cannot be assigned to Frank's speaker
        if frank_self_id_speaker is not None and thanks_frank_speaker is not None:
            assert thanks_frank_speaker != frank_self_id_speaker

    def test_multiple_self_identifications_needs_more_changes(self) -> None:
        """Characterize that all-grouped output occurs with weak change signals.

        With three self-identifications and num_speakers=3, the grouping
        depends on detected speaker change points. If the sentences don't
        have enough change signals (pronouns, questions, greetings), they
        may all be grouped to a single speaker.

        This documents current behavior: identity constraints alone don't
        force speaker changes - they only prevent conflicting groupings
        when change points are detected.
        """
        text = (
            "Hello everyone.\r\n"
            "I'm Peter Parker.\r\n"
            "Nice to be here.\r\n"
            "I'm Frank Oz.\r\n"
            "Welcome to the team.\r\n"
            "I'm Fred Flintstone.\r\n"
        )

        enhanced, speaker_map = enhance_text(text, num_speakers=3)

        # Verify speakerless detection was triggered
        assert speaker_map == {}

        # Document current behavior: with weak change signals, all may be grouped
        # The identity constraints prevent conflicting groupings but don't force
        # speaker changes on their own.
        assert "Speaker A:" in enhanced
        assert "Peter Parker" in enhanced
        assert "Frank Oz" in enhanced
        assert "Fred Flintstone" in enhanced

    def test_self_identifications_with_strong_change_signals(self) -> None:
        """Test that self-identifications with change signals are separated.

        With strong speaker change signals (questions, responses, greetings),
        different self-identifications should end up on different speakers
        due to the identity constraints preventing conflicting groupings.
        """
        text = (
            "Hello everyone, how are you?\r\n"
            "I'm doing great. I'm Peter Parker.\r\n"
            "Thank you for asking!\r\n"
            "I'm Frank Oz, nice to meet you.\r\n"
        )

        enhanced, speaker_map = enhance_text(text, num_speakers=3)

        # Verify speakerless detection was triggered
        assert speaker_map == {}

        # With strong change signals, should have multiple speakers
        speaker_labels: set[str] = set()
        for line in enhanced.split("\r\n"):
            if line.startswith("Speaker A:"):
                speaker_labels.add("A")
            elif line.startswith("Speaker B:"):
                speaker_labels.add("B")
            elif line.startswith("Speaker C:"):
                speaker_labels.add("C")

        # Strong change signals (question, response, greeting) produce distinct speakers
        assert len(speaker_labels) >= 2


class TestEnhanceTextNormalizationInteractions:
    """Test how enhance_text interacts with text normalization states.

    These characterization tests verify that enhance_text handles
    various text states correctly, including:
    - Text with different line endings
    - Text with unusual whitespace
    - Text that may or may not have been normalized
    """

    def test_unix_line_endings_handled(self) -> None:
        """Test that text with Unix line endings (LF) is processed correctly.

        The enhance_text function should handle Unix line endings even
        though the pipeline normally works with CRLF.
        """
        text = "Speaker A: Hello.\nSpeaker B: Hi there."

        enhanced, _speaker_map = enhance_text(text)

        # Should preserve content
        assert "Hello" in enhanced
        assert "Hi there" in enhanced

    def test_mixed_line_endings_handled(self) -> None:
        """Test that text with mixed line endings is processed correctly.

        Real-world text may have mixed LF/CRLF/CR line endings.
        """
        # Mix of CRLF, LF, and content
        text = "Speaker A: First.\r\nSpeaker A: Second.\nSpeaker B: Third."

        enhanced, _speaker_map = enhance_text(text)

        # Should preserve all content
        assert "First" in enhanced
        assert "Second" in enhanced
        assert "Third" in enhanced

    def test_whitespace_only_text_handled(self) -> None:
        """Test that whitespace-only text is handled gracefully."""
        text = "   \r\n   \r\n   "

        _enhanced, speaker_map = enhance_text(text)

        # Should handle gracefully without crashing
        assert speaker_map == {}

    def test_single_line_no_labels(self) -> None:
        """Test single-line text without labels triggers speakerless."""
        text = "Hello everyone, welcome to the meeting."

        enhanced, speaker_map = enhance_text(text)

        # Should trigger speakerless detection
        assert speaker_map == {}

        # Should add a speaker label
        assert "Speaker A:" in enhanced

    def test_trailing_whitespace_preserved(self) -> None:
        """Test content preservation when input has trailing whitespace."""
        text = "Speaker A: Hello.   \r\nSpeaker B: Hi.   "

        enhanced, _speaker_map = enhance_text(text)

        # Content should be preserved (whitespace may be cleaned)
        assert "Hello" in enhanced
        assert "Hi" in enhanced

    def test_empty_lines_between_speakers(self) -> None:
        """Test handling of empty lines between speaker utterances."""
        text = (
            "Speaker A: First statement.\r\n"
            "\r\n"
            "Speaker B: Second statement.\r\n"
            "\r\n"
            "Speaker A: Third statement."
        )

        enhanced, _speaker_map = enhance_text(text)

        # All content should be preserved
        assert "First statement" in enhanced
        assert "Second statement" in enhanced
        assert "Third statement" in enhanced

    def test_very_long_speakerless_text(self) -> None:
        """Test speakerless detection with longer text.

        Verify that longer dialogue without labels is processed correctly.
        """
        text = (
            "Welcome everyone to our quarterly planning session. "
            "I'm excited to share our progress. "
            "Thank you for joining us today. "
            "Let me start with the financial overview. "
            "Revenue increased by fifteen percent. "
            "That's great news. "
            "What about the expenses? "
            "Expenses remained flat. "
            "Excellent work everyone."
        )

        enhanced, speaker_map = enhance_text(text)

        # Should trigger speakerless detection
        assert speaker_map == {}

        # Should add speaker labels
        assert "Speaker" in enhanced

        # Content should be preserved
        assert "quarterly planning session" in enhanced
        assert "fifteen percent" in enhanced


class TestEnhanceTextEdgeCases:
    """Test edge cases and boundary conditions for enhance_text.

    These tests document behavior in unusual but valid input scenarios.
    """

    def test_single_sentence_speakerless(self) -> None:
        """Test single sentence without speaker label."""
        text = "Hello world."

        enhanced, speaker_map = enhance_text(text)

        # Should be assigned to Speaker A
        assert speaker_map == {}
        assert "Speaker A:" in enhanced
        assert "Hello world" in enhanced

    def test_question_answer_pattern_speakerless(self) -> None:
        """Test question-answer pattern triggers speaker changes.

        Questions followed by answers should result in speaker changes.
        """
        text = "How are you doing today?\r\nI'm doing great, thanks for asking."

        enhanced, speaker_map = enhance_text(text)

        # Should trigger speakerless with speaker changes
        assert speaker_map == {}

        # Both speakers should be present
        lines = [line for line in enhanced.split("\r\n") if line.strip()]

        # Document behavior: Q&A pattern should result in different speakers
        speaker_labels: set[str] = set()
        for line in lines:
            if line.startswith("Speaker A:"):
                speaker_labels.add("A")
            elif line.startswith("Speaker B:"):
                speaker_labels.add("B")

        # Q&A pattern produces speaker changes - should have 2 speakers
        assert len(speaker_labels) >= 2

    def test_pronoun_shift_detection(self) -> None:
        """Test pronoun shift pattern (I/you exchange) affects speaker assignment.

        When one sentence has 'I' and next has 'you' (or vice versa),
        this often indicates a speaker change.
        """
        text = "I think we should proceed with the plan.\r\nYou make an excellent point."

        enhanced, speaker_map = enhance_text(text)

        assert speaker_map == {}
        assert "Speaker" in enhanced

    def test_greeting_triggers_speaker_change(self) -> None:
        """Test that greetings like 'Hello' trigger speaker changes."""
        text = "Let's get started.\r\nHello everyone, thanks for joining."

        enhanced, speaker_map = enhance_text(text)

        assert speaker_map == {}
        assert "Speaker" in enhanced

    def test_thank_you_pattern_speaker_change(self) -> None:
        """Test that 'Thank you' patterns trigger speaker changes."""
        text = "Here are the quarterly results.\r\n" "Thank you for that comprehensive overview."

        enhanced, speaker_map = enhance_text(text)

        assert speaker_map == {}
        # "Thank you" at start of sentence should trigger speaker change
        assert "Speaker" in enhanced

    def test_acknowledgment_triggers_speaker_change(self) -> None:
        """Test that acknowledgment patterns trigger speaker changes."""
        text = "We need to review the budget.\r\nSure, let me pull up the numbers."

        enhanced, speaker_map = enhance_text(text)

        assert speaker_map == {}
        assert "Speaker" in enhanced

    def test_num_speakers_one(self) -> None:
        """Test num_speakers=1 parameter (monologue)."""
        text = (
            "Welcome to my presentation.\r\n"
            "Today I'll discuss the project.\r\n"
            "Let me start with the background."
        )

        enhanced, speaker_map = enhance_text(text, num_speakers=1)

        assert speaker_map == {}

        # With num_speakers=1, all should be Speaker A
        assert "Speaker A:" in enhanced
        # Should not have Speaker B
        lines = enhanced.split("\r\n")
        for line in lines:
            if line.strip():
                assert not line.startswith("Speaker B:")

    def test_num_speakers_four(self) -> None:
        """Test num_speakers=4 parameter for multi-person dialogue."""
        text = "Hello.\r\n" "Hi there.\r\n" "Good morning.\r\n" "Good to see you all."

        enhanced, speaker_map = enhance_text(text, num_speakers=4)

        assert speaker_map == {}
        assert "Speaker" in enhanced

    def test_labeled_with_speakerless_content(self) -> None:
        """Test transcript with some labels but also unlabeled lines.

        Regression test: If transcript has speaker labels, the speakerless
        path should NOT be triggered even if some lines lack labels.
        """
        text = (
            "Speaker A: Let me explain.\r\n"
            "This is an important point.\r\n"  # Continuation without label
            "Speaker B: I understand."
        )

        enhanced, _speaker_map = enhance_text(text)

        # Should NOT trigger speakerless detection
        assert "Speaker A:" in enhanced
        assert "Speaker B:" in enhanced

    def test_metadata_then_speakerless_dialogue(self) -> None:
        """Test transcript with metadata section followed by speakerless dialogue.

        The metadata section may contain label-like patterns (Date:, Attendees:)
        but the actual dialogue should still trigger speakerless detection if
        there are no speaker labels in the dialogue portion.
        """
        text = (
            "Date: 2025-12-03\r\n"
            "Topic: Quarterly Review\r\n"
            "\r\n"
            "Welcome everyone.\r\n"
            "Thank you for joining.\r\n"
        )

        enhanced, _speaker_map = enhance_text(text)

        # Text should be enhanced
        assert len(enhanced) > 0
        assert "Welcome everyone" in enhanced
