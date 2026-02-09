# Policy Compliance Audit: 2025-12-04-baseline-coverage-20 (Epic review)

Audit Date: 2026-02-04
Timestamp: 2026-02-04T16-53
Scope: Documentation + evidence audit only (no new code changes were made as part of this epic review run).

## Executive summary

This audit evaluates policy compliance signals relevant to the baseline coverage epic (#20), focusing on:
- presence/quality of test evidence artifacts under `remediation-baseline/` folders
- compliance with the epic review hard-gate schema for auto-checking plan items
- policy risks that could block future agent-driven changes (e.g., suppression rules)

**Overall status:** **PARTIAL**
- Core tests and coverage evidence exist for many features, but evidence artifacts are not consistently machine-checkable (missing `EXIT_CODE:`).
- At least one non-preauthorized `# type: ignore[...]` was found in test code.

Policy documents evaluated:
- ✅ `general-code-change.instructions.md`
- ✅ `general-unit-test.instructions.md`
- ✅ `python-code-change.instructions.md`
- ✅ `python-unit-test.instructions.md`
- ✅ `python-suppressions.instructions.md`

## Evidence sources used (canonical-first)

Per-feature evidence was taken from:
- `docs/features/active/2025-12-04-baseline-coverage-20/*/remediation-baseline/`
- `docs/features/active/2025-12-04-baseline-coverage-20/*/issue-updates/`

## 1) General unit test policy (audit view)

### Independence / Isolation / Determinism

Status: **Reported PASS** (but not fully Verified under the epic hard gate).

Evidence examples:
- Feature #22 coverage run output (deterministic unit tests):
  - File: `2025-12-04-speakerless-heuristics-22/remediation-baseline/coverage.2026-02-03T18-30.txt`
  - Contains: `Timestamp:` + `Command:` + full pytest output (155 passed)
  - Missing: `EXIT_CODE:` (hard-gate requirement)

### Avoid external dependencies and temp files

Status: **PASS (spot-verified by inspection for key integration tests)**

Evidence:
- `tests/integration/test_cli_e2e_notes.py` and `tests/integration/test_cli_e2e_speakerless.py` run the CLI entrypoint in-process and monkeypatch I/O paths to avoid writing temp files.

## 2) General code change policy (audit view)

This epic review run did not implement code changes. Therefore the “toolchain loop” requirement is **N/A for this run**.

However, multiple features store tool outputs that appear to represent Black/Ruff/Pyright/Pytest runs. Many of these artifacts are missing the required structured fields for audit-grade verification.

## 3) Python suppression policy (blocking risk)

Status: **FAIL (policy risk found)**

Evidence:
- `tests/integration/test_cli_e2e_notes.py` contains `type ignore attr-defined` markers.
- `tests/integration/test_cli_e2e_speakerless.py` contains `type ignore attr-defined` markers.

Per `python-suppressions.instructions.md`, `# type: ignore[...]` suppressions must match a pre-authorized pattern (or have explicit user approval). `attr-defined` is not listed as pre-authorized.

Recommended remediation:
- Remove these suppressions by tightening types (preferred), or
- Obtain explicit approval and document an authorized pattern (least preferred).

## 4) Epic-review evidence schema compliance (hard gate)

Status: **FAIL**

Reason:
- Most remediation-baseline artifacts include `Timestamp:` and `Command:` but do **not** include `EXIT_CODE:`.
- Example: `2025-12-04-formatters-parser-27/remediation-baseline/coverage.2026-02-03T18-30.txt` includes timestamp and command, but no exit code line.

Impact:
- Plan checkbox reconciliation cannot be done automatically under the epic-review agent rules.

## 5) Summary of required follow-ups (policy-driven)

1. Standardize evidence artifacts with `EXIT_CODE:` fields in each feature’s `remediation-baseline/`.
2. Replace/augment #26 fail-before narrative with a machine-checkable Fail-before Exception Dossier.
3. Resolve/test or remove non-preauthorized `type ignore attr-defined` suppressions.
4. Update #28 remediation-baseline evidence to match the repo state and include verified CI run evidence.
