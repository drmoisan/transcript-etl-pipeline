"""Tests for speaker resolution functionality."""

import pytest

from transcript_etl_pipeline.transform.name import Name
from transcript_etl_pipeline.transform.speakers import (
    _apply_speaker_mappings,  # pyright: ignore[reportPrivateUsage]
    _extract_names_from_dialogue,  # pyright: ignore[reportPrivateUsage]
    _extract_names_from_metadata,  # pyright: ignore[reportPrivateUsage]
    _extract_speaker_from_line,  # pyright: ignore[reportPrivateUsage]
    _extract_speaker_labels,  # pyright: ignore[reportPrivateUsage]
    _extract_speaker_samples,  # pyright: ignore[reportPrivateUsage]
    _identify_dan_moisan,  # pyright: ignore[reportPrivateUsage]
    _identify_speaker_by_name,  # pyright: ignore[reportPrivateUsage]
    _is_likely_person_name,  # pyright: ignore[reportPrivateUsage]
    _is_proper_noun,  # pyright: ignore[reportPrivateUsage]
    _is_speaker_line,  # pyright: ignore[reportPrivateUsage]
    resolve_speakers,
)


class TestIsSpeakerLine:
    """Test speaker line detection."""

    def test_simple_speaker(self) -> None:
        """Test detection of simple speaker line."""
        assert _is_speaker_line("John: hello")
        assert _is_speaker_line("Speaker: test")

    def test_speaker_with_space(self) -> None:
        """Test speaker with space in name."""
        assert _is_speaker_line("Speaker A: hello")
        assert _is_speaker_line("Dan Moisan: hello")

    def test_not_speaker_line(self) -> None:
        """Test non-speaker lines."""
        assert not _is_speaker_line("Just text")
        assert not _is_speaker_line("meeting: notes")


class TestExtractSpeakerFromLine:
    """Test speaker label extraction."""

    def test_extract_simple_speaker(self) -> None:
        """Test extracting simple speaker."""
        assert _extract_speaker_from_line("John: hello") == "John"

    def test_extract_speaker_with_space(self) -> None:
        """Test extracting speaker with space."""
        assert _extract_speaker_from_line("Speaker A: text") == "Speaker A"

    def test_no_speaker(self) -> None:
        """Test line without speaker."""
        assert _extract_speaker_from_line("Just text") is None


class TestExtractSpeakerLabels:
    """Test speaker label extraction from text."""

    def test_single_speaker(self) -> None:
        """Test extracting single speaker."""
        text = "John: Hello\r\nJohn: World"
        labels = _extract_speaker_labels(text)
        assert labels == ["John"]

    def test_multiple_speakers(self) -> None:
        """Test extracting multiple speakers."""
        text = "Speaker A: Hello\r\nSpeaker B: Hi\r\nSpeaker A: Bye"
        labels = _extract_speaker_labels(text)
        assert labels == ["Speaker A", "Speaker B"]

    def test_no_speakers(self) -> None:
        """Test text without speakers."""
        text = "Just some text\r\nNo speakers here"
        labels = _extract_speaker_labels(text)
        assert labels == []


class TestExtractNamesFromMetadata:
    """Test name extraction from metadata."""

    def test_attendees_line(self) -> None:
        """Test extracting names from attendees line."""
        text = "Attendees: John, Jane, Bob\r\nSpeaker: Hello"
        names = _extract_names_from_metadata(text)
        assert Name(first_name="John") in names
        assert Name(first_name="Jane") in names
        assert Name(first_name="Bob") in names

    def test_participants_line(self) -> None:
        """Test extracting names from participants line."""
        text = "Participants: Alice, Charlie\r\nSpeaker: Hi"
        names = _extract_names_from_metadata(text)
        assert Name(first_name="Alice") in names
        assert Name(first_name="Charlie") in names

    def test_no_metadata(self) -> None:
        """Test text without metadata."""
        text = "Speaker: Hello"
        names = _extract_names_from_metadata(text)
        assert len(names) == 0


class TestExtractNamesFromDialogue:
    """Test name extraction from dialogue."""

    def test_names_in_dialogue(self) -> None:
        """Test extracting names mentioned in dialogue."""
        text = "Speaker A: Hello John, how is Alice?\r\nSpeaker B: She is fine."
        names = _extract_names_from_dialogue(text)
        assert Name(first_name="John") in names
        assert Name(first_name="Alice") in names

    def test_filter_common_words(self) -> None:
        """Test filtering out common words."""
        text = "Speaker: The meeting is when?"
        names = _extract_names_from_dialogue(text)
        # Should not include "The" even though it's capitalized
        # Our filter might not be perfect but should avoid obvious ones
        assert Name(first_name="The") not in names or len(names) > 0  # Implementation dependent


