# multi-sentence-turn-grouping - Plan

- Issue: #16
- Owner: drmoisan
- Last Updated: 2025-12-04

## Required References (read, do not restate)

- Coding workflow and standards: [`docs/code-change.instructions.md`](../../code-change.instructions.md)
- Unit test policy: [`docs/unit-test-policy.md`](../../unit-test-policy.md)

**All work must comply with these policies; do not duplicate their content here.**

## Phases

### Phase 1: Instrumentation & Baseline [0%]
- [ ] Add debug logging to `detect_speaker_changes()` (sentence index + heuristic trigger).
- [ ] Run on SpaceX fixture to capture current triggers (12 vs 18 lines).

### Phase 2: Rhetorical continuation suppression [0%]
- [ ] Implement `_is_rhetorical_question()` (short/tag questions followed by continuations).
- [ ] Suppress speaker changes for rhetorical continuations.
- [ ] Add unit tests for rhetorical handling.

### Phase 3: Topic continuation heuristic [0%]
- [ ] Add keyword overlap check (>40%) to suppress changes for continuing topics.
- [ ] Add unit tests for topic-based suppression.

### Phase 4: Pronoun-shift gating [0%]
- [ ] Gate pronoun-shift triggers on boundary + dialogue marker (reduce false positives).
- [ ] Update/extend tests for pronoun-shift detection.

### Phase 5: Validation & integration [0%]
- [ ] Re-run `test_3speaker_spacex_discussion.py` (target 18 lines; remove XFAIL when passing).
- [ ] Ensure no regressions in other speakerless tests.
- [ ] Tooling: black/ruff/pyright/pytest.

## Test Plan

- Unit: rhetorical continuation helper; topic overlap suppression; gated pronoun shifts.
- Integration: `tests/integration/test_3speaker_spacex_discussion.py` expected 18 lines; other speakerless integration tests.
- Tooling: black, ruff, pyright, full pytest suite.

## Open Questions / Notes

- Keep heuristics lightweight and avoid overfitting to the SpaceX fixture; ensure 2-speaker scenarios remain stable.
