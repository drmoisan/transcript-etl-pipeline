# Epic Audit: 2025-12-04-baseline-coverage-20 (Issue #20)

Timestamp: 2026-02-04T16-53
EpicRootFolder: `docs/features/active/2025-12-04-baseline-coverage-20/`

## Executive summary

This epic’s planning artifacts (`initiative.md`, `issue.md`, `orchestration.md`) are coherent and actionable for a single developer, with clear scope boundaries and a sensible sequencing model across child features #21–#28.

Delivery verification is **not audit-complete** under the epic-review hard gates because the majority of “evidence” artifacts do not include a machine-checkable `EXIT_CODE:` field, and at least one fail-before dossier does not meet the required schema.

**Readiness verdict:** **NEEDS REVISION** (evidence hygiene + a small number of doc/evidence inconsistencies)

### PASS / PARTIAL / FAIL snapshot

| Dimension | Status | Evidence |
| --- | --- | --- |
| Resource lockup clarity | **PASS** | `initiative.md` includes a 0.5–1.0 FTE, 2–3 week envelope and review capacity estimate. |
| Objective + scope clarity | **PASS** | `initiative.md` explicitly scopes to core transform + formatter/parser modules, defers full CLI/UI parity. |
| Sequencing + dependency clarity | **PASS** | `orchestration.md` enumerates parallel tracks and ratchet sequencing tied to milestones. |
| Delivery evidence quality (hard-gate compliance) | **FAIL** | Coverage/test artifacts frequently lack `EXIT_CODE:`; fail-before dossier for #26 is missing required machine-checkable fields. |
| Cross-doc coherence | **PARTIAL** | Feature #28 remediation evidence claims `ci.yml` is missing, but repo contains `.github/workflows/ci.yml`. |

## Work-planning checklist (single-developer audit)

| Requirement | Status | Evidence / Notes |
| --- | --- | --- |
| Objective / outcome is specific and testable | PASS | `initiative.md` “Goal & Outcomes” + module target table. |
| Stakeholders/users identified | PASS | `initiative.md` “Stakeholders & Users”. |
| Scope boundaries (in/out) defined | PASS | `initiative.md` “MVP Scope & Metrics” + constraints. |
| Sequencing and dependencies explicit | PASS | `orchestration.md` + “Dependencies” section in `initiative.md`. |
| Success signals / quality gates | PARTIAL | Targets are defined, but the epic review’s evidence schema requirements are not consistently met by stored artifacts (blocks checklist reconciliation). |
| Effort/capacity envelope | PASS | `initiative.md` “Resource Lockup”. |
| Risks + mitigations | PASS | `initiative.md` “Risks & Mitigations”. |

## Scope → delivery mapping

Primary epic intent (from `initiative.md`): raise coverage on core transform/formatter/parser logic and enforce regression prevention.

| Epic objective slice | Primary delivering child features |
| --- | --- |
| Core transform coverage (enhance / identity / normalize) | #21, #23 |
| Speakerless heuristic regression protection | #22 |
| Multi-speaker fixtures + regression harness | #24 |
| CLI integration safety net for speakerless + notes | #25 |
| Notes edge-case regression suite | #26 |
| Parser + formatters unit coverage | #27 |
| CI coverage gate + reporting | #28 |

## Top delivery-quality risks (blocking / near-blocking)

1. **Evidence artifacts are not auto-check eligible (missing `EXIT_CODE:` field)**
   - Why it matters: plan checkbox reconciliation is explicitly blocked by the epic review hard gate.
   - Smallest fix: standardize evidence artifacts in each feature’s `remediation-baseline/` to include:
     - `Timestamp: <ISO-8601>`
     - `Command: <exact command>`
     - `EXIT_CODE: <int>`

2. **Fail-before evidence for “new regression tests” is not in the approved dossier schema**
   - Evidence: #26 `remediation-baseline/fail-before.2026-02-03T18-30.md` is narrative-only (no `Timestamp/Command/EXIT_CODE`).
   - Smallest fix: replace/augment with a “Fail-before Exception Dossier” that includes machine-checkable fields and an absence-of-test proof (e.g., `git grep` results at the baseline commit).

3. **Feature #28 evidence contradicts the repo state**
   - Evidence: `2025-12-04-ci-coverage-gate-28/remediation-baseline/ci-run.2026-02-03T18-30.md` claims `.github/workflows/ci.yml` does not exist.
   - Repo reality: `.github/workflows/ci.yml` exists and runs pytest with coverage + uploads artifacts.
   - Smallest fix: update #28 remediation-baseline evidence to reflect current configuration and include a CI run URL that demonstrates threshold behavior.

4. **Repo suppression policy risk: non-preauthorized `# type: ignore[...]` in tests**
   - Evidence: `tests/integration/test_cli_e2e_notes.py` and `tests/integration/test_cli_e2e_speakerless.py` contain `type ignore attr-defined` markers.
   - Why it matters: per `python-suppressions.instructions.md`, non-preauthorized `type: ignore` codes require explicit approval.
   - Smallest fix: remove the ignores by tightening types (prefer) or document/approve a compliant suppression pattern.

5. **Coverage evidence is inconsistent across features (some runs are global and fail-under sensitive)**
   - Example: #26 `remediation-baseline/coverage.2026-02-03T18-30.txt` shows `transform/notes.py` at 99% but a failing total-coverage floor when running a narrow subset.
   - Smallest fix: standardize on module-scoped coverage commands for feature evidence (avoid global fail-under failures in subset runs), and capture the final full-suite coverage separately at the epic level.