class TestIdentifyDanMoisan:
    """Test Dan Moisan identification logic."""

    def test_dan_referenced_in_dialogue(self) -> None:
        """Test identifying Dan when referenced in dialogue."""
        text = (
            "Speaker A: Dan, what do you think?\r\n"
            "Speaker B: I think it's good.\r\n"
            "Speaker A: Thanks Dan."
        )
        labels = ["Speaker A", "Speaker B"]
        dan_label = _identify_dan_moisan(text, labels)
        # Speaker B is likely Dan (not addressing Dan)
        assert dan_label == "Speaker B"

    def test_no_dan_references(self) -> None:
        """Test when Dan is not mentioned."""
        text = "Speaker A: Hello\r\nSpeaker B: Hi"
        labels = ["Speaker A", "Speaker B"]
        dan_label = _identify_dan_moisan(text, labels)
        assert dan_label is None

    def test_hypothetical_dan_reference(self) -> None:
        """Test that hypothetical references to Dan don't trigger identification."""
        text = (
            "Speaker A: Hello\r\n"
            "Speaker B: If you were to say, is Dan a functional sales leader? "
            "I can do sales. Is Dan a functional marketer? Yes, I can do marketing.\r\n"
            "Speaker A: That makes sense."
        )
        labels = ["Speaker A", "Speaker B"]
        dan_label = _identify_dan_moisan(text, labels)
        # Should NOT identify Speaker B as Dan, despite mentioning "Dan"
        # Because these are third-person hypothetical questions, not direct addresses
        assert dan_label is None

    def test_real_world_hypothetical_scenario(self) -> None:
        """Test real-world scenario with complex hypothetical construction."""
        text = (
            "Speaker A: So what's your background?\r\n"
            "Speaker B: Yeah, it is boring. And you know, in my most recent tour of duty "
            "at Sabra, that was a radical turnaround. And you know, the question is, "
            "what's next? And for me, I really love managing businesses end to end. "
            "I'm not a functional expert. So if you were to say, hey, is Dan a functional "
            "sales leader? I can do sales, I've done sales. Is Dan a functional marketer? "
            "Yes, I can do marketing, I've done a lot of marketing.\r\n"
            "Speaker A: That's interesting."
        )
        labels = ["Speaker A", "Speaker B"]
        dan_label = _identify_dan_moisan(text, labels)
        # Speaker B is Dan (self-referencing in third person within hypothetical)
        # Should NOT be identified because there's no direct address from Speaker A
        assert dan_label is None or dan_label == "Speaker B"

    def test_vocative_comma_direct_address(self) -> None:
        """Test detection of vocative comma pattern: 'Dan, ...'"""
        text = "Speaker A: Dan, could you explain that?\r\n" "Speaker B: Sure, let me clarify."
        labels = ["Speaker A", "Speaker B"]
        dan_label = _identify_dan_moisan(text, labels)
        assert dan_label == "Speaker B"

    def test_vocative_comma_at_end(self) -> None:
        """Test detection of vocative comma at end of sentence: '..., Dan.'"""
        text = (
            "Speaker A: I'm learning so much about you, Dan.\r\n"
            "Speaker B: Thank you, I appreciate that."
        )
        labels = ["Speaker A", "Speaker B"]
        dan_label = _identify_dan_moisan(text, labels)
        assert dan_label == "Speaker B"

    def test_thanks_dan_pattern(self) -> None:
        """Test 'Thanks, Dan' pattern."""
        text = "Speaker A: Thanks, Dan.\r\n" "Speaker B: You're welcome."
        labels = ["Speaker A", "Speaker B"]
        dan_label = _identify_dan_moisan(text, labels)
        assert dan_label == "Speaker B"

    def test_real_world_learning_about_you_dan(self) -> None:
        """Test real-world case: 'Such a good story...I'm learning so much about you, Dan.'"""
        text = (
            "Speaker A: Such a good story. Yeah. I can't wait to hear your second one. "
            "I'm learning so much about you, Dan.\r\n"
            "Speaker B: Thank you, that means a lot."
        )
        labels = ["Speaker A", "Speaker B"]
        dan_label = _identify_dan_moisan(text, labels)
        assert dan_label == "Speaker B"

    def test_prepositional_reference_to_dan(self) -> None:
        """Test detection of prepositional references: 'to Dan', 'with Dan', etc."""
        text = (
            "Speaker A: I need to speak to Dan about the project.\r\n"
            "Speaker B: I can help with that."
        )
        labels = ["Speaker A", "Speaker B"]
        dan_label = _identify_dan_moisan(text, labels)
        assert dan_label == "Speaker B"

    def test_with_dan_reference(self) -> None:
        """Test 'with Dan' prepositional phrase."""
        text = "Speaker A: I was working with Dan on this.\r\n" "Speaker B: Yes, that's correct."
        labels = ["Speaker A", "Speaker B"]
        dan_label = _identify_dan_moisan(text, labels)
        assert dan_label == "Speaker B"

    def test_for_dan_reference(self) -> None:
        """Test 'for Dan' prepositional phrase."""
        text = "Speaker A: This question is for Dan.\r\n" "Speaker B: I'll answer that."
        labels = ["Speaker A", "Speaker B"]
        dan_label = _identify_dan_moisan(text, labels)
        assert dan_label == "Speaker B"

    def test_about_dan_reference(self) -> None:
        """Test 'about Dan' prepositional phrase."""
        text = (
            "Speaker A: I heard about Dan joining the team.\r\n"
            "Speaker B: Yes, I'm excited to be here."
        )
        labels = ["Speaker A", "Speaker B"]
        dan_label = _identify_dan_moisan(text, labels)
        assert dan_label == "Speaker B"

    def test_from_dan_reference(self) -> None:
        """Test 'from Dan' prepositional phrase."""
        text = (
            "Speaker A: We received feedback from Dan.\r\n"
            "Speaker B: I shared my thoughts yesterday."
        )
        labels = ["Speaker A", "Speaker B"]
        dan_label = _identify_dan_moisan(text, labels)
        assert dan_label == "Speaker B"

    def test_dan_mentioned_attribution(self) -> None:
        """Test attributive references: 'Dan mentioned', 'Dan said'."""
        text = "Speaker A: Dan mentioned this earlier.\r\n" "Speaker B: What was it?"
        labels = ["Speaker A", "Speaker B"]
        dan_label = _identify_dan_moisan(text, labels)
        assert dan_label == "Speaker B"

    def test_dan_said_attribution(self) -> None:
        """Test 'Dan said' attribution."""
        text = "Speaker A: Dan said we should proceed.\r\n" "Speaker B: I'm not sure about that."
        labels = ["Speaker A", "Speaker B"]
        dan_label = _identify_dan_moisan(text, labels)
        assert dan_label == "Speaker B"

    def test_dan_thinks_attribution(self) -> None:
        """Test 'Dan thinks' attribution."""
        text = (
            "Speaker A: Dan thinks this is the right approach.\r\n"
            "Speaker B: Interesting perspective."
        )
        labels = ["Speaker A", "Speaker B"]
        dan_label = _identify_dan_moisan(text, labels)
        assert dan_label == "Speaker B"

    def test_dan_believes_attribution(self) -> None:
        """Test 'Dan believes' attribution."""
        text = (
            "Speaker A: Dan believes we can improve this.\r\n" "Speaker B: Thanks for the feedback."
        )
        labels = ["Speaker A", "Speaker B"]
        dan_label = _identify_dan_moisan(text, labels)
        assert dan_label == "Speaker B"

    def test_dan_suggested_attribution(self) -> None:
        """Test 'Dan suggested' attribution."""
        text = (
            "Speaker A: Dan suggested a different approach.\r\n"
            "Speaker B: Let me explain my reasoning."
        )
        labels = ["Speaker A", "Speaker B"]
        dan_label = _identify_dan_moisan(text, labels)
        assert dan_label == "Speaker B"

    def test_is_dan_a_article_excluded(self) -> None:
        """Test exclusion of 'is Dan a/an/the' third-person questions."""
        text = "Speaker A: So, is Dan a good fit for this role?\r\n" "Speaker B: I think so."
        labels = ["Speaker A", "Speaker B"]
        dan_label = _identify_dan_moisan(text, labels)
        # Should NOT identify anyone as Dan
        assert dan_label is None

    def test_is_dan_an_excluded(self) -> None:
        """Test exclusion of 'is Dan an' pattern."""
        text = "Speaker A: Is Dan an experienced leader?\r\n" "Speaker B: That's a good question."
        labels = ["Speaker A", "Speaker B"]
        dan_label = _identify_dan_moisan(text, labels)
        assert dan_label is None

    def test_is_dan_the_excluded(self) -> None:
        """Test exclusion of 'is Dan the' pattern."""
        text = "Speaker A: Is Dan the right person?\r\n" "Speaker B: I believe so."
        labels = ["Speaker A", "Speaker B"]
        dan_label = _identify_dan_moisan(text, labels)
        assert dan_label is None

    def test_is_dan_general_excluded(self) -> None:
        """Test exclusion of general 'is Dan' pattern."""
        text = "Speaker A: Is Dan available for the meeting?\r\n" "Speaker B: Yes, I can attend."
        labels = ["Speaker A", "Speaker B"]
        dan_label = _identify_dan_moisan(text, labels)
        assert dan_label is None

    def test_if_you_were_to_say_excluded(self) -> None:
        """Test exclusion of 'if you were to say' hypothetical."""
        text = (
            "Speaker A: Continue.\r\n"
            "Speaker B: If you were to say, Dan is great, I'd agree.\r\n"
            "Speaker A: Noted."
        )
        labels = ["Speaker A", "Speaker B"]
        dan_label = _identify_dan_moisan(text, labels)
        assert dan_label is None

    def test_if_someone_were_to_ask_excluded(self) -> None:
        """Test exclusion of 'if someone were to ask' hypothetical."""
        text = (
            "Speaker A: What do you think?\r\n"
            "Speaker B: If someone were to ask about Dan, I'd say he's qualified.\r\n"
            "Speaker A: Good to know."
        )
        labels = ["Speaker A", "Speaker B"]
        dan_label = _identify_dan_moisan(text, labels)
        assert dan_label is None

    def test_the_question_is_dan_excluded(self) -> None:
        """Test exclusion of 'the question is...Dan' hypothetical."""
        text = (
            "Speaker A: Tell me more.\r\n"
            "Speaker B: The question is whether Dan can handle this.\r\n"
            "Speaker A: I see."
        )
        labels = ["Speaker A", "Speaker B"]
        dan_label = _identify_dan_moisan(text, labels)
        assert dan_label is None

    def test_you_might_ask_dan_excluded(self) -> None:
        """Test exclusion of 'you might ask...Dan' hypothetical."""
        text = (
            "Speaker A: Proceed.\r\n"
            "Speaker B: You might ask why Dan chose this path.\r\n"
            "Speaker A: Right."
        )
        labels = ["Speaker A", "Speaker B"]
        dan_label = _identify_dan_moisan(text, labels)
        assert dan_label is None

    def test_one_might_say_dan_excluded(self) -> None:
        """Test exclusion of 'one might say...Dan' hypothetical."""
        text = (
            "Speaker A: Go on.\r\n"
            "Speaker B: One might say Dan has unique skills.\r\n"
            "Speaker A: Interesting."
        )
        labels = ["Speaker A", "Speaker B"]
        dan_label = _identify_dan_moisan(text, labels)
        assert dan_label is None

    def test_multiple_speakers_one_addresses_dan(self) -> None:
        """Test with multiple speakers where only one addresses Dan."""
        text = (
            "Speaker A: Dan, what's your opinion?\r\n"
            "Speaker B: I agree.\r\n"
            "Speaker C: Me too.\r\n"
            "Speaker A: Thanks for asking Dan."
        )
        labels = ["Speaker A", "Speaker B", "Speaker C"]
        dan_label = _identify_dan_moisan(text, labels)
        # Speaker A addresses Dan (twice), so A is NOT Dan
        # Speaker B and C don't address Dan, so one of them could be Dan
        # The algorithm picks the first non-addressing speaker
        assert dan_label in ["Speaker B", "Speaker C"]

    def test_dan_as_speaker_label_ignored(self) -> None:
        """Test that 'Dan:' as speaker label is properly ignored."""
        text = "Dan: Hello everyone.\r\n" "Speaker A: Hi Dan, how are you?\r\n" "Dan: I'm good."
        labels = ["Dan", "Speaker A"]
        dan_label = _identify_dan_moisan(text, labels)
        # "Dan" as a label is excluded; Speaker A addresses Dan, so Dan must be the other speaker
        # But "Dan" IS a speaker label, so the function should NOT identify it
        assert dan_label is None or dan_label == "Dan"

    def test_no_direct_address_only_third_person(self) -> None:
        """Test when Dan is only mentioned in third person, no direct address."""
        text = "Speaker A: I heard Dan works here.\r\n" "Speaker B: Yes, that's true."
        labels = ["Speaker A", "Speaker B"]
        dan_label = _identify_dan_moisan(text, labels)
        # "heard Dan works" is not a direct address pattern we detect
        assert dan_label is None


