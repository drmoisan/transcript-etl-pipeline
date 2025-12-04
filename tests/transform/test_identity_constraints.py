"""Unit tests for identity constraint extraction.

Tests the extraction of speaker identity information from sentences,
including self-identifications and direct addresses to others.
"""

import pytest

from transcript_etl_pipeline.transform.identity_constraints import (
    IdentityConstraint,
    detect_addresses_to_person,
    detect_self_identification,
    extract_identity_constraints,
)


class TestDetectSelfIdentification:
    """Tests for detecting self-identification patterns."""

    def test_im_pattern_simple(self) -> None:
        """Test 'I'm [Name]' pattern detection."""
        sentence = "You both know me. I'm Peter Parker and I work here."
        result = detect_self_identification(sentence)
        assert result == "Peter Parker"

    def test_i_am_pattern(self) -> None:
        """Test 'I am [Name]' pattern detection."""
        sentence = "Hello everyone, I am Fred Flintstone from accounting."
        result = detect_self_identification(sentence)
        assert result == "Fred Flintstone"

    def test_my_name_is_pattern(self) -> None:
        """Test 'My name is [Name]' pattern detection."""
        sentence = "My name is Alice Johnson and I'll be your host today."
        result = detect_self_identification(sentence)
        assert result == "Alice Johnson"

    def test_this_is_pattern(self) -> None:
        """Test 'This is [Name]' pattern (phone/intro context)."""
        sentence = "Hi, this is Bob Smith calling about the meeting."
        result = detect_self_identification(sentence)
        assert result == "Bob Smith"

    def test_single_name(self) -> None:
        """Test self-identification with single name."""
        sentence = "I'm Frank and I appreciate your time."
        result = detect_self_identification(sentence)
        assert result == "Frank"

    def test_no_self_identification(self) -> None:
        """Test sentence without self-identification returns None."""
        sentence = "What do you think about the proposal?"
        result = detect_self_identification(sentence)
        assert result is None

    def test_lowercase_not_matched(self) -> None:
        """Test that lowercase names are not matched (likely not names)."""
        sentence = "I'm working on the project today."
        result = detect_self_identification(sentence)
        assert result is None

    def test_case_insensitive_pattern(self) -> None:
        """Test that pattern matching is case-insensitive for keywords."""
        sentence = "I'M Sarah Williams and I'll help you."
        result = detect_self_identification(sentence)
        assert result == "Sarah Williams"


