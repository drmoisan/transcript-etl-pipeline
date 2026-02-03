# identity-normalize (Issue [#23](https://github.com/drmoisan/transcript-etl-pipeline/issues/23))

- Date captured: 2025-12-04
- Author: Dan Moisan
- Status: Promoted -> docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-identity-normalize-23/ (Issue #23)

- Issue: #23
- Issue URL: [https://github.com/drmoisan/transcript-etl-pipeline/issues/23](https://github.com/drmoisan/transcript-etl-pipeline/issues/23)
- Last Updated: 2025-12-04

## Problem / Why

`transform/identity_constraints.py` and `transform/normalize.py` lack targeted unit coverage, leaving name extraction, constraint application, and normalization edge cases unverified. This gap makes regressions easy to miss and obscures behavior for tricky inputs.

## Proposed Behavior

Add focused Pytest unit coverage for identity constraint extraction/application and text normalization edge cases, asserting on expected constraints and normalized outputs for tricky inputs.

## Acceptance Criteria (early draft)

- [ ] Unit tests cover primary branches and edge cases in `transform/identity_constraints.py` and `transform/normalize.py`.
- [ ] Tests assert on extracted constraints and normalized outputs for tricky inputs.
- [ ] Combined coverage across both modules reaches $\ge 75\%$.

## Constraints & Risks

- Tests must be deterministic, isolated, and avoid filesystem/temp files.
- Avoid expanding scope beyond the two modules.
- Risk: unclear expected behavior for ambiguous inputs; clarify via explicit assertions.

## Test Conditions to Consider

- [ ] Identity constraint extraction: names, aliases, and constraint combinations.
- [ ] Constraint application ordering and conflict resolution.
- [ ] Normalization edge cases: whitespace, punctuation, casing, and mixed speaker labels.
- [ ] Tricky inputs (e.g., partial names, parentheticals) with explicit expected outputs.

## Next Step

- [ ] Promote to GitHub issue (feature request template)
- [ ] Create `docs/features/active/identity-normalize/` folder from the template

## Sync Summary (as of 2026-02-03T17-30)

- **Status:** Partially delivered; acceptance criteria not fully evidenced.
- **Evidence highlights:** Tests exist in `tests/transform/test_identity_constraints.py` and `tests/transform/test_normalize.py`; coverage summary in `coverage-results.md`.
- **Open gaps:** Issue #23 update with coverage evidence not recorded; QA toolchain steps not verified.