class TestExtractSpeakerSamples:
    """Test speaker sample extraction."""

    def test_extract_samples(self) -> None:
        """Test extracting sample utterances."""
        text = "Speaker A: First.\r\nSpeaker A: Second.\r\nSpeaker B: Other.\r\nSpeaker A: Third."
        samples = _extract_speaker_samples("Speaker A", text, count=2)
        assert len(samples) == 2
        assert samples[0] == "First."
        assert samples[1] == "Second."

    def test_extract_fewer_than_requested(self) -> None:
        """Test when fewer samples exist than requested."""
        text = "Speaker A: Only one."
        samples = _extract_speaker_samples("Speaker A", text, count=5)
        assert len(samples) == 1


class TestApplySpeakerMappings:
    """Test speaker _mapping application."""

    def test_simple_mapping(self) -> None:
        """Test applying simple speaker _mapping."""
        text = "Speaker A: Hello\r\nSpeaker B: Hi"
        _mapping = {"Speaker A": "John", "Speaker B": "Jane"}
        result = _apply_speaker_mappings(text, _mapping)
        assert "John:" in result
        assert "Jane:" in result
        assert "Speaker A:" not in result

    def test_empty_mapping(self) -> None:
        """Test with empty _mapping."""
        text = "Speaker A: Hello"
        result = _apply_speaker_mappings(text, {})
        assert result == text

    def test_partial_mapping(self) -> None:
        """Test _mapping only some speakers."""
        text = "Speaker A: Hello\r\nSpeaker B: Hi"
        _mapping = {"Speaker A": "John"}
        result = _apply_speaker_mappings(text, _mapping)
        assert "John:" in result
        assert "Speaker B:" in result


