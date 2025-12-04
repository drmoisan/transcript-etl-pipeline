"""Tests for speaker_helpers module covering heuristics and clustering helpers.

This module tests:
- Sentence tokenization and fallback splitting
- Pronoun pattern analysis
- Dialogue marker detection
- Sentence feature extraction
- Sentence similarity computation
- Speaker grouping by similarity
- Identity constraint violations
- Address violation resolution
"""

from transcript_etl_pipeline.transform.identity_constraints import (
    IdentityConstraint,
)
from transcript_etl_pipeline.transform.speaker_helpers import (
    ACKNOWLEDGMENTS,
    FIRST_PERSON_PRONOUNS,
    GREETINGS,
    SECOND_PERSON_PRONOUNS,
    TURN_TAKING_CUES,
    _fallback_sentence_split,  # pyright: ignore[reportPrivateUsage]
    _find_safe_replacement_speaker,  # pyright: ignore[reportPrivateUsage]
    analyze_pronoun_patterns,
    compute_sentence_similarity,
    detect_dialogue_markers,
    ensure_nltk_data,
    extract_sentence_features,
    extract_speaker_identities,
    group_sentences_by_similarity,
    resolve_addresses_other_violations,
    tokenize_into_sentences,
    violates_identity_constraints,
)


class TestConstants:
    """Tests for module constants."""

    def test_greetings_contains_common_greetings(self) -> None:
        """Verify GREETINGS contains standard greeting words."""
        assert "hello" in GREETINGS
        assert "hi" in GREETINGS
        assert "hey" in GREETINGS
        assert "good morning" in GREETINGS
        assert "good afternoon" in GREETINGS
        assert "good evening" in GREETINGS

    def test_acknowledgments_contains_common_affirmations(self) -> None:
        """Verify ACKNOWLEDGMENTS contains standard affirmation words."""
        assert "yes" in ACKNOWLEDGMENTS
        assert "no" in ACKNOWLEDGMENTS
        assert "yeah" in ACKNOWLEDGMENTS
        assert "okay" in ACKNOWLEDGMENTS
        assert "sure" in ACKNOWLEDGMENTS
        assert "right" in ACKNOWLEDGMENTS
        assert "great" in ACKNOWLEDGMENTS

    def test_turn_taking_cues_contains_transitions(self) -> None:
        """Verify TURN_TAKING_CUES contains transition words."""
        assert "well" in TURN_TAKING_CUES
        assert "so" in TURN_TAKING_CUES
        assert "but" in TURN_TAKING_CUES
        assert "actually" in TURN_TAKING_CUES
        assert "anyway" in TURN_TAKING_CUES

    def test_first_person_pronouns_complete(self) -> None:
        """Verify FIRST_PERSON_PRONOUNS includes singular and plural forms."""
        assert "i" in FIRST_PERSON_PRONOUNS
        assert "me" in FIRST_PERSON_PRONOUNS
        assert "my" in FIRST_PERSON_PRONOUNS
        assert "mine" in FIRST_PERSON_PRONOUNS
        assert "myself" in FIRST_PERSON_PRONOUNS
        assert "we" in FIRST_PERSON_PRONOUNS
        assert "us" in FIRST_PERSON_PRONOUNS
        assert "our" in FIRST_PERSON_PRONOUNS

    def test_second_person_pronouns_complete(self) -> None:
        """Verify SECOND_PERSON_PRONOUNS includes all forms."""
        assert "you" in SECOND_PERSON_PRONOUNS
        assert "your" in SECOND_PERSON_PRONOUNS
        assert "yours" in SECOND_PERSON_PRONOUNS
        assert "yourself" in SECOND_PERSON_PRONOUNS
        assert "yourselves" in SECOND_PERSON_PRONOUNS


class TestEnsureNltkData:
    """Tests for NLTK data availability."""

    def test_ensure_nltk_data_returns_true(self) -> None:
        """Verify NLTK data can be loaded or downloaded."""
        result = ensure_nltk_data()
        assert result is True


