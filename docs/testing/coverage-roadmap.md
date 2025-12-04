# Coverage Improvement Roadmap

Current snapshot (2025-12-04):
- Tests: 617 passed, 1 xfail (3-speaker SpaceX fixture)
- Coverage: 16% (includes CLI/UI/legacy code paths)
- Command: `poetry run pytest --maxfail=1 --disable-warnings --cov=src/transcript_etl_pipeline --cov-report=term`

## Tracking issue (create as an epic)
**Title:** Tracking Issue: Establish baseline automated tests & coverage  
**Body (suggested):**
```
Current state
- Coverage: ~16% (CLI/UI/legacy paths included)
- Gaps: low coverage in core transform and speakerless flows; CLI/UI barely covered

Goals
- Reach 60–70% coverage on core logic; do not block on CLI/UI parity
- Add regression tests for recent/known bug-prone areas
- Hold the line: no PR merges without tests; every bug fix ships with a regression test

Plan (child issues)
- [ ] #<id> Add characterization + unit tests for transform/enhance.py
- [ ] #<id> Add unit tests for speakerless grouping heuristics
- [ ] #<id> Add end-to-end tests for speakerless + notes flows (CLI)
- [ ] #<id> Add regression tests for notes conversion edge cases
- [ ] #<id> Add fixtures for multi-speaker cases (3+ speakers, SpaceX scenario)
- [ ] #<id> Wire coverage reporting into CI; start with fail-under 40%, ratchet upward
```
Add label `epic` (or `type: epic`) and put it on your project board.

## Child issue templates (draft)
- **Add tests for transform/enhance.py (target ≥70% on module):** characterization tests around current behavior; unit tests for helpers; cover speakerless routing and constraint handling.
- **Add tests for speakerless grouping heuristics:** unit tests for rhetorical/tag questions, addressee detection, and continuation heuristics; integration check against known fixtures (SpaceX, etc.).
- **Add end-to-end tests for speakerless + notes flows:** CLI-driven runs that assert on DOCX/MD outputs for representative transcripts (notes pipeline, multi-speaker).
- **Add regression tests for notes conversion edge cases:** capture bugs previously noted in `feature_status.md` and notes_feature history.
- **Add fixtures for 3+ speakers:** reusable fixtures for multi-speaker identity resolution, including the SpaceX discussion.
- **CI coverage gate:** add `coverage report --fail-under=40` (or similar) in CI; later bump to 60%+ once core modules are covered.

## Ground rules (apply immediately)
1) No new feature without tests.  
2) Every bug fix ships with a regression test.  
3) Coverage must not decrease (enforce locally; wire CI gate once baseline improves).

## Priority focus areas (Tier 1 first)
- Tier 1: `transform/enhance.py`, `transform/speakerless.py`, `transform/speaker_helpers.py`, `transform/identity_constraints.py`, `transform/normalize.py`
- Tier 2: `document/parser.py`, `document/model.py`, `document/formatting_rules.py`, formatters (`docx`, `rtf`, `md`)
- Tier 3: CLI/UI glue (`cli.py`, `ui.py`), legacy/deprecated paths

## Execution loop per module
1) Characterize current behavior (tests that lock in existing outputs).  
2) Add unit tests at seams (pure functions first, then higher-level).  
3) Add targeted integration tests where wiring matters (CLI end-to-end).  
4) Refactor only after coverage in that area is in place.  
5) Re-run coverage and ensure the module meets the target before moving on.

## How to apply this now
1) Create the tracking issue with the body above.  
2) Spin off the child issues with the draft bullets; link them in the tracking issue.  
3) Adopt the ground rules for all new PRs.  
4) After a couple of modules are covered, add the CI fail-under gate (start lenient, then ratchet).