class TestDetectAddressesToPerson:
    """Tests for detecting when someone is addressed by name."""

    def test_thanks_with_comma(self) -> None:
        """Test 'Thanks, Name' pattern."""
        sentence = "Thanks, Frank, that was helpful."
        result = detect_addresses_to_person(sentence)
        assert "Frank" in result

    def test_thank_you_pattern(self) -> None:
        """Test 'Thank you Name' pattern."""
        sentence = "Thank you Alice for the clarification."
        result = detect_addresses_to_person(sentence)
        assert "Alice" in result

    def test_vocative_at_start(self) -> None:
        """Test 'Name, what...' pattern (vocative at start)."""
        sentence = "Peter, what do you think about this approach?"
        result = detect_addresses_to_person(sentence)
        assert "Peter" in result

    def test_vocative_at_end(self) -> None:
        """Test '..., Name.' pattern (vocative at end)."""
        sentence = "I have a question for you, Dan."
        result = detect_addresses_to_person(sentence)
        assert "Dan" in result

    def test_name_with_imperative(self) -> None:
        """Test 'Name tell/explain/show...' patterns."""
        sentence = "Alice explain how this works."
        result = detect_addresses_to_person(sentence)
        assert "Alice" in result

    def test_question_about_person(self) -> None:
        """Test questions about someone (e.g., 'Can Name...').

        Note: This pattern is intentionally NOT included in addresses_to_person
        as it's more of a "mentions" pattern than a direct address. The conservative
        approach is to only detect clear vocative or attributive patterns.
        """
        sentence = "Can Frank join us for the call?"
        result = detect_addresses_to_person(sentence)
        # This should NOT be detected as a direct address in our conservative implementation
        assert "Frank" not in result

    def test_attribution_pattern(self) -> None:
        """Test 'Name mentioned/said...' patterns."""
        sentence = "Peter mentioned this in the last meeting."
        result = detect_addresses_to_person(sentence)
        assert "Peter" in result

    def test_third_person_question_excluded(self) -> None:
        """Test that 'is Name a...' patterns are excluded."""
        sentence = "Is Dan a manager or a developer?"
        result = detect_addresses_to_person(sentence)
        assert "Dan" not in result

    def test_hypothetical_excluded(self) -> None:
        """Test that hypothetical references are excluded."""
        sentence = "If you were to say Alice was correct, would that help?"
        result = detect_addresses_to_person(sentence)
        assert "Alice" not in result

    def test_is_name_question_excluded(self) -> None:
        """Test that 'Is Name...' questions are excluded."""
        sentence = "Is Frank available for a quick chat?"
        result = detect_addresses_to_person(sentence)
        # Note: This should be excluded as it's asking ABOUT Frank, not TO Frank
        # Our implementation correctly excludes this pattern
        assert "Frank" not in result

    def test_multiple_names_addressed(self) -> None:
        """Test sentence addressing multiple people."""
        sentence = "Thanks, Alice and Bob, for your input."
        result = detect_addresses_to_person(sentence)
        assert "Alice" in result
        assert "Bob" in result

    def test_no_names_in_sentence(self) -> None:
        """Test sentence without any names returns empty list."""
        sentence = "What do you think about the proposal?"
        result = detect_addresses_to_person(sentence)
        assert result == []

    def test_full_name_addressed(self) -> None:
        """Test addressing someone by full name."""
        sentence = "Thank you, Peter Parker, for the update."
        result = detect_addresses_to_person(sentence)
        assert "Peter Parker" in result

    def test_thanks_followed_by_name_extracts_name(self) -> None:
        """Test extracting name after excluded word in phrase like 'Thanks Frank'."""
        # "Thanks Frank" should extract "Frank" as addressed name
        sentence = "Thanks Frank for helping us today."
        result = detect_addresses_to_person(sentence)
        assert "Frank" in result

    def test_hello_followed_by_name_extracts_name(self) -> None:
        """Test extracting name after 'Hello' prefix."""
        sentence = "Hello Sarah, nice to meet you."
        result = detect_addresses_to_person(sentence)
        # "Sarah" should be detected from vocative comma pattern
        assert "Sarah" in result

    def test_short_single_char_name_excluded(self) -> None:
        """Test that single-character tokens are not treated as names."""
        # Single-char tokens like "I" should be excluded (len < 2)
        sentence = "I think we should proceed."
        result = detect_addresses_to_person(sentence)
        assert result == []

    def test_standalone_name_question_excluded(self) -> None:
        """Test standalone name as question is excluded (e.g., 'Fred?')."""
        sentence = "Fred?"
        result = detect_addresses_to_person(sentence)
        # A standalone question like "Fred?" is not direct address
        assert "Fred" not in result

    def test_standalone_name_question_with_context_excluded(self) -> None:
        """Test standalone name question with context is excluded."""
        sentence = "Wait, Fred?"
        result = detect_addresses_to_person(sentence)
        # Asking "Fred?" is a question about the person, not to them
        assert "Fred" not in result

    def test_is_name_article_noun_excluded(self) -> None:
        """Test 'is Name a/an/the [noun]' pattern is excluded."""
        sentence = "Is Dan a leader in this group?"
        result = detect_addresses_to_person(sentence)
        # "Is Dan a..." asks ABOUT Dan, not TO Dan
        assert "Dan" not in result

    def test_is_name_an_expert_excluded(self) -> None:
        """Test 'is Name an [noun]' pattern is excluded."""
        sentence = "Is Alice an expert in this field?"
        result = detect_addresses_to_person(sentence)
        # "Is Alice an..." asks ABOUT Alice, not TO Alice
        assert "Alice" not in result

    def test_is_name_the_person_excluded(self) -> None:
        """Test 'is Name the [noun]' pattern is excluded."""
        sentence = "Is Bob the manager here?"
        result = detect_addresses_to_person(sentence)
        # "Is Bob the..." asks ABOUT Bob, not TO Bob
        assert "Bob" not in result

    def test_mid_sentence_is_name_article_excluded(self) -> None:
        """Test mid-sentence 'is Name a/an/the' pattern is excluded."""
        # Tests the third-person question exclusion: 'is Name a/an/the' mid-sentence
        sentence = "And is Dan a good choice for this role?"
        result = detect_addresses_to_person(sentence)
        # "is Dan a..." mid-sentence asks ABOUT Dan, not TO Dan
        assert "Dan" not in result

    def test_mid_sentence_is_name_an_excluded(self) -> None:
        """Test mid-sentence 'is Name an' pattern is excluded."""
        sentence = "I wonder, is Charlie an expert here?"
        result = detect_addresses_to_person(sentence)
        # "is Charlie an..." mid-sentence asks ABOUT Charlie, not TO Charlie
        assert "Charlie" not in result

    def test_mid_sentence_is_name_the_excluded(self) -> None:
        """Test mid-sentence 'is Name the' pattern is excluded."""
        sentence = "But is Sarah the right person for this?"
        result = detect_addresses_to_person(sentence)
        # "is Sarah the..." mid-sentence asks ABOUT Sarah, not TO Sarah
        assert "Sarah" not in result


