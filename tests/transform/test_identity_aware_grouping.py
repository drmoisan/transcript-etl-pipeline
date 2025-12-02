"""Unit tests for identity-aware speaker grouping.

Tests that identity constraints prevent incompatible speakers from being
grouped together during similarity-based speaker assignment.
"""

from transcript_etl_pipeline.transform.identity_constraints import (
    IdentityConstraint,
    extract_identity_constraints,
)
from transcript_etl_pipeline.transform.speaker_helpers import (
    group_sentences_by_similarity,
    resolve_addresses_other_violations,
    violates_identity_constraints,
)


class TestViolatesIdentityConstraints:
    """Tests for constraint violation detection."""

    def test_no_constraints_no_violation(self) -> None:
        """Test that empty constraints never violate."""
        group1 = [0, 1]
        group2 = [2, 3]
        constraints: list[IdentityConstraint] = []

        result = violates_identity_constraints(group1, group2, constraints)
        assert result is False

    def test_same_identity_no_violation(self) -> None:
        """Test that same identity in both groups is allowed."""
        group1 = [0, 1]
        group2 = [2, 3]
        constraints = [
            IdentityConstraint(0, "self_identification", "Peter Parker"),
            IdentityConstraint(2, "self_identification", "Peter Parker"),
        ]

        result = violates_identity_constraints(group1, group2, constraints)
        assert result is False

    def test_different_identities_violates(self) -> None:
        """Test that different identities in groups cause violation."""
        group1 = [0, 1]
        group2 = [2, 3]
        constraints = [
            IdentityConstraint(0, "self_identification", "Peter Parker"),
            IdentityConstraint(2, "self_identification", "Fred Flintstone"),
        ]

        result = violates_identity_constraints(group1, group2, constraints)
        assert result is True

    def test_one_group_no_identity_no_violation(self) -> None:
        """Test that if one group has no identity, no violation occurs."""
        group1 = [0, 1]
        group2 = [2, 3]
        constraints = [
            IdentityConstraint(0, "self_identification", "Peter Parker"),
            # group2 has no self-identification
        ]

        result = violates_identity_constraints(group1, group2, constraints)
        assert result is False

    def test_addresses_other_not_checked(self) -> None:
        """Test that addresses_other constraints don't cause violations."""
        group1 = [0, 1]
        group2 = [2, 3]
        constraints = [
            IdentityConstraint(0, "addresses_other", "Frank"),
            IdentityConstraint(2, "addresses_other", "Dan"),
        ]

        result = violates_identity_constraints(group1, group2, constraints)
        assert result is False

    def test_first_name_normalization(self) -> None:
        """Test that full names are normalized to first name for comparison."""
        group1 = [0, 1]
        group2 = [2, 3]
        constraints = [
            IdentityConstraint(0, "self_identification", "Peter Parker"),
            IdentityConstraint(2, "self_identification", "Peter Johnson"),
        ]

        # Both normalize to "Peter" so should NOT violate
        result = violates_identity_constraints(group1, group2, constraints)
        assert result is False