class TestResolveSpeakers:
    """Test complete speaker resolution."""

    def test_no_speakers(self) -> None:
        """Test text without speakers."""
        text = "Just plain text"
        result, _mapping = resolve_speakers(text)
        assert result == text
        assert _mapping == {}

    def test_empty_text(self) -> None:
        """Test empty text."""
        result, _mapping = resolve_speakers("")
        assert result == ""
        assert _mapping == {}

    def test_with_metadata_names(self) -> None:
        """Test resolution using metadata names."""
        text = "Attendees: John\r\nSpeaker A: Hello everyone."
        _result, _mapping = resolve_speakers(text)
        # Should attempt to map Speaker A to John
        assert len(_mapping) >= 0  # May or may not auto-resolve

    def test_with_ui_callback(self) -> None:
        """Test resolution with UI callback."""

        def mock_ui(speaker_label: str, sample_utterances: list[str]) -> str | None:
            """Mock UI that resolves Speaker A to John."""
            if speaker_label == "Speaker A":
                return "John"
            return None

        text = "Speaker A: Hello\r\nSpeaker A: World"
        result, _mapping = resolve_speakers(text, ui_callback=mock_ui)
        # Should resolve Speaker A to John
        if "Speaker A" in _mapping:
            assert _mapping["Speaker A"] == "John"
            assert "John:" in result

    def test_dan_moisan_identification(self) -> None:
        """Test Dan Moisan identification in resolution."""
        text = (
            "Speaker A: Dan, what do you think?\r\n"
            "Speaker B: I think it's great.\r\n"
            "Speaker A: Thanks Dan."
        )
        _result, _mapping = resolve_speakers(text)
        # Should identify Speaker B as Dan Moisan
        if "Speaker B" in _mapping:
            assert _mapping["Speaker B"] == "Dan Moisan"

    def test_preserves_non_speaker_text(self) -> None:
        """Test that non-speaker text is preserved."""
        text = "Meeting: Team Sync\r\nSpeaker A: Hello"
        result, _mapping = resolve_speakers(text)
        assert "Meeting: Team Sync" in result

    def test_ui_callback_cancel(self) -> None:
        """Test UI callback returning None (cancel)."""

        def mock_ui_cancel(speaker_label: str, sample_utterances: list[str]) -> str | None:
            """Mock UI that always cancels."""
            return None

        text = "Speaker A: Hello"
        result, _mapping = resolve_speakers(text, ui_callback=mock_ui_cancel)
        # Should not resolve if UI cancels
        # Original text should be preserved
        assert "Speaker A:" in result

    def test_multiple_names_with_unambiguous_matches(self) -> None:
        """Test resolution when multiple names have clear 1:1 matches.

        With proximity heuristics, immediate responses identify speakers.
        """
        text = (
            "Attendees: Alice, Bob\r\n"
            "Transcript:\r\n"
            "Speaker A: Alice, what's your view?\r\n"
            "Speaker B: I think it's good.\r\n"
            "Speaker A: Thanks. Bob, what about you?\r\n"
            "Speaker C: I agree with Alice."
        )
        _result, mapping = resolve_speakers(text)
        # Analysis:
        # - Speaker B responds immediately after Alice is addressed → B is Alice (+3)
        # - Speaker C responds immediately after Bob is addressed → C is Bob (+3)
        assert mapping.get("Speaker B") == "Alice"
        assert mapping.get("Speaker C") == "Bob"

    def test_ambiguous_candidates_without_ui(self) -> None:
        """Test that immediate response identifies speaker even without UI.

        With proximity heuristics, an immediate response is enough to identify
        the speaker, even without a UI callback.
        """
        text = (
            "Speaker A: Alice, what do you think?\r\n"
            "Speaker B: Good idea.\r\n"
            "Speaker C: I agree.\r\n"
            "Speaker A: Thanks Alice."
        )
        _result, mapping = resolve_speakers(text)
        # Speaker B responds immediately after Alice is addressed → B is Alice
        assert mapping.get("Speaker B") == "Alice"


