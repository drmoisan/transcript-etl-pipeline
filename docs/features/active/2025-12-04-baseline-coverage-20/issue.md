# baseline-coverage (Issue [#20](https://github.com/drmoisan/transcript-etl-pipeline/issues/20))

- Date captured: 2025-12-04
- Author: Dan Moisan
- Status: Promoted -> docs/features/active/2025-12-04-baseline-coverage-20 (Issue #20)

> Automation note: Keep the section headings below unchanged; the promotion tooling maps each of them into the GitHub bug issue template.

- Issue: #20
- Issue URL: https://github.com/drmoisan/transcript-etl-pipeline/issues/20
- Last Updated: 2026-02-06

## Problem / Why

Coverage is ~16% with gaps in core transform and speakerless flows; CLI/UI paths are barely covered. The project needs a coordinated baseline to prevent regressions and steadily raise coverage on core logic without blocking on full CLI/UI parity.

## Proposed Behavior

Establish a baseline automated test/coverage initiative that prioritizes core logic, adds regression tests for bug-prone areas, and enforces “no merge without tests.”

## Acceptance Criteria (early draft)

- [ ] Reach 80% coverage on core logic without blocking on CLI/UI parity.
- [ ] Add regression tests for recent/known bug-prone areas.
- [ ] Enforce “no PR merges without tests” and “every bug fix ships with a regression test.”
- [ ] Coverage must not decrease; enforce locally and add CI coverage gate once baseline improves.

## Constraints & Risks

- Current coverage includes CLI/UI/legacy paths and is ~16% (snapshot on 2025-12-04).
- Avoid blocking on CLI/UI parity; focus on core transform and speakerless flows first.
- Coverage gate should be introduced after baseline improves to avoid blocking progress.

## Test Conditions to Consider

- [ ] Unit tests for core transform modules: `transform/enhance.py`, `identity_constraints.py`, `normalize.py`.
- [ ] Unit/regression tests for speakerless grouping heuristics.
- [ ] Fixtures and regression tests for 3+ speaker scenarios.
- [ ] End-to-end tests for speakerless + notes flows (CLI).
- [ ] Regression tests for notes conversion edge cases.
- [ ] Tests for formatters and document parser.

## Next Step

- [x] Promote to GitHub issue (Issue #20)
- [ ] Create `docs/features/active/baseline-coverage/` folder from the template

## Sync Summary (as of 2026-02-03T17-30)

- **Status:** In progress; acceptance criteria not fully evidenced.
- **Evidence highlights:** Core feature docs and plans exist under `docs/features/active/2025-12-04-baseline-coverage-20/` for #21–#28.
- **Open gaps:** Coverage >= 80% not evidenced; CI coverage gate documentation and run evidence pending; multiple feature issue updates remain outstanding.

### Sync Summary Update (as of 2026-02-06T16-44)

- **Status:** Delivered (tests/coverage/CI); documentation reconciliation in progress.

- **Authoritative final QA evidence (recorded 2026-02-03T18-30):**
	- Evidence file: `baseline/final-qa.2026-02-03T18-30/pytest.final.2026-02-03T18-30.txt`
	- Coverage: `Required test coverage of 15.0% reached. Total coverage: 86.03%`
	- Tests: `1749 passed, 5 xfailed`

- **CI coverage gate evidence:**
	- Evidence file: `2025-12-04-ci-coverage-gate-28/evidence/qa-gates/ci-run.2026-02-06T01-41.md`

- **GitHub issue updated:**
	- Issue: https://github.com/drmoisan/transcript-etl-pipeline/issues/20
	- GitHub Sync Summary updated to include final QA coverage + xfail inventory (see the issue body).

### Sync Summary Update (as of 2026-02-06T21-09)

- **Status:** Delivered (tests/coverage/CI) — audit-quality documentation alignment improved.

- **No new QA run performed since the 2026-02-03T18-30 final QA.** This update is documentation + conventions only.

- **Fail-before evidence accounting corrected (Issue #21):**
	- The epic feature delivery inventory now reflects #21 AC1 as **Met (exception recorded)** based on a schema-compliant dossier:
		- `2025-12-04-enhance-tests-21/evidence/regression-testing/fail-before-exception.2026-02-05T13-05.md`

- **Evidence conventions strengthened to prevent false negative claims:**
	- `evidence-and-timestamp-conventions` now requires deterministic search for `fail-before-exception.*.md` before stating “no fail-before evidence exists,” and requires recording `SearchScope` / `SearchPatterns` / `SearchResult` for any negative evidence claim.
	- Repo path: `.github/skills/evidence-and-timestamp-conventions/SKILL.md`

- **GitHub issue updated + mirrored:**
	- Issue: https://github.com/drmoisan/transcript-etl-pipeline/issues/20
	- Local mirror evidence: `evidence/issue-updates/issue-20.2026-02-06T21-09.md`