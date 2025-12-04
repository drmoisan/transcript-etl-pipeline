# multi-sentence-turn-grouping - Spec

- Issue: #16
- Owner: drmoisan
- Last Updated: 2025-12-04

## Overview

Improve speakerless detection for multi-sentence turns by adding diagnostic logging and suppression heuristics (rhetorical question continuation, topic continuation, gated pronoun shifts) so over-splitting is reduced and the 3-speaker SpaceX test reaches 18 turns.

## Behavior

- Diagnostics: `detect_speaker_changes()` logs sentence index and which heuristic fires (debug level) for targeted runs.
- Rhetorical continuation: short/tag questions followed by continuation words (e.g., “Right?” + “And…”) do not trigger a speaker change.
- Topic continuation: if keyword overlap with the previous sentence exceeds a threshold (e.g., >40%), suppress change to keep the same speaker.
- Pronoun-shift gating: require sentence boundary plus a dialogue marker (e.g., greeting/acknowledgment) before treating pronoun shifts as speaker changes.
- Outcome: consecutive same-speaker sentences remain grouped; SpaceX test expected lines = 18; no regressions on simpler cases.

## Inputs / Outputs

- Inputs: existing speakerless pipeline sentences; no new CLI flags.
- Outputs: unchanged API; improved grouping results and optional debug logs.

## API / CLI Surface

- Internal changes only; logging controlled via existing logging configuration.
- Files touched: `transform/speakerless.py`, `transform/speaker_helpers.py`, tests under `tests/transform` and `tests/integration/test_3speaker_spacex_discussion.py`.

## Data & State

- Uses in-memory heuristics; no persistent state changes.
- Logging is optional and should be disabled in normal runs.

## Constraints & Risks

- Must avoid regressions in 2-speaker scenarios and other speakerless tests.
- Heuristics should be lightweight and not overfit to a single fixture.
- Keep code/tooling compliance (black/ruff/pyright/pytest).

## Definition of Done

- [ ] Logging implemented for heuristic triggers.
- [ ] Rhetorical continuation suppression added and tested.
- [ ] Topic continuation heuristic added and tested.
- [ ] Pronoun-shift gating added and tested.
- [ ] SpaceX test outputs 18 lines; XFAIL can be removed.
- [ ] Full test/tooling pass (pytest/ruff/black/pyright).

## Seeded Test Conditions

- [ ] Unit: rhetorical continuation detection; topic overlap suppression; gated pronoun shifts.
- [ ] Integration: `test_3speaker_spacex_discussion.py` produces 18 lines; no regression in other speakerless tests.