class TestExtractIdentityConstraints:
    """Tests for extracting all identity constraints from sentences."""

    def test_self_identification_constraint(self) -> None:
        """Test extraction of self-identification constraint."""
        sentences = [
            "Hello everyone.",
            "I'm Peter Parker and I work in the lab.",
            "What brings you here today?",
        ]
        constraints = extract_identity_constraints(sentences)

        # Find the self-identification constraint
        self_id = [c for c in constraints if c.constraint_type == "self_identification"]
        assert len(self_id) == 1
        assert self_id[0].sentence_idx == 1
        assert self_id[0].name == "Peter Parker"

    def test_addresses_other_constraint(self) -> None:
        """Test extraction of addresses-other constraint."""
        sentences = [
            "Hello everyone.",
            "Thanks, Frank, for organizing this.",
            "What's the agenda?",
        ]
        constraints = extract_identity_constraints(sentences)

        # Find the addresses-other constraint
        addresses = [c for c in constraints if c.constraint_type == "addresses_other"]
        assert len(addresses) == 1
        assert addresses[0].sentence_idx == 1
        assert addresses[0].name == "Frank"

    def test_multiple_constraints_same_sentence(self) -> None:
        """Test sentence with both self-identification and addressing another.

        Note: When a sentence contains self-identification, address detection
        is skipped for that sentence because the constraint that matters is
        the self-identification (we already know who the speaker IS).
        """
        # Self-identification sentence - address detection is skipped
        sentences = [
            "I'm Alice and I want to thank you, Bob, for your help.",
        ]
        constraints = extract_identity_constraints(sentences)

        self_ids = [c for c in constraints if c.constraint_type == "self_identification"]
        addresses = [c for c in constraints if c.constraint_type == "addresses_other"]

        # Only self-identification is extracted (address detection skipped)
        assert len(self_ids) == 1
        assert self_ids[0].name == "Alice"
        assert len(addresses) == 0  # Skipped because sentence has self-ID

        # For a sentence without self-ID, address detection works normally
        sentences2 = [
            "Thank you, Bob, for your help.",
        ]
        constraints2 = extract_identity_constraints(sentences2)
        addresses2 = [c for c in constraints2 if c.constraint_type == "addresses_other"]
        assert len(addresses2) == 1
        assert addresses2[0].name == "Bob"

    def test_three_speaker_dialogue(self) -> None:
        """Test extraction from Peter Parker/Frank Oz/Fred Flintstone dialogue."""
        sentences = [
            "Hello everyone.",
            "Good morning.",
            "You both know me.",
            "I'm Peter Parker and I work in the lab.",
            "Thanks, Frank, for organizing this.",
            "No problem.",
            "I'm Frank Oz.",
            "Peter, what do you think?",
            "I agree with Frank.",
            "I'm Fred Flintstone.",
            "Fred, welcome to the team.",
        ]
        constraints = extract_identity_constraints(sentences)

        # Expected constraints:
        # Sentence 3: "I'm Peter Parker" → self_identification
        # Sentence 4: "Thanks, Frank" → addresses_other
        # Sentence 6: "I'm Frank Oz" → self_identification
        # Sentence 7: "Peter, what..." → addresses_other
        # Sentence 8: "...with Frank" → addresses_other (possibly)
        # Sentence 9: "I'm Fred Flintstone" → self_identification
        # Sentence 10: "Fred, welcome" → addresses_other

        self_ids = [c for c in constraints if c.constraint_type == "self_identification"]
        assert len(self_ids) == 3
        assert any(c.name == "Peter Parker" and c.sentence_idx == 3 for c in self_ids)
        assert any(c.name == "Frank Oz" and c.sentence_idx == 6 for c in self_ids)
        assert any(c.name == "Fred Flintstone" and c.sentence_idx == 9 for c in self_ids)

        addresses = [c for c in constraints if c.constraint_type == "addresses_other"]
        assert any(c.name == "Frank" and c.sentence_idx == 4 for c in addresses)
        assert any(c.name == "Peter" and c.sentence_idx == 7 for c in addresses)
        assert any(c.name == "Fred" and c.sentence_idx == 10 for c in addresses)

    def test_no_constraints(self) -> None:
        """Test sentences without any identity constraints."""
        sentences = [
            "What do you think?",
            "I agree with that approach.",
            "Let's move forward.",
        ]
        constraints = extract_identity_constraints(sentences)
        assert constraints == []

    def test_empty_input(self) -> None:
        """Test empty sentence list."""
        constraints = extract_identity_constraints([])
        assert constraints == []


