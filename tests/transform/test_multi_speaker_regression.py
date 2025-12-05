"""Regression tests for multi-speaker (3+) transcript processing.

This module tests speaker detection and assignment for transcripts with 3 or more
speakers. These tests help prevent regressions in the grouping and identity-aware
assignment logic.

Test Categories:
1. Fixture validation - Ensure fixtures are properly structured
2. Speaker count verification - Verify correct number of speakers detected
3. Identity constraint enforcement - Verify self-identification and addressing rules
4. Speaker assignment patterns - Verify expected speaker assignments
5. Content preservation - Verify transcript content is preserved

These tests use reusable fixtures from tests.fixtures.multi_speaker.
"""

import pytest

from tests.fixtures.multi_speaker import (
    ALL_3SPEAKER_FIXTURES,
    ALL_4SPEAKER_FIXTURES,
    ALL_MULTI_SPEAKER_FIXTURES,
    GENERIC_MEETING_3SPEAKER,
    PANEL_DISCUSSION_4SPEAKER,
    SPACEX_DISCUSSION,
    TEAM_STANDUP_3SPEAKER,
    MultiSpeakerFixture,
    get_fixture_by_name,
)
from transcript_etl_pipeline.transform.speakerless import (
    assign_speaker_labels,
    detect_speaker_changes,
    has_speaker_labels,
)


class TestMultiSpeakerFixtureValidation:
    """Validate the structure and content of multi-speaker fixtures."""

    @pytest.mark.parametrize(
        "fixture",
        ALL_MULTI_SPEAKER_FIXTURES,
        ids=[f.name for f in ALL_MULTI_SPEAKER_FIXTURES],
    )
    def test_fixture_has_required_fields(self, fixture: MultiSpeakerFixture) -> None:
        """Verify each fixture has all required fields populated."""
        assert fixture.name, "Fixture must have a name"
        assert fixture.description, "Fixture must have a description"
        assert fixture.num_speakers >= 3, "Multi-speaker fixtures must have 3+ speakers"
        assert fixture.input_text, "Fixture must have input text"
        assert len(fixture.expected_lines) > 0, "Fixture must have expected lines"
        assert len(fixture.characteristics) > 0, "Fixture must have characteristics"

    @pytest.mark.parametrize(
        "fixture",
        ALL_MULTI_SPEAKER_FIXTURES,
        ids=[f.name for f in ALL_MULTI_SPEAKER_FIXTURES],
    )
    def test_fixture_input_is_speakerless(self, fixture: MultiSpeakerFixture) -> None:
        """Verify fixture input text has no speaker labels."""
        result = has_speaker_labels(fixture.input_text)
        assert result is False, f"Fixture {fixture.name} input should be speakerless"

    @pytest.mark.parametrize(
        "fixture",
        ALL_MULTI_SPEAKER_FIXTURES,
        ids=[f.name for f in ALL_MULTI_SPEAKER_FIXTURES],
    )
    def test_fixture_expected_lines_are_valid(self, fixture: MultiSpeakerFixture) -> None:
        """Verify expected lines have valid speaker labels and content."""
        valid_speakers = {f"Speaker {chr(ord('A') + i)}" for i in range(fixture.num_speakers)}

        for line in fixture.expected_lines:
            assert line.speaker in valid_speakers, (
                f"Invalid speaker {line.speaker} in fixture {fixture.name}. "
                f"Expected one of {valid_speakers}"
            )
            assert line.content, f"Expected line {line.line_index} has empty content"
            assert line.line_index >= 0, f"Invalid line index {line.line_index}"

    def test_get_fixture_by_name_returns_correct_fixture(self) -> None:
        """Verify get_fixture_by_name works correctly."""
        fixture = get_fixture_by_name("spacex_discussion")
        assert fixture is not None
        assert fixture.name == "spacex_discussion"

    def test_get_fixture_by_name_returns_none_for_invalid(self) -> None:
        """Verify get_fixture_by_name returns None for invalid names."""
        fixture = get_fixture_by_name("nonexistent_fixture")
        assert fixture is None


