# 2025-11-30-identity_aware_speaker_detection - Spec

- Issue: N/A (completed change plan, PR #8)
- Owner: drmoisan
- Last Updated: 2025-12-02

## Overview

Identity-aware speaker detection integrates name-based constraints into speakerless grouping so self-identifications are honored and addressee violations are prevented, without regressing existing speakerless accuracy.

## Behavior

- Extract identity constraints before grouping:
  - Self-identification: “I'm <Name>”, “My name is <Name>”, “This is <Name>”.
  - Addresses-other: vocatives such as “Thanks <Name>”, “<Name>, what do you think”.
- Enforce constraints during grouping:
  - Self-ID is a hard constraint; conflicting identities cannot merge.
  - Similarity scoring is skipped when a merge would violate identity.
- Post-processing for addresses-other:
  - If a sentence addressing <Name> is assigned to <Name>, reassign conservatively to a safe speaker (adjacent preference); log warnings if unresolved.
- Preserve baseline behavior when no identity info is present; fall back to similarity and round-robin as needed.

## Inputs / Outputs

- Inputs: transcripts without explicit speaker labels containing name mentions/self-identifications.
- Outputs: speaker assignments that respect identity constraints; no self-addressing or self-identification violations.

## API / CLI Surface

- No new CLI flags; changes are internal to speakerless detection.
- Affected modules:
  - `transform/identity_constraints.py`: extract constraints.
  - `transform/speaker_helpers.py`: constraint-aware grouping and post-processing.
  - `transform/speakerless.py`: integrates constraint extraction + enforcement.

## Data & State

- IdentityConstraint dataclass captures constraint type and name per sentence.
- Constraints passed into grouping; post-processing uses constraint metadata for safe reassignment.

## Constraints & Risks

- Must not regress existing two-speaker accuracy or prior tests.
- Constraint checks add minimal overhead (small lists).
- Separate semantics retained for legacy `speakers.py` address detection vs constraint extraction.

## Definition of Done

- [x] Self-ID constraints enforced in grouping; addresses-other handled in post-processing.
- [x] 50 new tests added (constraints extraction, grouping, post-processing); total 509 tests passing.
- [x] Tooling clean (black, ruff, pyright, pytest).
- [x] Docs updated (change plan, README) to reflect identity-aware behavior.

## Seeded Test Conditions

- [x] Self-ID: “I'm Peter Parker” assigned to Peter; “I'm Fred Flintstone” assigned to Fred.
- [x] Addresses-other: “Thanks Frank” not assigned to Frank; conservative reassignment.
- [x] No constraints: similarity-only behavior unchanged.
- [x] Integration: explicit three-speaker test passes with identity constraints enforced.
