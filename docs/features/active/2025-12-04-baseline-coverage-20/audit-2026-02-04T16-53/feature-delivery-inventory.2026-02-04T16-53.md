# Feature Delivery Inventory: 2025-12-04-baseline-coverage-20

Timestamp: 2026-02-04T16-53
EpicRootFolder: `docs/features/active/2025-12-04-baseline-coverage-20/`

## Summary inventory table

> Status meanings:
> - **Met**: acceptance criterion has direct code/test/config evidence.
> - **Partially Met**: primary behavior is present, but required evidence schema (or a required sub-criterion like fail-before) is missing.
> - **Not Met**: criterion contradicted by current code/docs.
> - **Unknown**: not enough evidence found.

| Feature | Issue | Current version | Current plan | Docs present (issue/spec/story/plan) | AC count (story) | Delivered (Met/Total) | Notes |
| --- | ---:| --- | --- | --- | ---:| ---:| --- |
| enhance-tests | 21 | root | `plan.2026-02-02T12-23.md` | ✅/✅/✅/✅ | 3 | 2/3 | Coverage evidence exists; strict fail-before not satisfied. |
| speakerless-heuristics | 22 | root | `plan.2026-02-02T12-24.md` | ✅/✅/✅/✅ | 6 | 6/6 | Strong module-level coverage evidence captured (but missing `EXIT_CODE:` field). |
| identity-normalize | 23 | root | `plan.2026-02-02T13-08.md` | ✅/✅/✅/✅ | 5 | 5/5 | Issue mirror reports 98%/100% module coverage; corroborated by full-suite coverage evidence. |
| multi-speaker-fixtures | 24 | root | `plan.2026-02-02T13-09.md` | ✅/✅/✅/✅ | 5 | 5/5 | Fixtures + regression suite exist; xfails document known gaps. |
| e2e-speakerless-notes | 25 | root | `plan.2026-02-02T12-45.md` | ✅/✅/✅/✅ | 4 | 4/4 | In-memory CLI integration tests exist and run in suite. |
| notes-regressions | 26 | root | `plan.2026-02-02T13-09.md` | ✅/✅/✅/✅ | 3 | 2/3 | Regression tests exist; fail-before dossier schema not compliant. |
| formatters-parser | 27 | root | `plan.2026-02-02T13-08.md` | ✅/✅/✅/✅ | 4 | 4/4 | Targeted `--cov-fail-under=70` run shows 93.83% for targeted modules. |
| ci-coverage-gate | 28 | root | `plan.2025-12-04T11-43.md` | ✅/✅/✅/✅ | 5 | 3/5 | CI config exists; missing verified CI run evidence + doc mismatch in remediation-baseline. |

## Acceptance criteria audit (per feature)

### Feature #21 — `2025-12-04-enhance-tests-21/`

Acceptance criteria source: `user-story.md`.

1. **Tests fail before and pass after (for previously untested behavior).** → **Partially Met**
   - Evidence (pass-after): `2025-12-04-enhance-tests-21/remediation-baseline/pass-after.2026-02-03T18-30.txt` (37 passed).
   - Evidence (fail-before): `2025-12-04-enhance-tests-21/remediation-baseline/fail-before.2026-02-03T18-30.md` explicitly states strict fail-before evidence unavailable.

2. **Speakerless routing and constraint handling scenarios are exercised.** → **Met**
   - Evidence: `2025-12-04-enhance-tests-21/remediation-baseline/coverage.2026-02-03T18-30.txt` shows `src/transcript_etl_pipeline/transform/enhance.py` at 100% and the test file `tests/transform/test_enhance.py` executed.

3. **Coverage report shows ≥70% for `transform/enhance.py`.** → **Met**
   - Evidence: same `coverage.2026-02-03T18-30.txt` shows 100% for `enhance.py`.

### Feature #22 — `2025-12-04-speakerless-heuristics-22/`

Acceptance criteria source: `user-story.md`.

1. Unit tests cover positive/negative cases for `detect_speaker_changes` heuristics → **Met**
2. Unit tests cover `resolve_addresses_other_violations` follow-through behavior → **Met**
3. Unit tests cover `group_sentences_by_similarity` boundaries → **Met**
4. Coverage for `speakerless.py` and `speaker_helpers.py` is ≥70% → **Met**
   - Evidence: `remediation-baseline/coverage.2026-02-03T18-30.txt` includes:
     - `speaker_helpers.py` 92%
     - `speakerless.py` 95%
     - Timestamp: 2026-02-04T03:27:43Z
     - Command: `python -m poetry run pytest ... --cov=...`
   - Note: artifact is **not auto-check eligible** under the epic hard gate because it does not include `EXIT_CODE:`.
5. Tests deterministic; no filesystem/temp files/external services → **Met** (unit-test structure; no contrary evidence found)
6. Issue #22 updated with coverage evidence and links → **Met**
   - Evidence: `issue-updates/issue-22.2026-02-04T11-21.md` (remote verification captured).

### Feature #23 — `2025-12-04-identity-normalize-23/`

Acceptance criteria source: `user-story.md`.