class TestThreeSpeakerDetection:
    """Test speaker change detection for 3-speaker scenarios."""

    @pytest.mark.parametrize(
        "fixture",
        ALL_3SPEAKER_FIXTURES,
        ids=[f.name for f in ALL_3SPEAKER_FIXTURES],
    )
    def test_detects_multiple_speaker_changes(self, fixture: MultiSpeakerFixture) -> None:
        """Verify speaker changes are detected in 3-speaker transcripts."""
        changes = detect_speaker_changes(fixture.input_text)

        # A reasonable lower bound for speaker changes: at least half the expected lines.
        # This accounts for speaker turns being grouped (e.g., consecutive sentences from
        # the same speaker), while still verifying the algorithm detects meaningful changes.
        min_expected_changes = len(fixture.expected_lines) // 2
        assert len(changes) >= min_expected_changes, (
            f"Expected at least {min_expected_changes} speaker changes, " f"got {len(changes)}"
        )

    @pytest.mark.parametrize(
        "fixture",
        ALL_3SPEAKER_FIXTURES,
        ids=[f.name for f in ALL_3SPEAKER_FIXTURES],
    )
    def test_first_sentence_is_change_point(self, fixture: MultiSpeakerFixture) -> None:
        """Verify the first sentence is always a change point."""
        changes = detect_speaker_changes(fixture.input_text)
        assert 0 in changes, "First sentence (index 0) should always be a change point"


class TestFourSpeakerDetection:
    """Test speaker change detection for 4-speaker scenarios."""

    @pytest.mark.parametrize(
        "fixture",
        ALL_4SPEAKER_FIXTURES,
        ids=[f.name for f in ALL_4SPEAKER_FIXTURES],
    )
    def test_detects_multiple_speaker_changes(self, fixture: MultiSpeakerFixture) -> None:
        """Verify speaker changes are detected in 4-speaker transcripts."""
        changes = detect_speaker_changes(fixture.input_text)

        # Should detect at least as many changes as expected speaker turns
        min_expected_changes = len(fixture.expected_lines) // 2
        assert len(changes) >= min_expected_changes, (
            f"Expected at least {min_expected_changes} speaker changes, " f"got {len(changes)}"
        )


class TestSpeakerAssignment:
    """Test speaker label assignment for multi-speaker scenarios."""

    @pytest.mark.parametrize(
        "fixture",
        ALL_MULTI_SPEAKER_FIXTURES,
        ids=[f.name for f in ALL_MULTI_SPEAKER_FIXTURES],
    )
    def test_assigns_correct_number_of_speakers(self, fixture: MultiSpeakerFixture) -> None:
        """Verify the correct number of speakers are assigned."""
        result = assign_speaker_labels(fixture.input_text, num_speakers=fixture.num_speakers)

        # Extract unique speaker labels from result
        lines = [line for line in result.split("\r\n") if line.strip()]
        speakers = {line.split(":")[0].strip() for line in lines if ":" in line}

        assert (
            len(speakers) == fixture.num_speakers
        ), f"Expected {fixture.num_speakers} speakers, got {len(speakers)}: {speakers}"

    @pytest.mark.parametrize(
        "fixture",
        ALL_MULTI_SPEAKER_FIXTURES,
        ids=[f.name for f in ALL_MULTI_SPEAKER_FIXTURES],
    )
    def test_all_lines_have_speaker_labels(self, fixture: MultiSpeakerFixture) -> None:
        """Verify all output lines have speaker labels."""
        result = assign_speaker_labels(fixture.input_text, num_speakers=fixture.num_speakers)
        lines = [line for line in result.split("\r\n") if line.strip()]

        for i, line in enumerate(lines):
            assert line.startswith(
                "Speaker "
            ), f"Line {i} does not have speaker label: {line[:50]}..."


class TestContentPreservation:
    """Test that content is preserved during speaker assignment."""

    # Minimum word length to consider as a "key word" for content verification
    # Shorter words are often function words that don't indicate content preservation
    _MIN_KEY_WORD_LENGTH = 5

    # Common short words that should be excluded from key word matching
    # even if they meet the length threshold
    _EXCLUDED_COMMON_WORDS = frozenset({"their", "there", "these", "those"})

    @pytest.mark.parametrize(
        "fixture",
        ALL_MULTI_SPEAKER_FIXTURES,
        ids=[f.name for f in ALL_MULTI_SPEAKER_FIXTURES],
    )
    def test_key_content_preserved(self, fixture: MultiSpeakerFixture) -> None:
        """Verify key content phrases are preserved in output.

        Tests that the core words from expected content appear in the output.
        Note: Due to sentence tokenization, exact phrase matching may fail for
        sentences that get split. Instead, we check that key words appear.
        """
        result = assign_speaker_labels(fixture.input_text, num_speakers=fixture.num_speakers)

        # Check that significant words from expected content are present
        for expected in fixture.expected_lines[:5]:  # Check first 5 lines
            # Extract key words (words longer than threshold, excluding common words)
            key_words = [
                word.strip(".,!?")
                for word in expected.content.split()
                if (
                    len(word) >= self._MIN_KEY_WORD_LENGTH
                    and word.lower() not in self._EXCLUDED_COMMON_WORDS
                )
            ]
            # Check at least half the key words are present
            # (allows for sentence restructuring while still verifying content)
            words_found = sum(1 for word in key_words if word in result)
            assert words_found >= len(key_words) // 2, (
                f"Expected content keywords not found: {expected.content[:50]}... "
                f"(found {words_found}/{len(key_words)} key words)"
            )


