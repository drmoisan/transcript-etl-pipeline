# rhetorical-question-handling (Issue #19)

- Date captured: 2025-12-04
- Author: Dan Moisan
- Status: Promoted -> docs/features/active/rhetorical-question-handling/ (Issue #19)

- Issue: #19
- Issue URL: https://github.com/drmoisan/transcript-etl-pipeline/issues/19
- Last Updated: 2025-12-04
## Problem / Why

Rhetorical/tag questions (e.g., “Right?”, “You know?”, “..., didn’t it?”) are currently treated as speaker changes, causing over-splitting of multi-sentence turns (SpaceX test: 12 lines vs 18 expected).

## Proposed Behavior

- Detect rhetorical questions (short/tag patterns, continuations) and suppress speaker changes when they continue the same speaker’s thought.
- Handle trailing tag questions (“..., didn’t it?”, “right?”, “isn’t it?”, “don’t you think?”) so they don’t trigger a new speaker.

## Acceptance Criteria (early draft)

- [ ] Rhetorical question detection prevents speaker change on short/tag questions.
- [ ] Trailing tag questions do not trigger a change when they continue prior content.
- [ ] SpaceX test trend improves toward 18 lines (currently 12); no regressions in other speakerless tests.

## Constraints & Risks

- Keep heuristics lightweight; avoid overfitting to a single fixture.
- Must not regress 2-speaker accuracy.

## Test Conditions to Consider

- [ ] Unit: `_is_rhetorical_question()` patterns; tag question handling.
- [ ] Integration: `tests/integration/test_3speaker_spacex_discussion.py` expected 18 lines; other speakerless regression checks.
- [ ] CLI/API: no new flags; behavior validated via existing entry points.

## Next Step

- [ ] Promote to GitHub issue (feature request template)
- [ ] Create `docs/features/active/rhetorical-question-handling/` folder from the template


