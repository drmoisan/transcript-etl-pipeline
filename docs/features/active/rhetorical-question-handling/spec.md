# rhetorical-question-handling — Spec

- Issue: #19
- Owner: drmoisan
- Last Updated: 2025-12-04

## Overview

Rhetorical/tag questions (e.g., “Right?”, “You know?”, “..., didn’t it?”) are currently treated as speaker changes, causing over-splitting of multi-sentence turns (SpaceX test: 12 lines vs 18 expected).


## Behavior

- Detect rhetorical questions (short/tag patterns, continuations) and suppress speaker changes when they continue the same speaker’s thought.
- Handle trailing tag questions (“..., didn’t it?”, “right?”, “isn’t it?”, “don’t you think?”) so they don’t trigger a new speaker.


## Inputs / Outputs

- Inputs (CLI flags, files, env vars)
- Outputs (artifacts, logs, telemetry)

## API / CLI Surface

List commands, flags, request/response shapes, and examples.

## Data & State

Data flow, storage, or state changes introduced by this feature.

## Constraints & Risks

- Keep heuristics lightweight; avoid overfitting to a single fixture.
- Must not regress 2-speaker accuracy.


## Definition of Done

- [ ] Behavior matches acceptance criteria
- [ ] Tests updated/added
- [ ] Docs updated (README, docs/features/active/... links)
- [ ] Telemetry/logging (if applicable)

## Seeded Test Conditions (from potential)
- [ ] Unit: `_is_rhetorical_question()` patterns; tag question handling.
- [ ] Integration: `tests/integration/test_3speaker_spacex_discussion.py` expected 18 lines; other speakerless regression checks.
- [ ] CLI/API: no new flags; behavior validated via existing entry points.