class TestIdentityAwareAssignment:
    """Test identity-aware speaker assignment for 3+ speaker scenarios.

    These tests validate identity constraint enforcement. Some tests are marked
    as xfail because they represent known algorithmic gaps where the current
    implementation doesn't fully handle complex identity scenarios.
    """

    @pytest.mark.xfail(
        reason="Identity constraint ordering: first speaker identification may not "
        "map to Speaker A due to sentence tokenization and change detection order. "
        "This is a known gap in the current algorithm.",
        strict=False,
    )
    def test_generic_meeting_identity_constraints(self) -> None:
        """Test that self-identification constrains speaker assignment.

        In the generic meeting fixture:
        - "I'm Peter Parker" identifies Speaker A
        - "My name is Frank Oz" identifies Speaker B
        - "I'm Fred Flintstone" identifies Speaker C

        Note: This test is xfail because the algorithm doesn't guarantee that
        the first person to self-identify becomes Speaker A.
        """
        fixture = GENERIC_MEETING_3SPEAKER
        result = assign_speaker_labels(fixture.input_text, num_speakers=3)
        lines = [line for line in result.split("\r\n") if line.strip()]

        # Extract speaker and content for each line
        parsed_lines: list[tuple[str, str]] = []
        for line in lines:
            if ":" in line:
                speaker, content = line.split(":", 1)
                parsed_lines.append((speaker.strip(), content.strip()))

        # Verify identity constraints
        for speaker, content in parsed_lines:
            # Sentences containing "I'm Peter Parker" should be Speaker A
            if "I'm Peter Parker" in content or "I am Peter Parker" in content:
                assert (
                    speaker == "Speaker A"
                ), f"Peter Parker self-identification should be Speaker A, got {speaker}"

            # Sentences containing "My name is Frank Oz" should be Speaker B
            if "My name is Frank Oz" in content:
                assert (
                    speaker == "Speaker B"
                ), f"Frank Oz self-identification should be Speaker B, got {speaker}"

            # Sentences containing "I'm Fred Flintstone" should be Speaker C
            if "I'm Fred Flintstone" in content or "I am Fred Flintstone" in content:
                assert (
                    speaker == "Speaker C"
                ), f"Fred Flintstone self-identification should be Speaker C, got {speaker}"

    @pytest.mark.xfail(
        reason="Addresses-other constraint enforcement may not work when speaker "
        "identity is established mid-conversation. This is a known gap.",
        strict=False,
    )
    def test_generic_meeting_addressing_constraints(self) -> None:
        """Test that addressing someone by name constrains speaker assignment.

        In the generic meeting fixture:
        - "Thanks Frank" should NOT be assigned to Frank (Speaker B)
        - "Fred?" should NOT be assigned to Fred (Speaker C)

        Note: This test is xfail because addresses-other constraints may not
        be correctly enforced when speaker identities are established dynamically.
        """
        fixture = GENERIC_MEETING_3SPEAKER
        result = assign_speaker_labels(fixture.input_text, num_speakers=3)
        lines = [line for line in result.split("\r\n") if line.strip()]

        # Extract speaker and content for each line
        for line in lines:
            if ":" in line:
                speaker, content = line.split(":", 1)
                speaker = speaker.strip()
                content = content.strip()

                # "Thanks Frank" should NOT be from Frank (Speaker B)
                if "Thanks Frank" in content and "My name is Frank" not in content:
                    assert (
                        speaker != "Speaker B"
                    ), f"'Thanks Frank' should NOT be Speaker B (Frank), got {speaker}"

    def test_identity_constraints_different_speakers(self) -> None:
        """Test that different self-identifications get different speakers.

        This is a weaker test that verifies the basic constraint that
        people who identify as different names get different speaker labels.
        """
        fixture = GENERIC_MEETING_3SPEAKER
        result = assign_speaker_labels(fixture.input_text, num_speakers=3)
        lines = [line for line in result.split("\r\n") if line.strip()]

        # Find speakers for each identity
        peter_speaker = None
        frank_speaker = None
        fred_speaker = None

        for line in lines:
            if ":" in line:
                speaker, content = line.split(":", 1)
                speaker = speaker.strip()
                content = content.strip()

                if "I'm Peter Parker" in content or "I am Peter Parker" in content:
                    peter_speaker = speaker
                if "My name is Frank Oz" in content:
                    frank_speaker = speaker
                if "I'm Fred Flintstone" in content or "I am Fred Flintstone" in content:
                    fred_speaker = speaker

        # Verify different identities get different speakers
        if peter_speaker and frank_speaker:
            assert peter_speaker != frank_speaker, (
                f"Peter and Frank should have different speakers: "
                f"Peter={peter_speaker}, Frank={frank_speaker}"
            )
        if peter_speaker and fred_speaker:
            assert peter_speaker != fred_speaker, (
                f"Peter and Fred should have different speakers: "
                f"Peter={peter_speaker}, Fred={fred_speaker}"
            )
        if frank_speaker and fred_speaker:
            assert frank_speaker != fred_speaker, (
                f"Frank and Fred should have different speakers: "
                f"Frank={frank_speaker}, Fred={fred_speaker}"
            )