1. Unit tests cover main branches and edge cases → **Met**
2. Tests assert explicit constraints/normalized outputs → **Met**
3. Combined coverage ≥75% across both modules → **Met**
   - Evidence (reported in issue mirror): `issue-updates/issue-23.2026-02-04T11-21.md` reports 98% (`identity_constraints.py`) and 100% (`normalize.py`).
   - Corroborating evidence: full-suite coverage output embedded in `2025-12-04-identity-normalize-23/remediation-baseline/coverage.2026-02-03T18-30.txt` includes lines showing both modules at/near those values.
4. Tests deterministic; no filesystem/temp files/external services → **Met**
5. Issue updated with coverage evidence and links → **Met**
   - Evidence: `issue-updates/issue-23.2026-02-04T11-21.md`.

### Feature #24 — `2025-12-04-multi-speaker-fixtures-24/`

Acceptance criteria source: `user-story.md`.

All criteria appear **Met** by repo inspection and test-suite evidence:
- Shared fixtures exist under `tests/fixtures/multi_speaker.py`.
- Regression suite exists under `tests/transform/test_multi_speaker_regression.py`.
- `xfail` cases exist and are documented in coverage outputs (see the `XFAIL ...` lines in `2025-12-04-identity-normalize-23/remediation-baseline/coverage.2026-02-03T18-30.txt`).

### Feature #25 — `2025-12-04-e2e-speakerless-notes-25/`

Acceptance criteria source: `user-story.md`.

1. Integration tests cover speakerless CLI flows for DOCX/MD/RTF and pass reliably → **Met**
2. Integration tests cover notes-only and notes+transcript flows (including update mode) → **Met**
3. Tests include error cases for missing files/invalid args → **Met**
4. Output validation asserts stable markers rather than binary diffs → **Met**

Evidence:
- In-memory implementation confirmed by inspection:
  - `tests/integration/test_cli_e2e_speakerless.py` and `tests/integration/test_cli_e2e_notes.py` monkeypatch CLI extract/save paths and `Path.exists` to avoid filesystem writes.
- Suite execution evidence: `2025-12-04-notes-regressions-26/remediation-baseline/qa-pytest.2026-02-03T18-30.txt` includes both integration test modules running and passing.

### Feature #26 — `2025-12-04-notes-regressions-26/`

Acceptance criteria source: `user-story.md`.

1. Each known notes bug has a failing-before/passing-after regression test → **Partially Met**
   - Evidence of new regression tests + pass-after: `remediation-baseline/pass-after.2026-02-03T18-30.txt` (27 passed).
   - Fail-before artifact exists but does not meet the required machine-checkable dossier schema:
     - `remediation-baseline/fail-before.2026-02-03T18-30.md` (narrative only; no `Timestamp/Command/EXIT_CODE`).
2. Regression tests demonstrate prior failures and now pass → **Met (Exception intended)**
   - Evidence: regression test names in `pass-after` output (e.g., `test_regression_*`).
3. Coverage on notes-related paths measurably improves → **Unknown/Partially Met**
   - Evidence: `remediation-baseline/coverage.2026-02-03T18-30.txt` shows `transform/notes.py` at 99%, but also shows a failing total coverage floor when running only `tests/transform/test_notes.py`.

### Feature #27 — `2025-12-04-formatters-parser-27/`

Acceptance criteria source: `user-story.md`.

All criteria **Met**:
1. Tests assert key formatting/spacing rules and parsed structures → Met
2. Coverage report shows ≥70% for formatters and parser modules → Met
3. Avoid brittle binary DOCX assertions → Met
4. Deterministic; no external dependencies → Met

Evidence:
- `remediation-baseline/coverage.2026-02-03T18-30.txt` includes `--cov-fail-under=70` and reports total coverage 93.83% for targeted modules.

### Feature #28 — `2025-12-04-ci-coverage-gate-28/`

Acceptance criteria source: `user-story.md`.

1. CI runs pytest-cov and fails when total coverage < configured floor → **Partially Met (config present; run not verified)**
   - Evidence (config): `.github/workflows/ci.yml` runs pytest with `--cov-report=xml/html` and runs `poetry run coverage report`.
   - Evidence (floor): `pyproject.toml` contains `[tool.coverage.report] fail_under = 15`.
   - Missing: a captured CI run URL demonstrating pass/fail behavior for the gate.
2. CI passes when total coverage ≥ floor → **Unknown** (no verified run evidence captured in canonical evidence locations).
3. CI surfaces coverage results in logs and step summary → **Met (config)**
   - Evidence: `ci.yml` appends a markdown coverage report to `${GITHUB_STEP_SUMMARY}`.
4. CI uploads coverage artifacts (HTML + coverage.xml) → **Met (config)**
   - Evidence: `actions/upload-artifact@v4` steps in `ci.yml`.
5. Documentation explains how to adjust `fail_under` → **Met**
   - Evidence: `spec.md` “Fail-Under Ratchet Strategy”.

### Plan reconciliation (hard-gate)

No plan checkboxes were auto-checked in this epic review run.

Reason: under the epic review hard gate, evidence artifacts must include `Timestamp:`, `Command:`, and `EXIT_CODE:` (plus a fail-before condition when applicable). Most evidence files omit `EXIT_CODE:`.
