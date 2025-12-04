# multi-sentence-turn-grouping - User Story

- Issue: #16
- Owner: drmoisan
- Status: Draft
- Last Updated: 2025-12-04

## Problem / Why

Speakerless detection over-splits and under-groups multi-sentence turns. In the 3-speaker SpaceX test, the algorithm outputs 12 lines instead of 18 because change heuristics (pronoun shifts, dialogue markers) fire inside a single speaker’s turn and there is no rhetorical/topic continuation handling.

## Personas & Scenarios

- Persona: Developer improving speakerless detection  
  - Scenario: Needs heuristics and diagnostics to keep multi-sentence turns intact so 3-speaker transcripts align with expected turn counts.

## User Stories

- As a developer, I want rhetorical and topic continuations to suppress false speaker changes so multi-sentence turns stay grouped.
- As a developer, I want pronoun-shift triggers to be gated so they don’t fire inside one speaker’s turn.
- As a developer, I want debug logging that shows which heuristics fire to diagnose mis-grouping.

## Acceptance Criteria

- [ ] Debug logging in `detect_speaker_changes()` shows heuristic triggers (sentence index + trigger).
- [ ] Rhetorical question continuations do not trigger speaker changes.
- [ ] Topic continuation heuristic suppresses changes when keyword overlap is high (>40%).
- [ ] Pronoun shift change detection is gated (boundary + dialogue marker) to reduce false positives.
- [ ] 3-speaker SpaceX test outputs 18 lines (currently 12) and can be un-XFAILed.
- [ ] No regression to 2-speaker accuracy or existing tests.

## Non-Goals

- Broader speaker logic refinements (acknowledgments, addressee patterns, similarity features) are tracked separately.