class TestSpaceXDiscussionRegression:
    """Regression tests specific to the SpaceX discussion fixture.

    These tests capture known behavior and prevent regressions in the
    3-speaker detection algorithm for natural conversations.
    """

    def test_produces_output_with_three_speakers(self) -> None:
        """Verify SpaceX discussion produces exactly 3 distinct speakers."""
        fixture = SPACEX_DISCUSSION
        result = assign_speaker_labels(fixture.input_text, num_speakers=3)

        lines = [line for line in result.split("\r\n") if line.strip()]
        speakers = {line.split(":")[0].strip() for line in lines if ":" in line}

        assert speakers == {
            "Speaker A",
            "Speaker B",
            "Speaker C",
        }, f"Expected exactly 3 speakers (A, B, C), got: {speakers}"

    def test_first_speaker_is_a(self) -> None:
        """Verify the first speaker is always Speaker A."""
        fixture = SPACEX_DISCUSSION
        result = assign_speaker_labels(fixture.input_text, num_speakers=3)

        lines = [line for line in result.split("\r\n") if line.strip()]
        first_line = lines[0]

        assert first_line.startswith(
            "Speaker A:"
        ), f"First line should be Speaker A, got: {first_line[:50]}..."

    def test_opening_addresses_devin_and_chris(self) -> None:
        """Verify the opening line addresses Devin and Chris (not the speaker)."""
        fixture = SPACEX_DISCUSSION
        result = assign_speaker_labels(fixture.input_text, num_speakers=3)

        lines = [line for line in result.split("\r\n") if line.strip()]
        first_line = lines[0]

        # The first speaker addresses Devin and Chris, so is neither of them
        assert "Devin" in first_line or "devin" in first_line.lower()
        assert "Chris" in first_line or "chris" in first_line.lower()

    @pytest.mark.stress_test
    @pytest.mark.xfail(
        reason="Perfect A/B/C rotation in natural conversation is algorithmically challenging. "
        "Current implementation uses heuristics that may not achieve perfect rotation.",
        strict=False,
    )
    def test_expected_speaker_rotation_pattern(self) -> None:
        """Test expected A/B/C rotation pattern matches fixture expectations.

        This is a strict test that verifies the algorithm matches the expected
        rotation pattern. Currently marked as xfail because natural conversations
        have ambiguous turn-taking that the current heuristics may not fully resolve.
        """
        fixture = SPACEX_DISCUSSION
        result = assign_speaker_labels(fixture.input_text, num_speakers=3)

        lines = [line for line in result.split("\r\n") if line.strip()]

        # Compare actual vs expected for each line.
        # Using strict=False because sentence tokenization may produce a different
        # number of output lines than expected. This test is xfail anyway, but
        # we want to catch speaker mismatches even when line counts differ.
        mismatches: list[str] = []
        zipped = zip(lines, fixture.expected_lines, strict=False)
        for i, (actual_line, expected) in enumerate(zipped):
            actual_speaker = actual_line.split(":")[0].strip()
            if actual_speaker != expected.speaker:
                mismatches.append(f"Line {i}: expected {expected.speaker}, got {actual_speaker}")

        assert (
            not mismatches
        ), f"Found {len(mismatches)} speaker assignment mismatches:\n" + "\n".join(
            mismatches[:10]
        )  # Show first 10