class TestIdentityConstraintDataclass:
    """Tests for IdentityConstraint dataclass validation."""

    def test_valid_constraint(self) -> None:
        """Test creating a valid constraint."""
        constraint = IdentityConstraint(
            sentence_idx=5, constraint_type="self_identification", name="Peter Parker"
        )
        assert constraint.sentence_idx == 5
        assert constraint.constraint_type == "self_identification"
        assert constraint.name == "Peter Parker"

    def test_negative_index_raises_error(self) -> None:
        """Test that negative sentence index raises error."""
        with pytest.raises(ValueError, match="sentence_idx must be non-negative"):
            IdentityConstraint(sentence_idx=-1, constraint_type="self_identification", name="Alice")

    def test_empty_name_raises_error(self) -> None:
        """Test that empty name raises error."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            IdentityConstraint(sentence_idx=0, constraint_type="self_identification", name="")

    def test_whitespace_only_name_raises_error(self) -> None:
        """Test that whitespace-only name raises error."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            IdentityConstraint(sentence_idx=0, constraint_type="self_identification", name="   ")

    def test_immutability(self) -> None:
        """Test that IdentityConstraint is immutable (frozen dataclass)."""
        constraint = IdentityConstraint(
            sentence_idx=5, constraint_type="self_identification", name="Peter"
        )
        with pytest.raises((AttributeError, Exception)):
            constraint.sentence_idx = 10  # type: ignore[misc]

    def test_equality(self) -> None:
        """Test constraint equality comparison."""
        c1 = IdentityConstraint(sentence_idx=5, constraint_type="self_identification", name="Peter")
        c2 = IdentityConstraint(sentence_idx=5, constraint_type="self_identification", name="Peter")
        c3 = IdentityConstraint(sentence_idx=6, constraint_type="self_identification", name="Peter")

        assert c1 == c2
        assert c1 != c3
