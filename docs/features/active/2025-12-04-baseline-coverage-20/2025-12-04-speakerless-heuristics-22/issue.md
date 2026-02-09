# speakerless-heuristics (Issue [#22](https://github.com/drmoisan/transcript-etl-pipeline/issues/22))

- Date captured: 2025-12-04
- Author: Dan Moisan
- Status: Promoted -> docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-speakerless-heuristics-22/ (Issue #22)

- Issue: #22
- Issue URL: [https://github.com/drmoisan/transcript-etl-pipeline/issues/22](https://github.com/drmoisan/transcript-etl-pipeline/issues/22)
- Last Updated: 2025-12-04

## Problem / Why

`transform/speakerless.py` and `transform/speaker_helpers.py` lack focused unit tests for key heuristics (rhetorical/tag questions, addressee detection, continuation, clustering helpers). This leaves core speakerless grouping behavior under-specified and prone to regressions.

## Proposed Behavior

Add targeted Pytest unit coverage for speakerless heuristics and helper functions, validating positive and negative cases for each heuristic and ensuring coverage targets are met.

## Acceptance Criteria (early draft)

- [ ] Unit tests cover positive and negative cases for each heuristic in `transform/speakerless.py` and `transform/speaker_helpers.py`.
- [ ] Coverage for both modules reaches $\ge 70\%$.

## Constraints & Risks

- Tests must be deterministic and avoid filesystem/temp files.
- Keep scope limited to the two modules and their heuristics.
- Risk: ambiguous heuristic expectations; encode expected behavior explicitly in assertions.

## Test Conditions to Consider

- [ ] Rhetorical/tag question detection (positive/negative examples).
- [ ] Addressee detection cases, including mid-sentence vocatives.
- [ ] Continuation/turn-grouping heuristics.
- [ ] Clustering helper outputs and boundary conditions.

## Next Step

- [ ] Promote to GitHub issue (feature request template)
- [ ] Create `docs/features/active/speakerless-heuristics/` folder from the template

## Sync Summary (as of 2026-02-03T17-30)

- **Status:** Partially delivered; acceptance criteria not fully evidenced.
- **Evidence highlights:** Tests exist in `tests/transform/test_speakerless.py` and `tests/transform/test_speaker_helpers.py` matching plan items.
- **Open gaps:** Coverage report for `speakerless.py`/`speaker_helpers.py` not recorded; Issue #22 update not evidenced; QA toolchain steps not verified.

