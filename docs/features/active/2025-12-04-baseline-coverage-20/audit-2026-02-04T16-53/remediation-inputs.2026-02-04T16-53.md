# Remediation Inputs: 2025-12-04-baseline-coverage-20

Timestamp: 2026-02-04T16-53
EpicRootFolder: `docs/features/active/2025-12-04-baseline-coverage-20/`

## Why remediation is required

The epic-review hard gates prohibit auto-checking plan items and treating evidence as audit-complete unless evidence artifacts contain machine-checkable fields:
- `Timestamp: <ISO-8601>`
- `Command: <exact command>`
- `EXIT_CODE: <int>`

Additionally, “fail-before” expectations require either a recorded failing run (`EXIT_CODE != 0`) or an approved **Fail-before Exception Dossier** (with required schema).

## Delivery gaps / policy gaps (must fix)

### R1 — Evidence artifacts missing `EXIT_CODE:` (hard-gate blocker)

**Scope:** Most features (#21, #22, #23, #24, #25, #26, #27) have coverage/QA artifacts missing `EXIT_CODE:`.

**Done definition:** For each feature, at least one canonical evidence artifact per required command includes `EXIT_CODE: 0` (and, when appropriate, a failing command with `EXIT_CODE != 0`).

**Where:** Prefer updating/adding files under each feature’s `remediation-baseline/` directory (canonical location).

**Suggested standard format (top of file):**
- `Timestamp: ...`
- `Command: ...`
- `EXIT_CODE: 0`

### R2 — #26 fail-before dossier not schema-compliant

**Current file:** `2025-12-04-notes-regressions-26/remediation-baseline/fail-before.2026-02-03T18-30.md`

**Problem:** Narrative-only; missing required machine-checkable fields and absence-of-test proof.

**Done definition:** Create a Fail-before Exception Dossier that includes:
- `BaselineCommit: <SHA>`
- `Timestamp: <ISO-8601>`
- `Command: <exact command(s)>` (e.g., `git show`, `git grep`, `poetry run pytest -k <test>` on baseline)
- `EXIT_CODE: <int>` for each command
- Output proving absence of the regression tests at baseline (e.g., `git grep` not finding test names)
- `WhyFailingRunImpossible:` and `AlternativeProof:`

### R3 — Feature #28 remediation evidence contradicts repo state

**Current file:** `2025-12-04-ci-coverage-gate-28/remediation-baseline/ci-run.2026-02-03T18-30.md`

**Problem:** Claims `.github/workflows/ci.yml` does not exist; it does.

**Done definition:** Update evidence to:
- reflect actual workflow behavior (pytest-cov + coverage report + artifact upload + step summary)
- include at least one CI run URL that shows coverage artifacts uploaded and the coverage report step executed
- optionally: a demonstration of failure when `fail_under` is temporarily raised (document-only if not changing repo state)

### R4 — Python suppression policy risk (`type ignore attr-defined`)

**Files:**
- `tests/integration/test_cli_e2e_notes.py`
- `tests/integration/test_cli_e2e_speakerless.py`

**Problem:** `type ignore attr-defined` is not a pre-authorized suppression pattern.

**Done definition:** Either:
- remove the ignores by typing the `Document.sections` access correctly, or
- obtain explicit approval for these ignores and add compliant justification per policy (least preferred).

## Do-not-do list (scope guardrails)

- Do not widen scope into algorithm changes for speaker assignment/grouping.
- Do not refactor unrelated modules while updating evidence artifacts.
- Do not weaken repo policies or add broad suppressions.
- Do not check off plan items unless evidence meets the hard-gate schema.

## Plan-of-record note

Prior remediation plans exist under:
- `audit-2026-02-02T15-20/remediation-plan.2026-02-02T15-20.md`
- `audit-2026-02-03T16-10/remediation-plan.2026-02-03T16-10.md`
- `audit-2026-02-03T18-30/remediation-plan.2026-02-03T18-30.md`

The new remediation plan should carry forward any still-open tasks from the latest plan, but must focus on the hard-gate blockers above.