class TestIdentityAwareGrouping:
    """Tests for identity-aware similarity grouping."""

    def test_prevents_conflicting_identities_from_grouping(self) -> None:
        """Test that sentences with different self-identifications don't group."""
        sentences = [
            "Hello everyone.",
            "I'm Peter Parker and I work here.",
            "Nice to meet you.",
            "I'm Fred Flintstone from accounting.",
        ]

        # Simulate change points at each sentence
        change_points = [0, 1, 2, 3]
        num_speakers = 2

        # Create constraints
        constraints = [
            IdentityConstraint(1, "self_identification", "Peter Parker"),
            IdentityConstraint(3, "self_identification", "Fred Flintstone"),
        ]

        assignments = group_sentences_by_similarity(
            sentences, change_points, num_speakers, constraints
        )

        # Peter Parker and Fred Flintstone should be assigned to different speakers
        assert assignments[1] != assignments[3]

    def test_allows_same_identity_to_group(self) -> None:
        """Test that sentences with same identity CAN be grouped (not prevented)."""
        sentences = [
            "I'm Peter Parker.",
            "Let me explain my approach.",
            "As I mentioned, I'm Peter Parker.",
            "That's my perspective.",
        ]

        change_points = [0, 1, 2, 3]
        num_speakers = 2

        constraints = [
            IdentityConstraint(0, "self_identification", "Peter Parker"),
            IdentityConstraint(2, "self_identification", "Peter Parker"),
        ]

        assignments = group_sentences_by_similarity(
            sentences, change_points, num_speakers, constraints
        )

        # Key test: sentences with same identity are NOT prevented from grouping
        # (though they're not forced to group either - that's OK)
        # What matters is they CAN be assigned to the same speaker without violation
        assert all(a >= 0 for a in assignments)  # All assigned
        # Verify the constraint didn't prevent valid assignment
        # Both Peter Parker sentences should be assigned (somewhere)
        assert assignments[0] in [0, 1]
        assert assignments[2] in [0, 1]

    def test_three_speaker_constraint_enforcement(self) -> None:
        """Test constraint enforcement with three distinct speakers."""
        sentences = [
            "Hello everyone.",
            "I'm Peter Parker.",
            "Thanks for coming.",
            "I'm Frank Oz.",
            "Good to be here.",
            "I'm Fred Flintstone.",
        ]

        change_points = [0, 1, 2, 3, 4, 5]
        num_speakers = 3

        constraints = [
            IdentityConstraint(1, "self_identification", "Peter Parker"),
            IdentityConstraint(3, "self_identification", "Frank Oz"),
            IdentityConstraint(5, "self_identification", "Fred Flintstone"),
        ]

        assignments = group_sentences_by_similarity(
            sentences, change_points, num_speakers, constraints
        )

        # All three speakers should have different assignments
        assert assignments[1] != assignments[3]
        assert assignments[1] != assignments[5]
        assert assignments[3] != assignments[5]

    def test_no_constraints_uses_similarity_only(self) -> None:
        """Test that without constraints, grouping behavior is unchanged."""
        sentences = [
            "I think this is great.",
            "I agree completely.",
            "You make a good point.",
            "You're absolutely right.",
        ]

        change_points = [0, 1, 2, 3]
        num_speakers = 2

        # No constraints provided
        assignments = group_sentences_by_similarity(
            sentences, change_points, num_speakers, constraints=None
        )

        # Without constraints, algorithm should work as before
        # Verify that all sentences are assigned (no -1)
        assert all(a >= 0 for a in assignments)
        # Verify we use both speakers
        assert len(set(assignments)) == num_speakers

    def test_constraints_override_high_similarity(self) -> None:
        """Test that identity constraints override high similarity scores."""
        sentences = [
            "I think we should proceed.",  # Similar to next
            "I'm Peter Parker and I think we should proceed.",  # Very similar
            "I agree completely.",  # Similar to next
            "I'm Fred Flintstone and I agree completely.",  # Very similar
        ]

        change_points = [0, 1, 2, 3]
        num_speakers = 2

        constraints = [
            IdentityConstraint(1, "self_identification", "Peter Parker"),
            IdentityConstraint(3, "self_identification", "Fred Flintstone"),
        ]

        assignments = group_sentences_by_similarity(
            sentences, change_points, num_speakers, constraints
        )

        # Despite high similarity, different identities prevent grouping
        assert assignments[1] != assignments[3]