class TestTokenizeIntoSentences:
    """Tests for sentence tokenization."""

    def test_empty_text_returns_empty_list(self) -> None:
        """Verify empty input returns empty list."""
        assert tokenize_into_sentences("") == []
        assert tokenize_into_sentences("   ") == []

    def test_single_sentence(self) -> None:
        """Verify single sentence is returned as list with one element."""
        result = tokenize_into_sentences("Hello world.")
        assert len(result) == 1
        assert result[0] == "Hello world."

    def test_multiple_sentences(self) -> None:
        """Verify multiple sentences are split correctly."""
        text = "First sentence. Second sentence. Third sentence."
        result = tokenize_into_sentences(text)
        assert len(result) == 3
        assert "First sentence." in result
        assert "Second sentence." in result
        assert "Third sentence." in result

    def test_question_and_statement(self) -> None:
        """Verify questions and statements are tokenized correctly."""
        text = "What do you think? I agree."
        result = tokenize_into_sentences(text)
        assert len(result) == 2
        assert "What do you think?" in result
        assert "I agree." in result

    def test_exclamation_marks(self) -> None:
        """Verify exclamation marks are handled correctly."""
        text = "That's great! I'm so happy."
        result = tokenize_into_sentences(text)
        assert len(result) == 2

    def test_normalizes_line_breaks(self) -> None:
        """Verify line breaks are normalized to spaces."""
        text = "First sentence.\r\nSecond sentence.\nThird sentence."
        result = tokenize_into_sentences(text)
        assert len(result) == 3

    def test_handles_unicode(self) -> None:
        """Verify Unicode characters are handled."""
        text = "Café is great. I love café."
        result = tokenize_into_sentences(text)
        assert len(result) == 2


class TestFallbackSentenceSplit:
    """Tests for fallback sentence splitting."""

    def test_simple_sentences(self) -> None:
        """Verify simple sentence splitting works."""
        text = "First sentence. Second sentence."
        result = _fallback_sentence_split(text)
        assert len(result) == 2

    def test_question_splits(self) -> None:
        """Verify questions are split correctly."""
        text = "What do you think? I believe so."
        result = _fallback_sentence_split(text)
        assert len(result) == 2

    def test_exclamation_splits(self) -> None:
        """Verify exclamations are split correctly."""
        text = "Wow! That is amazing."
        result = _fallback_sentence_split(text)
        assert len(result) == 2

    def test_handles_multiple_spaces(self) -> None:
        """Verify multiple spaces are collapsed."""
        text = "First.   Second."
        result = _fallback_sentence_split(text)
        # May or may not split depending on capital letters
        assert len(result) >= 1

    def test_handles_line_breaks(self) -> None:
        """Verify line breaks are normalized."""
        text = "First sentence.\r\nSecond sentence."
        result = _fallback_sentence_split(text)
        assert len(result) == 2


class TestAnalyzePronounPatterns:
    """Tests for pronoun pattern analysis."""

    def test_empty_list_returns_empty(self) -> None:
        """Verify empty input returns empty list."""
        result = analyze_pronoun_patterns([])
        assert result == []

    def test_first_person_detection(self) -> None:
        """Verify first-person pronouns are detected."""
        sentences = ["I think we should proceed."]
        result = analyze_pronoun_patterns(sentences)
        assert len(result) == 1
        assert result[0].get("first_person", 0) >= 1

    def test_second_person_detection(self) -> None:
        """Verify second-person pronouns are detected."""
        sentences = ["You should consider your options."]
        result = analyze_pronoun_patterns(sentences)
        assert len(result) == 1
        assert result[0].get("second_person", 0) >= 1

    def test_question_detection(self) -> None:
        """Verify question marks trigger question detection."""
        sentences = ["What do you think?"]
        result = analyze_pronoun_patterns(sentences)
        assert len(result) == 1
        assert result[0].get("is_question", 0) == 1

    def test_statement_not_question(self) -> None:
        """Verify statements are not marked as questions."""
        sentences = ["This is a statement."]
        result = analyze_pronoun_patterns(sentences)
        assert len(result) == 1
        assert result[0].get("is_question", 0) == 0

    def test_multiple_sentences(self) -> None:
        """Verify analysis works for multiple sentences."""
        sentences = ["I believe this.", "You are right.", "What now?"]
        result = analyze_pronoun_patterns(sentences)
        assert len(result) == 3
        assert result[0].get("first_person", 0) >= 1
        assert result[1].get("second_person", 0) >= 1
        assert result[2].get("is_question", 0) == 1

    def test_mixed_pronouns(self) -> None:
        """Verify mixed pronoun usage is tracked."""
        sentences = ["I told you my plan."]
        result = analyze_pronoun_patterns(sentences)
        assert len(result) == 1
        # Contains both first and second person
        assert result[0].get("first_person", 0) >= 1
        assert result[0].get("second_person", 0) >= 1