class TestTeamStandupRegression:
    """Regression tests for the team standup fixture.

    Tests that the meeting lead pattern is correctly detected where
    Speaker A facilitates and calls on other speakers.
    """

    def test_meeting_lead_opens_and_closes(self) -> None:
        """Verify the meeting lead (Speaker A) opens and closes the standup."""
        fixture = TEAM_STANDUP_3SPEAKER
        result = assign_speaker_labels(fixture.input_text, num_speakers=3)

        lines = [line for line in result.split("\r\n") if line.strip()]

        # First line should be Speaker A (meeting lead)
        assert lines[0].startswith("Speaker A:"), "Meeting lead should open the standup"

        # Last line should be Speaker A (meeting lead wrapping up)
        assert lines[-1].startswith("Speaker A:"), "Meeting lead should close the standup"

    @pytest.mark.xfail(
        reason="Addressing constraints for team members by name requires the "
        "algorithm to recognize that 'Sarah, you're next' comes from a different "
        "speaker than Sarah. This is a known gap in the current implementation.",
        strict=False,
    )
    def test_addressing_team_members(self) -> None:
        """Verify addressing team members by name works correctly.

        When the meeting lead says "Sarah, you're next" or "Mike, what about you",
        those lines should be from the meeting lead (Speaker A), not the addressed person.

        Note: This test is xfail because the algorithm may not correctly handle
        address constraints in all cases.
        """
        fixture = TEAM_STANDUP_3SPEAKER
        result = assign_speaker_labels(fixture.input_text, num_speakers=3)

        lines = [line for line in result.split("\r\n") if line.strip()]

        for line in lines:
            speaker, content = line.split(":", 1) if ":" in line else ("", line)
            speaker = speaker.strip()
            content = content.strip()

            # Lines addressing Sarah should NOT be from Sarah (Speaker B)
            if "Sarah, you're next" in content:
                assert (
                    speaker == "Speaker A"
                ), f"Line addressing Sarah should be from Speaker A, got {speaker}"

            # Lines addressing Mike should NOT be from Mike (Speaker C)
            if "Mike, what about you" in content:
                assert (
                    speaker == "Speaker A"
                ), f"Line addressing Mike should be from Speaker A, got {speaker}"

    def test_different_speakers_for_updates(self) -> None:
        """Verify that different team members get different speakers for their updates.

        This is a weaker test that verifies basic speaker diversity in the standup.
        """
        fixture = TEAM_STANDUP_3SPEAKER
        result = assign_speaker_labels(fixture.input_text, num_speakers=3)

        lines = [line for line in result.split("\r\n") if line.strip()]
        speakers = {line.split(":")[0].strip() for line in lines if ":" in line}

        # Should have exactly 3 speakers (meeting lead + 2 team members)
        assert len(speakers) == 3, f"Expected 3 speakers, got: {speakers}"


class TestPanelDiscussionRegression:
    """Regression tests for the 4-speaker panel discussion fixture."""

    def test_produces_four_speakers(self) -> None:
        """Verify panel discussion produces exactly 4 distinct speakers."""
        fixture = PANEL_DISCUSSION_4SPEAKER
        result = assign_speaker_labels(fixture.input_text, num_speakers=4)

        lines = [line for line in result.split("\r\n") if line.strip()]
        speakers = {line.split(":")[0].strip() for line in lines if ":" in line}

        assert speakers == {
            "Speaker A",
            "Speaker B",
            "Speaker C",
            "Speaker D",
        }, f"Expected 4 speakers (A, B, C, D), got: {speakers}"

    def test_moderator_asks_questions(self) -> None:
        """Verify moderator (Speaker A) asks questions throughout the discussion."""
        fixture = PANEL_DISCUSSION_4SPEAKER
        result = assign_speaker_labels(fixture.input_text, num_speakers=4)

        lines = [line for line in result.split("\r\n") if line.strip()]

        # Find lines that are questions (end with ?)
        speaker_a_questions: list[str] = []
        for line in lines:
            if ":" in line:
                speaker, content = line.split(":", 1)
                if speaker.strip() == "Speaker A" and "?" in content:
                    speaker_a_questions.append(content.strip())

        # Moderator should ask at least 2 questions
        assert len(speaker_a_questions) >= 2, (
            f"Expected moderator (Speaker A) to ask at least 2 questions, "
            f"found {len(speaker_a_questions)}"
        )