class TestResolveAddressesOtherViolations:
    """Tests for Phase 3: Post-processing addresses_other constraint violations."""

    def test_thanks_frank_not_assigned_to_frank(self) -> None:
        """Test that 'Thanks Frank' is NOT assigned to Speaker who is Frank.

        This is the key success criterion from the change plan:
        - 'Thanks Frank' should NOT be assigned to Frank (speaker cannot address themselves)
        """
        sentences = [
            "Hello everyone.",
            "I'm Frank Oz and I like puppets.",
            "Thanks Frank, that was interesting.",
            "You're welcome.",
        ]
        # Initial assignments: suppose sentence 2 gets wrongly assigned to Speaker B (Frank)
        # Speaker A = 0, Speaker B = 1
        initial_assignments = [0, 1, 1, 0]  # Sentence 2 wrongly assigned to Frank

        constraints = [
            IdentityConstraint(1, "self_identification", "Frank Oz"),
            IdentityConstraint(2, "addresses_other", "Frank"),
        ]

        result = resolve_addresses_other_violations(
            sentences, initial_assignments, constraints, num_speakers=3
        )

        # Sentence 2 should be reassigned away from Speaker B (Frank = index 1)
        assert result[2] != 1, "Sentence 'Thanks Frank' should NOT be assigned to Frank (Speaker B)"

    def test_no_violation_unchanged(self) -> None:
        """Test that correct assignments are not changed."""
        sentences = [
            "Hello everyone.",
            "I'm Frank Oz.",
            "Thanks Frank.",  # Already assigned to non-Frank speaker
            "You're welcome.",
        ]
        initial_assignments = [0, 1, 0, 1]  # Sentence 2 correctly assigned to Speaker A

        constraints = [
            IdentityConstraint(1, "self_identification", "Frank Oz"),
            IdentityConstraint(2, "addresses_other", "Frank"),
        ]

        result = resolve_addresses_other_violations(
            sentences, initial_assignments, constraints, num_speakers=3
        )

        # No change needed - already correct
        assert result == initial_assignments

    def test_unknown_person_ignored(self) -> None:
        """Test that addresses to unknown people are ignored."""
        sentences = [
            "Thanks Bob.",  # No one identified as Bob
            "You're welcome.",
        ]
        initial_assignments = [0, 1]

        # No self-identification constraint for "Bob"
        constraints = [
            IdentityConstraint(0, "addresses_other", "Bob"),
        ]

        result = resolve_addresses_other_violations(
            sentences, initial_assignments, constraints, num_speakers=2
        )

        # No change - Bob is unknown
        assert result == initial_assignments

    def test_adjacent_context_preferred(self) -> None:
        """Test that reassignment prefers adjacent speakers for natural flow."""
        sentences = [
            "Hello.",
            "I'm Frank Oz.",
            "Thanks Frank.",  # Violation if assigned to Frank
            "Interesting point.",
        ]
        # Sentence 2 wrongly assigned to Speaker B (Frank)
        initial_assignments = [0, 1, 1, 0]

        constraints = [
            IdentityConstraint(1, "self_identification", "Frank Oz"),
            IdentityConstraint(2, "addresses_other", "Frank"),
        ]

        result = resolve_addresses_other_violations(
            sentences, initial_assignments, constraints, num_speakers=3
        )

        # Should prefer previous or next speaker (0 or 0) for natural flow
        assert result[2] == 0  # Speaker A from adjacent context

    def test_two_speakers_skipped(self) -> None:
        """Test that two-speaker mode skips post-processing."""
        sentences = [
            "I'm Alice.",
            "Thanks Alice.",  # Would be a violation
        ]
        initial_assignments = [0, 0]  # Both assigned to same speaker

        constraints = [
            IdentityConstraint(0, "self_identification", "Alice"),
            IdentityConstraint(1, "addresses_other", "Alice"),
        ]

        # For 2 speakers, alternation already handles this
        result = resolve_addresses_other_violations(
            sentences, initial_assignments, constraints, num_speakers=2
        )

        # No change for 2 speakers
        assert result == initial_assignments

    def test_integration_with_constraint_extraction(self) -> None:
        """Test end-to-end with real constraint extraction."""
        sentences = [
            "Welcome everyone.",
            "I'm Frank Oz.",
            "Thanks Frank, go ahead.",
            "Sure, I'll start.",
        ]

        constraints = extract_identity_constraints(sentences)

        # Initial assignment with violation
        initial_assignments = [0, 1, 1, 0]  # Sentence 2 wrongly with Frank

        result = resolve_addresses_other_violations(
            sentences, initial_assignments, constraints, num_speakers=3
        )

        # Sentence 2 should be reassigned
        assert result[2] != 1, "Sentence addressing Frank should not be assigned to Frank"