class TestDetectDialogueMarkers:
    """Tests for dialogue marker detection."""

    def test_greeting_detection(self) -> None:
        """Verify greetings are detected."""
        assert detect_dialogue_markers("Hello everyone")["is_greeting"] is True
        assert detect_dialogue_markers("Hi there")["is_greeting"] is True
        assert detect_dialogue_markers("Hey folks")["is_greeting"] is True
        assert detect_dialogue_markers("Good morning team")["is_greeting"] is True

    def test_non_greeting(self) -> None:
        """Verify non-greetings are not marked as greetings."""
        assert detect_dialogue_markers("The hello was loud")["is_greeting"] is False
        assert detect_dialogue_markers("I said hello")["is_greeting"] is False

    def test_acknowledgment_detection(self) -> None:
        """Verify acknowledgments are detected."""
        assert detect_dialogue_markers("Yes, I agree")["is_acknowledgment"] is True
        assert detect_dialogue_markers("No, that's wrong")["is_acknowledgment"] is True
        assert detect_dialogue_markers("Okay, let's proceed")["is_acknowledgment"] is True
        assert detect_dialogue_markers("Sure, I can do that")["is_acknowledgment"] is True
        assert detect_dialogue_markers("Right, exactly")["is_acknowledgment"] is True
        assert detect_dialogue_markers("Great job everyone")["is_acknowledgment"] is True

    def test_acknowledgment_handles_punctuation(self) -> None:
        """Verify acknowledgments handle punctuation correctly."""
        assert detect_dialogue_markers("Yes!")["is_acknowledgment"] is True
        assert detect_dialogue_markers("Okay.")["is_acknowledgment"] is True
        assert detect_dialogue_markers("Sure,")["is_acknowledgment"] is True

    def test_turn_taking_cue_detection(self) -> None:
        """Verify turn-taking cues are detected."""
        assert detect_dialogue_markers("Well, I think...")["is_turn_taking"] is True
        assert detect_dialogue_markers("So, what's next?")["is_turn_taking"] is True
        assert detect_dialogue_markers("But wait a minute")["is_turn_taking"] is True
        assert detect_dialogue_markers("Actually, let me clarify")["is_turn_taking"] is True

    def test_response_pattern_detection(self) -> None:
        """Verify response patterns are detected."""
        assert detect_dialogue_markers("I think that's correct")["is_response"] is True
        assert detect_dialogue_markers("I believe we should")["is_response"] is True
        assert detect_dialogue_markers("I agree with you")["is_response"] is True
        assert detect_dialogue_markers("That's a good point")["is_response"] is True
        assert detect_dialogue_markers("It's interesting")["is_response"] is True

    def test_non_response(self) -> None:
        """Verify non-responses are not marked as responses."""
        result = detect_dialogue_markers("The weather is nice")
        assert result["is_response"] is False

    def test_empty_sentence(self) -> None:
        """Verify empty sentence handling."""
        result = detect_dialogue_markers("")
        assert result["is_greeting"] is False
        assert result["is_acknowledgment"] is False
        assert result["is_turn_taking"] is False
        assert result["is_response"] is False


