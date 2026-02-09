# Issue Update Mirror — Issue #20

Timestamp: 2026-02-06T16-44
Command: mcp_github_issue_write(method=update, owner=drmoisan, repo=transcript-etl-pipeline, issue_number=20, title=Tracking Issue: Establish baseline automated tests & coverage, body=<full body below>)
EXIT_CODE: 0

IssueNumber: 20
IssueURL: https://github.com/drmoisan/transcript-etl-pipeline/issues/20
PostedAs: body
IssueUpdatedAt: 2026-02-07T01:39:51Z

## Posted body (verbatim)

# Tracking Issue: Establish baseline automated tests & coverage

**Current state**
- Baseline snapshot (2025-12-04): ~16% coverage (CLI/UI/legacy paths included)
- Latest verified final QA (2026-02-03T18-30): **86.03% total coverage**, **1749 passed**, **5 xfailed**
- Gaps (historical): low coverage in core transform and speakerless flows; CLI/UI barely covered

**Goals**
- Reach 80% coverage on core logic; do not block on CLI/UI parity
- Add regression tests for recent/known bug-prone areas
- Hold the line: no PR merges without tests; every bug fix ships with a regression test

**Plan (child issues)**
- [x] #21 Add characterization + unit tests for `transform/enhance.py`
- [x] #22 Add unit tests for speakerless grouping heuristics
- [x] #23 Add tests for `identity_constraints.py` and `normalize.py`
- [ ] #24 Add fixtures and regression tests for 3+ speaker scenarios
- [ ] #25 Add end-to-end tests for speakerless + notes flows (CLI)
- [ ] #26 Add regression tests for notes conversion edge cases
- [ ] #27 Add tests for formatters and document parser
- [x] #28 Add CI coverage gate and reporting

**Ground rules**
1) No new feature without tests.  
2) Every bug fix ships with a regression test.  
3) Coverage must not decrease (enforce locally; add a CI gate once baseline improves).

**Reference**
- Coverage snapshot (2025-12-04): 617 passed, 1 xfail (3-speaker SpaceX), 16% coverage.
- Command used: `poetry run pytest --maxfail=1 --disable-warnings --cov=src/transcript_etl_pipeline --cov-report=term`

---

## Sync Summary (as of 2026-02-06T16-44)

- **Status:** Delivered (tests/coverage/CI) — documentation reconciliation in progress.

- **Authoritative final QA evidence (recorded 2026-02-03T18-30):**
  - Evidence file (repo path): `docs/features/active/2025-12-04-baseline-coverage-20/baseline/final-qa.2026-02-03T18-30/pytest.final.2026-02-03T18-30.txt`
  - Total coverage: `86.03%` (coverage floor satisfied: `Required test coverage of 15.0% reached`)
  - Tests: `1749 passed, 5 xfailed`

- **XFAILs (expected / documented gaps):**
  - `tests/integration/test_3speaker_spacex_discussion.py` (Complex 3-speaker detection)
  - `tests/transform/test_multi_speaker_regression.py` (4 xfails covering known identity/addressing/rotation gaps)

- **CI coverage gate evidence:**
  - Evidence file (repo path): `docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-ci-coverage-gate-28/evidence/qa-gates/ci-run.2026-02-06T01-41.md`

- **Open documentation items (non-code):**
  - Epic/feature docs contain a stale sync summary claiming “Coverage >= 80% not evidenced” prior to the final QA run; this needs to be superseded in the local epic docs for audit completeness.