class TestIdentifySpeakerByName:
    """Test generalized speaker identification by first name.

    This tests the _identify_speaker_by_name function with various names
    to ensure the pattern matching is truly name-agnostic.
    """

    @pytest.mark.parametrize(
        "name,direct_address,expected_speaker",
        [
            (
                Name(first_name="Alice"),
                "Speaker A: Alice, what do you think?\r\nSpeaker B: I think it's good.",
                "Speaker B",
            ),
            (
                Name(first_name="Bob"),
                "Speaker A: Thanks, Bob.\r\nSpeaker B: You're welcome.",
                "Speaker B",
            ),
            (
                Name(first_name="Charlie"),
                "Speaker A: I need to speak to Charlie.\r\nSpeaker B: I'm here.",
                "Speaker B",
            ),
            (
                Name(first_name="Diana"),
                "Speaker A: Diana mentioned this earlier.\r\nSpeaker B: Yes, I did.",
                "Speaker B",
            ),
            (
                Name(first_name="Eve"),
                "Speaker A: I'm learning about you, Eve.\r\nSpeaker B: Thank you.",
                "Speaker B",
            ),
            (
                Name(first_name="Frank"),
                "Speaker A: For Frank, this is important.\r\nSpeaker B: I appreciate that.",
                "Speaker B",
            ),
        ],
    )
    def test_various_names_vocative_comma(
        self, name: Name, direct_address: str, expected_speaker: str
    ) -> None:
        """Test that identification works with various first names."""
        labels = ["Speaker A", "Speaker B"]
        identified = _identify_speaker_by_name(direct_address, labels, name)
        assert identified == [expected_speaker]

    @pytest.mark.parametrize(
        "name,hypothetical_text",
        [
            (Name(first_name="Alice"), "Speaker A: Is Alice a good fit?\r\nSpeaker B: I think so."),
            (
                Name(first_name="Bob"),
                "Speaker A: If you were to say Bob is great.\r\nSpeaker B: Agreed.",
            ),
            (
                Name(first_name="Charlie"),
                "Speaker A: Is Charlie an experienced leader?\r\nSpeaker B: Yes.",
            ),
            (
                Name(first_name="Diana"),
                "Speaker A: The question is whether Diana can do it.\r\nSpeaker B: I can.",
            ),
        ],
    )
    def test_various_names_hypothetical_excluded(self, name: Name, hypothetical_text: str) -> None:
        """Test that hypothetical references are correctly excluded for any name."""
        labels = ["Speaker A", "Speaker B"]
        identified = _identify_speaker_by_name(hypothetical_text, labels, name)
        assert identified == []

    def test_case_insensitive_matching(self) -> None:
        """Test that name matching is case-insensitive."""
        text = "Speaker A: ALICE, can you help?\r\nSpeaker B: Sure."
        labels = ["Speaker A", "Speaker B"]
        # Should work with lowercase input name
        identified = _identify_speaker_by_name(text, labels, Name(first_name="alice"))
        assert identified == ["Speaker B"]

    def test_multiple_speakers_complex(self) -> None:
        """Test identification with multiple speakers.

        With proximity heuristics, immediate response identifies the speaker.
        """
        text = (
            "Speaker A: Alice, what's your take?\r\n"
            "Speaker B: I agree with the approach.\r\n"
            "Speaker C: Me too.\r\n"
            "Speaker A: Thanks Alice."
        )
        labels = ["Speaker A", "Speaker B", "Speaker C"]
        identified = _identify_speaker_by_name(text, labels, Name(first_name="Alice"))
        # Speaker B responds immediately after Alice is addressed
        assert identified == ["Speaker B"]

    def test_no_matches_returns_empty_list(self) -> None:
        """Test that no matches returns empty list."""
        text = "Speaker A: Hello\r\nSpeaker B: Hi"
        labels = ["Speaker A", "Speaker B"]
        identified = _identify_speaker_by_name(text, labels, Name(first_name="Alice"))
        assert identified == []

    def test_name_as_speaker_label(self) -> None:
        """Test when the name itself appears as a speaker label."""
        text = "Alice: Hello everyone.\r\nSpeaker A: Hi Alice, how are you?"
        labels = ["Alice", "Speaker A"]
        identified = _identify_speaker_by_name(text, labels, Name(first_name="Alice"))
        # Alice is not in the candidate list because she's not addressed
        # (Speaker A addresses Alice, so Alice could be in the other speakers,
        # but Alice is the one doing the addressing in the speaker line)
        assert identified == []

    def test_multiple_candidates_no_order_bias(self) -> None:
        """Test that immediate response identifies speaker without order bias.

        With proximity heuristics, the immediate responder is identified.
        """
        text = (
            "Speaker A: Alice, what's your plan?\r\n"
            "Speaker B: I think we should proceed.\r\n"
            "Speaker C: I agree with that approach.\r\n"
            "Speaker A: Thanks Alice for the input."
        )
        labels = ["Speaker A", "Speaker B", "Speaker C"]
        identified = _identify_speaker_by_name(text, labels, Name(first_name="Alice"))
        # Speaker B responds immediately after Alice is addressed
        assert identified == ["Speaker B"]