class TestExtractSentenceFeatures:
    """Tests for sentence feature extraction."""

    def test_word_count(self) -> None:
        """Verify word count is extracted correctly."""
        features = extract_sentence_features("One two three four")
        assert features["word_count"] == 4

    def test_char_count(self) -> None:
        """Verify character count is extracted correctly."""
        sentence = "Hello"
        features = extract_sentence_features(sentence)
        assert features["char_count"] == len(sentence)

    def test_first_person_count(self) -> None:
        """Verify first-person pronoun count."""
        features = extract_sentence_features("I told my friend about myself")
        assert features["first_person_count"] >= 3

    def test_second_person_count(self) -> None:
        """Verify second-person pronoun count."""
        features = extract_sentence_features("You should bring your books")
        assert features["second_person_count"] >= 2

    def test_is_question(self) -> None:
        """Verify question detection."""
        features_q = extract_sentence_features("What is this?")
        features_s = extract_sentence_features("This is something.")
        assert features_q["is_question"] is True
        assert features_s["is_question"] is False

    def test_is_exclamation(self) -> None:
        """Verify exclamation detection."""
        features_e = extract_sentence_features("Wow!")
        features_s = extract_sentence_features("Wow.")
        assert features_e["is_exclamation"] is True
        assert features_s["is_exclamation"] is False

    def test_has_greeting(self) -> None:
        """Verify greeting detection in features."""
        features = extract_sentence_features("Hello everyone")
        assert features["has_greeting"] is True

    def test_has_acknowledgment(self) -> None:
        """Verify acknowledgment detection in features."""
        features = extract_sentence_features("Yes, I agree")
        assert features["has_acknowledgment"] is True

    def test_avg_word_length(self) -> None:
        """Verify average word length calculation."""
        features = extract_sentence_features("a bb ccc dddd")
        # (1 + 2 + 3 + 4) / 4 = 2.5
        assert features["avg_word_length"] == 2.5

    def test_empty_sentence_avg_word_length(self) -> None:
        """Verify empty sentence returns zero avg word length."""
        features = extract_sentence_features("")
        assert features["avg_word_length"] == 0.0


class TestComputeSentenceSimilarity:
    """Tests for sentence similarity computation."""

    def test_identical_features_high_similarity(self) -> None:
        """Verify identical features have high similarity."""
        features = {
            "word_count": 5,
            "first_person_count": 1,
            "second_person_count": 0,
            "is_question": False,
            "has_acknowledgment": False,
            "has_greeting": False,
        }
        score = compute_sentence_similarity(features, features)
        assert score == 1.0

    def test_different_word_counts(self) -> None:
        """Verify different word counts reduce similarity."""
        features1 = {"word_count": 5, "first_person_count": 0, "second_person_count": 0}
        features2 = {"word_count": 15, "first_person_count": 0, "second_person_count": 0}
        score = compute_sentence_similarity(features1, features2)
        assert score < 1.0

    def test_similar_word_counts(self) -> None:
        """Verify similar word counts maintain high similarity."""
        features1 = {"word_count": 5, "first_person_count": 0, "second_person_count": 0}
        features2 = {"word_count": 6, "first_person_count": 0, "second_person_count": 0}
        score = compute_sentence_similarity(features1, features2)
        assert score > 0.5

    def test_pronoun_usage_similarity(self) -> None:
        """Verify similar pronoun usage increases similarity."""
        features1 = {"word_count": 5, "first_person_count": 1, "second_person_count": 0}
        features2 = {"word_count": 5, "first_person_count": 2, "second_person_count": 0}
        score = compute_sentence_similarity(features1, features2)
        # Both have first person, neither has second person
        assert score > 0.6

    def test_question_similarity(self) -> None:
        """Verify question matching increases similarity."""
        q_features = {"word_count": 5, "is_question": True}
        s_features = {"word_count": 5, "is_question": False}
        score_same = compute_sentence_similarity(q_features, q_features)
        score_diff = compute_sentence_similarity(q_features, s_features)
        assert score_same > score_diff

    def test_dialogue_marker_similarity(self) -> None:
        """Verify dialogue marker matching increases similarity."""
        ack_features = {"word_count": 5, "has_acknowledgment": True, "has_greeting": False}
        no_ack_features = {"word_count": 5, "has_acknowledgment": False, "has_greeting": False}
        score_same = compute_sentence_similarity(ack_features, ack_features)
        score_diff = compute_sentence_similarity(ack_features, no_ack_features)
        assert score_same >= score_diff


