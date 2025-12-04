# Tracking Issue: Establish baseline automated tests & coverage

**Current state**

- Coverage: ~16% (CLI/UI/legacy paths included)
- Gaps: low coverage in core transform and speakerless flows; CLI/UI barely covered

**Goals**

- Reach 60–70% coverage on core logic; do not block on CLI/UI parity
- Add regression tests for recent/known bug-prone areas
- Hold the line: no PR merges without tests; every bug fix ships with a regression test

**Plan (child issues)**

- [ ] #`<id>` Add characterization + unit tests for `transform/enhance.py`
- [ ] #`<id>` Add unit tests for speakerless grouping heuristics
- [ ] #`<id>` Add end-to-end tests for speakerless + notes flows (CLI)
- [ ] #`<id>` Add regression tests for notes conversion edge cases
- [ ] #`<id>` Add fixtures for multi-speaker cases (3+ speakers, SpaceX scenario)
- [ ] #`<id>` Wire coverage reporting into CI; start with fail-under 40%, then ratchet upward

**Ground rules**

1) No new feature without tests.
2) Every bug fix ships with a regression test.
3) Coverage must not decrease (enforce locally; add a CI gate once baseline improves).

**Reference**

- Coverage snapshot (2025-12-04): 617 passed, 1 xfail (3-speaker SpaceX), 16% coverage.
- Command used: `poetry run pytest --maxfail=1 --disable-warnings --cov=src/transcript_etl_pipeline --cov-report=term`