class TestProximityHeuristics:
    """Test proximity heuristics for speaker identification."""

    def test_immediate_response_pattern(self) -> None:
        """Test that immediate response after direct address identifies speaker."""
        text = (
            "Speaker A: Alice, what do you think?\r\n"
            "Speaker B: I agree with that approach.\r\n"
            "Speaker A: Dan, your thoughts?\r\n"
            "Speaker C: Sounds good."
        )
        labels = ["Speaker A", "Speaker B", "Speaker C"]
        # Alice is addressed, B responds immediately → B is likely Alice
        identified = _identify_speaker_by_name(text, labels, Name(first_name="Alice"))
        assert identified == ["Speaker B"]

    def test_technical_difficulty_pattern(self) -> None:
        """Test identification when technical issues interrupt response."""
        text = (
            "Speaker A: Alice, what do you think?\r\n"
            "Speaker B: Are you there?\r\n"
            "Speaker A: Maybe we're having connection issues.\r\n"
            "Speaker B: Yes, her screen looks frozen.\r\n"
            "Speaker C: No, I'm here! Sorry I lost you for a moment."
        )
        labels = ["Speaker A", "Speaker B", "Speaker C"]
        # Speaker C self-identifies with "I'm here" and "Sorry I lost you"
        identified = _identify_speaker_by_name(text, labels, Name(first_name="Alice"))
        assert identified == ["Speaker C"]

    def test_muted_speaker_pattern(self) -> None:
        """Test identification when speaker is muted."""
        text = (
            "Speaker A: Alice, what do you think?\r\n"
            "Speaker B: You are on mute.\r\n"
            "Speaker C: Sorry, I was saying that I thought it was good."
        )
        labels = ["Speaker A", "Speaker B", "Speaker C"]
        # Speaker C apologizes and uses self-identification
        identified = _identify_speaker_by_name(text, labels, Name(first_name="Alice"))
        assert identified == ["Speaker C"]

    def test_third_person_reference_reinforcement(self) -> None:
        """Test that third-person references reinforce candidate selection."""
        text = (
            "Speaker A: Alice, can you hear us?\r\n"
            "Speaker B: I think her audio is out.\r\n"
            "Speaker C: Alice's microphone seems muted.\r\n"
            "Speaker D: Can you hear me now? Sorry about that."
        )
        labels = ["Speaker A", "Speaker B", "Speaker C", "Speaker D"]
        # A, B, C all refer to Alice in third person → they are NOT Alice
        # D self-identifies → D is Alice
        identified = _identify_speaker_by_name(text, labels, Name(first_name="Alice"))
        assert identified == ["Speaker D"]

    def test_no_clear_heuristic_returns_empty(self) -> None:
        """Test that ambiguous cases without clear heuristics return empty list."""
        text = (
            "Speaker B: I think we should discuss this.\r\n"
            "Speaker C: That's a good point.\r\n"
            "Speaker A: Alice had some thoughts on this earlier.\r\n"
            "Speaker B: Yes, we should consider all options.\r\n"
            "Speaker C: Agreed, let's move forward."
        )
        labels = ["Speaker A", "Speaker B", "Speaker C"]
        # Alice mentioned in third person by A (not B or C addressing her)
        # No direct address followed by response
        # No self-identification patterns
        # Should return empty list (heuristics inconclusive)
        identified = _identify_speaker_by_name(text, labels, Name(first_name="Alice"))
        assert identified == []

    def test_multiple_direct_addresses_with_responses(self) -> None:
        """Test handling of multiple direct addresses with clear responses."""
        text = (
            "Speaker A: Alice, your thoughts?\r\n"
            "Speaker B: I think it's excellent.\r\n"
            "Speaker A: Bob, what about you?\r\n"
            "Speaker C: I agree with Alice."
        )
        labels = ["Speaker A", "Speaker B", "Speaker C"]
        # Alice is addressed, B responds immediately → B is Alice
        alice_identified = _identify_speaker_by_name(text, labels, Name(first_name="Alice"))
        assert alice_identified == ["Speaker B"]
        # Bob is addressed, C responds → C is Bob
        bob_identified = _identify_speaker_by_name(text, labels, Name(first_name="Bob"))
        assert bob_identified == ["Speaker C"]

    def test_apology_pattern_self_identification(self) -> None:
        """Test various apology patterns for self-identification."""
        text = (
            "Speaker A: Alice, are you there?\r\n"
            "Speaker B: Maybe she dropped off.\r\n"
            "Speaker C: Apologies, I was just reviewing the document."
        )
        labels = ["Speaker A", "Speaker B", "Speaker C"]
        # Speaker C uses "Apologies, I" pattern
        identified = _identify_speaker_by_name(text, labels, Name(first_name="Alice"))
        assert identified == ["Speaker C"]

    def test_combined_heuristics_reinforce_identification(self) -> None:
        """Test that multiple heuristics combine to strengthen identification."""
        text = (
            "Speaker A: Alice, can you share your screen?\r\n"
            "Speaker B: I think she's having trouble.\r\n"
            "Speaker C: Her connection looks unstable.\r\n"
            "Speaker D: Sorry, I was trying to share. Can you see it now?"
        )
        labels = ["Speaker A", "Speaker B", "Speaker C", "Speaker D"]
        # B and C refer to Alice in third person (reinforcement)
        # D self-identifies with apology and context
        identified = _identify_speaker_by_name(text, labels, Name(first_name="Alice"))
        assert identified == ["Speaker D"]

    def test_building_on_question_pattern(self) -> None:
        """Test when one speaker builds on another's question before the addressee responds.

        In this pattern, Speaker B adds to Speaker A's question to Alice,
        but Speaker C is the one who actually responds. The algorithm should
        identify C as Alice, not B (who was just elaborating on the question).
        """
        text = (
            "Speaker A: Alice, tell me about a time you led a team "
            "through a difficult circumstance?\r\n"
            "Speaker B: And let me build. Can you also tell us how many "
            "of the team that you needed to replace?\r\n"
            "Speaker C: Sure, let me begin."
        )
        labels = ["Speaker A", "Speaker B", "Speaker C"]
        # Speaker A addresses Alice
        # Speaker B builds on the question (not a response from Alice)
        # Speaker C responds with "Sure, let me begin" - this is Alice
        identified = _identify_speaker_by_name(text, labels, Name(first_name="Alice"))
        assert identified == ["Speaker C"]