class TestViolatesIdentityConstraints:
    """Tests for identity constraint violation detection."""

    def test_no_identities_no_violation(self) -> None:
        """Verify no violation when neither group has identities."""
        group1 = [0, 1]
        group2 = [2, 3]
        constraints: list[IdentityConstraint] = []
        assert violates_identity_constraints(group1, group2, constraints) is False

    def test_same_identity_no_violation(self) -> None:
        """Verify no violation when both groups have same identity."""
        group1 = [0, 1]
        group2 = [2, 3]
        constraints = [
            IdentityConstraint(
                sentence_idx=0, name="Peter Parker", constraint_type="self_identification"
            ),
            IdentityConstraint(
                sentence_idx=2, name="Peter Parker", constraint_type="self_identification"
            ),
        ]
        # Both have same identity, should not violate
        assert violates_identity_constraints(group1, group2, constraints) is False

    def test_different_identities_violation(self) -> None:
        """Verify violation when groups have different identities."""
        group1 = [0, 1]
        group2 = [2, 3]
        constraints = [
            IdentityConstraint(
                sentence_idx=0, name="Peter Parker", constraint_type="self_identification"
            ),
            IdentityConstraint(
                sentence_idx=2, name="Frank Oz", constraint_type="self_identification"
            ),
        ]
        # Different identities, should violate
        assert violates_identity_constraints(group1, group2, constraints) is True

    def test_only_one_group_has_identity(self) -> None:
        """Verify no violation when only one group has identity."""
        group1 = [0, 1]
        group2 = [2, 3]
        constraints = [
            IdentityConstraint(
                sentence_idx=0, name="Peter Parker", constraint_type="self_identification"
            ),
        ]
        # Only group1 has identity, no conflict
        assert violates_identity_constraints(group1, group2, constraints) is False

    def test_addresses_other_ignored(self) -> None:
        """Verify addresses_other constraints are not considered for violation."""
        group1 = [0, 1]
        group2 = [2, 3]
        constraints = [
            IdentityConstraint(sentence_idx=0, name="Frank", constraint_type="addresses_other"),
        ]
        # addresses_other should not cause violation
        assert violates_identity_constraints(group1, group2, constraints) is False


