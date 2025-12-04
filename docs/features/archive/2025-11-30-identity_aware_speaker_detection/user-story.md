# 2025-11-30-identity_aware_speaker_detection - User Story

- Issue: N/A (completed change plan, PR #8)
- Owner: drmoisan
- Status: Complete
- Last Updated: 2025-12-02

## Problem / Why

Speaker assignment failed in multi-speaker transcripts that mentioned names: self-identifications could be misassigned, and utterances addressing someone by name could be incorrectly attributed to that person. Similarity-only grouping created assignments that violated conversational constraints.

## Personas & Scenarios

- Persona: Analyst processing multi-speaker transcripts  
  - Scenario: Transcript with explicit self-identifications (“I'm Peter Parker”) and addressee mentions (“Thanks Frank”); needs correct speaker labels without manual fixes.

## User Stories

- As a user, I want speaker detection to respect self-identifications so the named speaker is assigned correctly.
- As a user, I want sentences that address someone by name (“Thanks Frank”) to never be assigned to that person.
- As a user, I want identity constraints enforced without breaking existing two-speaker accuracy.

## Acceptance Criteria

- [x] Self-identification constraints enforced during grouping (“I'm X” ⇒ speaker X).
- [x] Addressing constraints enforced (“Thanks X” not assigned to X; conservative reassignment).
- [x] No regressions in existing speakerless detection; all prior tests still pass.
- [x] Full toolchain clean (black, ruff, pyright) and tests passing (509 total, 50 new).
- [x] Documentation updated to reflect identity-aware detection behavior.

## Non-Goals

- Performance benchmarking and visual debug output (tracked as nice-to-have P2).