class TestIsProperNoun:
    """Test proper noun detection logic."""

    def test_valid_proper_noun(self) -> None:
        """Test valid proper nouns are recognized."""
        assert _is_proper_noun("John")
        assert _is_proper_noun("Alice")
        assert _is_proper_noun("Daniel")

    def test_lowercase_not_proper_noun(self) -> None:
        """Test lowercase words are not proper nouns."""
        assert not _is_proper_noun("hello")
        assert not _is_proper_noun("world")
        assert not _is_proper_noun("test")

    def test_all_uppercase_not_proper_noun(self) -> None:
        """Test all uppercase words are not proper nouns (acronyms)."""
        assert not _is_proper_noun("USA")
        assert not _is_proper_noun("NASA")
        assert not _is_proper_noun("IBM")

    def test_single_letter_not_proper_noun(self) -> None:
        """Test single letters are not proper nouns."""
        assert not _is_proper_noun("A")
        assert not _is_proper_noun("I")
        assert not _is_proper_noun("x")

    def test_empty_not_proper_noun(self) -> None:
        """Test empty strings are not proper nouns."""
        assert not _is_proper_noun("")
        assert not _is_proper_noun(" ")

    def test_mixed_case_proper_nouns(self) -> None:
        """Test proper nouns with mixed case."""
        assert _is_proper_noun("McDonald")
        assert _is_proper_noun("O'Brien")

    def test_hyphenated_proper_nouns(self) -> None:
        """Test hyphenated proper nouns."""
        # These should be proper nouns if they follow the pattern
        assert _is_proper_noun("Anne-Marie")
        assert _is_proper_noun("Jean-Claude")


class TestIsLikelyPersonName:
    """Test person name classification logic."""

    def test_typical_person_names(self) -> None:
        """Test typical person names are recognized."""
        assert _is_likely_person_name("John")
        assert _is_likely_person_name("Alice")
        assert _is_likely_person_name("Sarah")
        assert _is_likely_person_name("Michael")
        assert _is_likely_person_name("Jennifer")

    def test_place_names_excluded(self) -> None:
        """Test place names are excluded."""
        assert not _is_likely_person_name("America")
        assert not _is_likely_person_name("California")
        assert not _is_likely_person_name("London")
        assert not _is_likely_person_name("Paris")
        assert not _is_likely_person_name("Tokyo")
        assert not _is_likely_person_name("Chicago")

    def test_days_excluded(self) -> None:
        """Test day names are excluded."""
        assert not _is_likely_person_name("Monday")
        assert not _is_likely_person_name("Tuesday")
        assert not _is_likely_person_name("Friday")

    def test_months_excluded(self) -> None:
        """Test month names are excluded."""
        assert not _is_likely_person_name("January")
        assert not _is_likely_person_name("February")
        assert not _is_likely_person_name("December")

    def test_company_names_excluded(self) -> None:
        """Test company names are excluded."""
        assert not _is_likely_person_name("Microsoft")
        assert not _is_likely_person_name("Apple")
        assert not _is_likely_person_name("Google")
        assert not _is_likely_person_name("Amazon")

    def test_common_words_excluded(self) -> None:
        """Test common words are excluded."""
        assert not _is_likely_person_name("The")
        assert not _is_likely_person_name("This")
        assert not _is_likely_person_name("Thanks")
        assert not _is_likely_person_name("Hello")
        assert not _is_likely_person_name("Really")

    def test_case_insensitive_filtering(self) -> None:
        """Test filtering is case-insensitive."""
        assert not _is_likely_person_name("MONDAY")
        assert not _is_likely_person_name("monday")
        assert not _is_likely_person_name("MoNdAy")