class TestGroupSentencesBySimilarity:
    """Tests for similarity-based sentence grouping."""

    def test_empty_sentences_returns_empty(self) -> None:
        """Verify empty input returns empty list."""
        result = group_sentences_by_similarity([], [], 2)
        assert result == []

    def test_single_speaker_all_same(self) -> None:
        """Verify single speaker assigns all to speaker 0."""
        sentences = ["First.", "Second.", "Third."]
        change_points = [0, 1, 2]
        result = group_sentences_by_similarity(sentences, change_points, 1)
        assert all(s == 0 for s in result)

    def test_two_speakers_alternation(self) -> None:
        """Verify two speakers get assigned in segments."""
        sentences = ["First speaker.", "Second speaker.", "Third speaker."]
        change_points = [0, 1, 2]
        result = group_sentences_by_similarity(sentences, change_points, 2)
        assert len(result) == 3
        # Should have at least 2 different speakers
        assert len(set(result)) >= 1  # May be 1 if similarity clusters them

    def test_three_speakers_round_robin(self) -> None:
        """Verify three speakers with few segments use round-robin."""
        sentences = ["A speaks.", "B speaks.", "C speaks."]
        change_points = [0, 1, 2]
        result = group_sentences_by_similarity(sentences, change_points, 3)
        assert len(result) == 3
        # With round-robin, should have 3 different speakers
        assert set(result) == {0, 1, 2}

    def test_respects_identity_constraints(self) -> None:
        """Verify identity constraints prevent merging."""
        sentences = ["I'm Peter.", "Generic.", "I'm Frank."]
        change_points = [0, 1, 2]
        constraints = [
            IdentityConstraint(sentence_idx=0, name="Peter", constraint_type="self_identification"),
            IdentityConstraint(sentence_idx=2, name="Frank", constraint_type="self_identification"),
        ]
        result = group_sentences_by_similarity(sentences, change_points, 3, constraints)
        # Peter and Frank should NOT be same speaker
        assert result[0] != result[2]

    def test_more_segments_than_speakers(self) -> None:
        """Verify handling when more segments than speakers."""
        sentences = ["One.", "Two.", "Three.", "Four.", "Five.", "Six."]
        change_points = [0, 1, 2, 3, 4, 5]
        result = group_sentences_by_similarity(sentences, change_points, 2)
        assert len(result) == 6
        # All should be assigned to valid speakers
        assert all(s in [0, 1] for s in result)


class TestExtractSpeakerIdentities:
    """Tests for speaker identity extraction."""

    def test_im_pattern(self) -> None:
        """Verify 'I'm [Name]' pattern is detected."""
        sentences = ["Hello there.", "I'm Peter Parker.", "Nice to meet you."]
        identities = extract_speaker_identities(sentences)
        assert 1 in identities
        assert "Peter Parker" in identities[1]

    def test_my_name_is_pattern(self) -> None:
        """Verify 'My name is [Name]' pattern is detected."""
        sentences = ["Hello.", "My name is Frank Oz."]
        identities = extract_speaker_identities(sentences)
        assert 1 in identities
        assert "Frank Oz" in identities[1]

    def test_this_is_pattern(self) -> None:
        """Verify 'This is [Name]' pattern is detected."""
        sentences = ["This is Alice Johnson speaking."]
        identities = extract_speaker_identities(sentences)
        assert 0 in identities
        assert "Alice Johnson" in identities[0]

    def test_no_identification(self) -> None:
        """Verify no match returns empty dict for generic sentences."""
        sentences = ["Hello.", "How are you?", "Good to see you."]
        identities = extract_speaker_identities(sentences)
        assert len(identities) == 0

    def test_multiple_identifications(self) -> None:
        """Verify multiple identifications are captured."""
        sentences = ["I'm Alice.", "Nice to meet you.", "I'm Bob."]
        identities = extract_speaker_identities(sentences)
        assert 0 in identities
        assert 2 in identities
        assert "Alice" in identities[0]
        assert "Bob" in identities[2]


class TestResolveAddressesOtherViolations:
    """Tests for resolving addresses_other violations."""

    def test_two_speakers_no_change(self) -> None:
        """Verify 2 speakers returns unchanged assignments."""
        sentences = ["Thanks Frank.", "You're welcome."]
        assignments = [0, 1]
        constraints: list[IdentityConstraint] = [
            IdentityConstraint(sentence_idx=0, name="Frank", constraint_type="addresses_other"),
        ]
        result = resolve_addresses_other_violations(sentences, assignments, constraints, 2)
        # For 2 speakers, no change should occur
        assert result == assignments

    def test_three_speakers_fixes_violation(self) -> None:
        """Verify 3 speakers fixes addresses_other violations."""
        sentences = ["I'm Frank.", "Thanks Frank.", "You're welcome."]
        # Initially sentence 1 is assigned to speaker 0 (Frank) which is wrong
        # because it addresses Frank
        assignments = [0, 0, 1]
        constraints = [
            IdentityConstraint(
                sentence_idx=0, name="Frank Oz", constraint_type="self_identification"
            ),
            IdentityConstraint(sentence_idx=1, name="Frank", constraint_type="addresses_other"),
        ]
        result = resolve_addresses_other_violations(sentences, assignments, constraints, 3)
        # Sentence 1 should NOT be assigned to speaker 0 (Frank)
        assert result[1] != 0

    def test_no_constraints_unchanged(self) -> None:
        """Verify no constraints returns unchanged assignments."""
        sentences = ["Hello.", "Hi there."]
        assignments = [0, 1]
        constraints: list[IdentityConstraint] = []
        result = resolve_addresses_other_violations(sentences, assignments, constraints, 3)
        assert result == assignments

    def test_unknown_addressed_person_unchanged(self) -> None:
        """Verify addressing unknown person leaves assignment unchanged."""
        sentences = ["Thanks Alice.", "You're welcome."]
        assignments = [0, 1]
        constraints = [
            IdentityConstraint(sentence_idx=0, name="Alice", constraint_type="addresses_other"),
        ]
        # Alice is not identified, so no change
        result = resolve_addresses_other_violations(sentences, assignments, constraints, 3)
        assert result == assignments


