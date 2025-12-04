# multi-sentence-turn-grouping (Issue: #16)

- Date captured: 2025-12-03
- Author: Dan Moisan
- Issue: #16
- Issue URL: https://github.com/drmoisan/transcript-etl-pipeline/issues/16
- Last Updated: 2025-12-04
- Status: Promoted -> docs/features/active/multi-sentence-turn-grouping/ (Issue #16)

## Problem / Why

Speakerless detection over-splits and under-groups multi-sentence turns: the 3-speaker SpaceX test produces 12 lines instead of 18, with 100% speaker mismatch due to aggressive change detection (pronoun shifts, dialogue markers) and missing rhetorical/topic continuation handling.

## Proposed Behavior

- Suppress false speaker changes within a single speaker’s multi-sentence turn by adding rhetorical question continuation and topic continuation heuristics.
- Reduce pronoun-shift false positives by requiring boundary + dialogue marker confirmation.
- Add debug logging to trace fired heuristics in `detect_speaker_changes()` for diagnostics.
- Rebalance grouping so consecutive same-speaker sentences stay merged and the SpaceX test hits the expected 18 turns.

## Acceptance Criteria (early draft)

- [ ] Debug logging exists for `detect_speaker_changes()` heuristics (sentence index + trigger).
- [ ] Rhetorical question continuations do not trigger speaker changes.
- [ ] Topic continuation heuristic suppresses changes when keyword overlap is high (>40%).
- [ ] Pronoun shift heuristic only triggers when boundary + dialogue marker conditions are met.
- [ ] 3-speaker SpaceX test produces 18 lines (currently 12) and is no longer XFAIL.

## Constraints & Risks

- Must not regress existing speakerless accuracy for 2-speaker cases.
- Heuristics should avoid overfitting to SpaceX while remaining lightweight.
- Logging should be optional and not impact performance in normal runs.

## Test Conditions to Consider

- [ ] Unit: rhetorical continuation, topic overlap suppression, pronoun-shift gating.
- [ ] Integration: `tests/integration/test_3speaker_spacex_discussion.py` expected 18 lines.
- [ ] CLI/API: no new flags; validate behavior via existing speakerless entry points.

## Next Step

- [ ] Promote to GitHub issue (feature request template)
- [ ] Create `docs/features/active/multi-sentence-turn-grouping/` folder from the template