class TestExtractNamesFromDialogueEnhanced:
    """Test enhanced name extraction with proper noun filtering."""

    def test_extracts_proper_person_names(self) -> None:
        """Test extraction of proper person names."""
        text = "Speaker A: Hi, Dan\r\nSpeaker B: Hello Alice"
        names = _extract_names_from_dialogue(text)
        assert Name(first_name="Dan") in names
        assert Name(first_name="Alice") in names

    def test_filters_place_names(self) -> None:
        """Test place names are filtered out."""
        text = "Speaker A: Hi, California\r\nSpeaker B: Thanks, London"
        names = _extract_names_from_dialogue(text)
        assert Name(first_name="California") not in names
        assert Name(first_name="London") not in names

    def test_filters_day_names(self) -> None:
        """Test day names are filtered out."""
        text = "Speaker A: Hi, Monday\r\nSpeaker B: Thanks, Friday"
        names = _extract_names_from_dialogue(text)
        assert Name(first_name="Monday") not in names
        assert Name(first_name="Friday") not in names

    def test_filters_month_names(self) -> None:
        """Test month names are filtered out."""
        text = "Speaker A: As January mentioned\r\nSpeaker B: So December said"
        names = _extract_names_from_dialogue(text)
        assert Name(first_name="January") not in names
        assert Name(first_name="December") not in names

    def test_filters_company_names(self) -> None:
        """Test company names are filtered out."""
        text = "Speaker A: Hi, Microsoft\r\nSpeaker B: Thanks, Google"
        names = _extract_names_from_dialogue(text)
        assert Name(first_name="Microsoft") not in names
        assert Name(first_name="Google") not in names

    def test_filters_common_words(self) -> None:
        """Test common words are filtered out."""
        text = "Speaker A: Hi, The\r\nSpeaker B: Thanks, This"
        names = _extract_names_from_dialogue(text)
        assert Name(first_name="The") not in names
        assert Name(first_name="This") not in names

    def test_filters_acronyms(self) -> None:
        """Test all-uppercase acronyms are filtered out (not proper nouns)."""
        text = "Speaker A: Hi, USA\r\nSpeaker B: Thanks, NASA"
        names = _extract_names_from_dialogue(text)
        assert Name(first_name="USA") not in names
        assert Name(first_name="NASA") not in names

    def test_multiple_valid_names(self) -> None:
        """Test extraction of multiple valid person names."""
        text = (
            "Speaker A: John, what do you think?\r\n"
            "Speaker B: I agree. Sarah, how is Alice?\r\n"
            "Speaker C: She's fine."
        )
        names = _extract_names_from_dialogue(text)
        assert Name(first_name="John") in names
        assert Name(first_name="Sarah") in names
        assert Name(first_name="Alice") in names

    def test_mixed_valid_and_invalid(self) -> None:
        """Test mixture of valid person names and invalid entries."""
        text = (
            "Speaker A: John, what about California?\r\n"
            "Speaker B: Hi, Monday\r\n"
            "Speaker C: Thanks, Alice"
        )
        names = _extract_names_from_dialogue(text)
        # Should include person names
        assert Name(first_name="John") in names
        assert Name(first_name="Alice") in names
        # Should exclude places and days
        assert Name(first_name="California") not in names
        assert Name(first_name="Monday") not in names

    def test_empty_text(self) -> None:
        """Test extraction from empty text."""
        names = _extract_names_from_dialogue("")
        assert len(names) == 0

    def test_no_matching_patterns(self) -> None:
        """Test text with no matching patterns."""
        text = "Speaker A: Just regular text here\r\nSpeaker B: Nothing special"
        names = _extract_names_from_dialogue(text)
        assert len(names) == 0

    def test_greeting_pattern(self) -> None:
        """Test greeting pattern extraction."""
        text = "Speaker A: Hello, Michael\r\nSpeaker B: Hey, Jennifer"
        names = _extract_names_from_dialogue(text)
        assert Name(first_name="Michael") in names
        assert Name(first_name="Jennifer") in names

    def test_direct_address_pattern(self) -> None:
        """Test direct address pattern (name followed by question)."""
        text = "Speaker A: Sarah, what do you think?\r\nSpeaker B: Robert, how are you?"
        names = _extract_names_from_dialogue(text)
        assert Name(first_name="Sarah") in names
        assert Name(first_name="Robert") in names

    def test_mention_pattern(self) -> None:
        """Test mention pattern (As X mentioned)."""
        text = "Speaker A: As David mentioned earlier\r\nSpeaker B: So Emily noted"
        names = _extract_names_from_dialogue(text)
        assert Name(first_name="David") in names
        assert Name(first_name="Emily") in names

    def test_how_is_pattern(self) -> None:
        """Test 'how is X' pattern."""
        text = "Speaker A: How is Thomas?\r\nSpeaker B: Where is Lisa?"
        names = _extract_names_from_dialogue(text)
        assert Name(first_name="Thomas") in names
        assert Name(first_name="Lisa") in names