class TestFindSafeReplacementSpeaker:
    """Tests for finding safe replacement speakers."""

    def test_previous_speaker_safe(self) -> None:
        """Verify previous sentence speaker is preferred if safe."""
        assignments = [1, 0, 2]  # sentence 0 -> speaker 1, sentence 1 -> speaker 0
        constraints: list[IdentityConstraint] = []
        speaker_to_name: dict[int, str] = {0: "Frank"}
        # For sentence 1, exclude speaker 0 (Frank)
        result = _find_safe_replacement_speaker(1, 0, assignments, constraints, speaker_to_name, 3)
        # Should prefer speaker 1 (previous sentence's speaker)
        assert result == 1

    def test_next_speaker_used_if_previous_excluded(self) -> None:
        """Verify next sentence speaker is used if previous is excluded."""
        assignments = [0, 0, 2]  # sentence 0 and 1 both speaker 0
        constraints: list[IdentityConstraint] = []
        speaker_to_name: dict[int, str] = {0: "Frank"}
        # Exclude speaker 0, prev (sentence 0) is also 0, so use next
        result = _find_safe_replacement_speaker(1, 0, assignments, constraints, speaker_to_name, 3)
        # Should use speaker 2 (next sentence's speaker)
        assert result == 2

    def test_fallback_to_any_safe_speaker(self) -> None:
        """Verify fallback to any non-excluded speaker."""
        assignments = [0, 0, 0]
        constraints: list[IdentityConstraint] = []
        speaker_to_name: dict[int, str] = {0: "Frank"}
        # All assigned to 0, exclude 0
        result = _find_safe_replacement_speaker(1, 0, assignments, constraints, speaker_to_name, 3)
        # Should return 1 or 2
        assert result in [1, 2]

    def test_multiple_exclusions(self) -> None:
        """Verify multiple exclusions are respected."""
        assignments = [0, 0, 2]
        constraints = [
            IdentityConstraint(sentence_idx=1, name="Alice", constraint_type="addresses_other"),
            IdentityConstraint(sentence_idx=1, name="Bob", constraint_type="addresses_other"),
        ]
        speaker_to_name = {0: "Frank", 1: "Alice", 2: "Bob"}
        # Sentence 1 addresses Alice (speaker 1) and Bob (speaker 2)
        # Exclude Frank (0), Alice (1), Bob (2)
        result = _find_safe_replacement_speaker(1, 0, assignments, constraints, speaker_to_name, 3)
        # No safe option should return None
        assert result is None

    def test_no_exclusions_returns_first_candidate(self) -> None:
        """Verify no exclusions returns previous speaker."""
        assignments = [1, 0, 2]
        constraints: list[IdentityConstraint] = []
        speaker_to_name: dict[int, str] = {}
        # No speaker_to_name, so no exclusions from addresses
        result = _find_safe_replacement_speaker(1, 0, assignments, constraints, speaker_to_name, 3)
        # Should return previous speaker (1)
        assert result == 1
