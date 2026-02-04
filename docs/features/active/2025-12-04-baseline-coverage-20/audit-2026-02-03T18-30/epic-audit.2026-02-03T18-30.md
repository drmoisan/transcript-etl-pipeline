# Epic Audit — 2025-12-04-baseline-coverage-20

**Audit Date:** 2026-02-03  
**Epic Root:** `docs/features/active/2025-12-04-baseline-coverage-20/`

## Executive Summary

- **Resource lockup clarity:** ⚠️ PARTIAL — No explicit capacity/effort envelope or timeline in `initiative.md`.
- **Objective + scope clarity:** ✅ PASS — Scope and module targets are explicit in `initiative.md`.
- **Sequencing + dependency clarity:** ✅ PASS — Sequencing and dependencies are explicit in `orchestration.md`.
- **Overall readiness:** ❌ **BLOCKED** — Multiple feature acceptance criteria and plan items remain incomplete; evidence gaps are blocking.

## Work Planning Checklist (Audit-Grade)

| Requirement | Status | Evidence | Missing / Gaps |
| --- | --- | --- | --- |
| Objective / outcome (specific & testable) | ✅ PASS | `initiative.md` Goal & Outcomes; module list + targets | None |
| Stakeholders / users | ⚠️ PARTIAL | Implicit maintainer/contributor focus across feature docs | Not explicitly named at epic level |
| Proposed approach + tradeoffs | ⚠️ PARTIAL | High-level approach in `initiative.md` | No explicit alternatives/tradeoffs recorded |
| Scope boundaries (“in/out”, done) | ✅ PASS | MVP scope and module targets in `initiative.md` | None |
| Success signals / quality gates | ⚠️ PARTIAL | Coverage targets and gate sequencing in `initiative.md` + `orchestration.md` | Evidence is stale; CI run evidence missing |
| Effort / capacity envelope | ❌ FAIL | None | No timebox, resourcing, or availability stated |
| Risks + mitigations | ⚠️ PARTIAL | Risks implied (coverage low, avoid blocking) | Explicit mitigations not cataloged |
| Dependencies + sequencing gates | ✅ PASS | `orchestration.md` sequencing and ratchet criteria | None |

## Scope & Delivery Mapping

**Primary objective:** raise test coverage on core logic without blocking on CLI/UI parity, with gating once baseline improves.

**Feature mapping:**
- Core transform tests: #21 (enhance), #22 (speakerless heuristics), #23 (identity/normalize)
- Regression/fixtures: #24 (multi-speaker fixtures), #26 (notes regressions)
- Integration/E2E: #25 (CLI speakerless + notes)
- Formatters/parser: #27
- CI coverage gate: #28

**Gaps:**
- Evidence of coverage improvements and CI gating runs is stale or missing.
- Several plan items remain unchecked for #24–#28.

## Delivery-Quality Risks (Top 5)

1. **Incomplete acceptance criteria across multiple features** → blocks readiness.  
   _Fix direction:_ Close remaining plan items and update issue evidence for #21–#28.
2. **Coverage evidence is stale or unverified** → cannot support gating decisions.  
   _Fix direction:_ Capture baseline and post-change toolchain outputs in canonical `baseline/` locations and update feature docs.
3. **Issue updates missing for several features** → audit trail incomplete.  
   _Fix direction:_ Update issues #21–#28 with coverage/test evidence.
4. **E2E CLI coverage incomplete** (#25) → integration risks remain.  
   _Fix direction:_ Complete remaining test scenarios (panel DOCX, additional MD/RTF cases, update-file reader path).
5. **Documentation gaps for coverage gate ratchet** (#28) → policy ambiguity.  
   _Fix direction:_ Update feature docs with `fail_under` ratchet guidance and evidence.

## Feature Delivery Status

| Issue | Feature | Plan Status | Coverage Status | QA Status | Acceptance Criteria Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| #21 | Enhance core tests | 0/3 tasks complete | [coverage.2026-02-03T18-30.txt](2025-12-04-enhance-tests-21/remediation-baseline/coverage.2026-02-03T18-30.txt) | Not yet captured | Partial (implicit) | Core transform test enhancements |
| #22 | Speakerless heuristics | 0/6 tasks complete | [coverage.2026-02-03T18-30.txt](2025-12-04-speakerless-heuristics-22/remediation-baseline/coverage.2026-02-03T18-30.txt) | [Black](2025-12-04-speakerless-heuristics-22/remediation-baseline/qa-black.2026-02-03T18-30.txt), [Ruff](2025-12-04-speakerless-heuristics-22/remediation-baseline/qa-ruff.2026-02-03T18-30.txt), [Pyright](2025-12-04-speakerless-heuristics-22/remediation-baseline/qa-pyright.2026-02-03T18-30.txt), [Pytest](2025-12-04-speakerless-heuristics-22/remediation-baseline/qa-pytest.2026-02-03T18-30.txt) | Partial (implicit) | Speakerless transformation logic tests |
| #23 | Identity normalization | 0/5 tasks complete | [coverage.2026-02-03T18-30.txt](2025-12-04-identity-normalize-23/remediation-baseline/coverage.2026-02-03T18-30.txt) | [Black](2025-12-04-identity-normalize-23/remediation-baseline/qa-black.2026-02-03T18-30.txt), [Ruff](2025-12-04-identity-normalize-23/remediation-baseline/qa-ruff.2026-02-03T18-30.txt), [Pyright](2025-12-04-identity-normalize-23/remediation-baseline/qa-pyright.2026-02-03T18-30.txt), [Pytest](2025-12-04-identity-normalize-23/remediation-baseline/qa-pytest.2026-02-03T18-30.txt) | Partial (implicit) | Speaker identity and normalization tests |
| #24 | Multi-speaker fixtures | 4/5 tasks complete | [coverage.2026-02-03T18-30.txt](2025-12-04-multi-speaker-fixtures-24/remediation-baseline/coverage.2026-02-03T18-30.txt) | [Black](2025-12-04-multi-speaker-fixtures-24/remediation-baseline/qa-black.2026-02-03T18-30.txt), [Ruff](2025-12-04-multi-speaker-fixtures-24/remediation-baseline/qa-ruff.2026-02-03T18-30.txt), [Pyright](2025-12-04-multi-speaker-fixtures-24/remediation-baseline/qa-pyright.2026-02-03T18-30.txt), [Pytest](2025-12-04-multi-speaker-fixtures-24/remediation-baseline/qa-pytest.2026-02-03T18-30.txt) | Partial (implicit) | Multi-speaker test fixtures and data |
| #25 | E2E CLI speakerless + notes | 3/4 tasks complete | [coverage.2026-02-03T18-30.txt](2025-12-04-e2e-speakerless-notes-25/remediation-baseline/coverage.2026-02-03T18-30.txt) | Not yet captured | Partial (implicit) | End-to-end CLI integration tests |
| #26 | Notes regression tests | 0/3 tasks complete | [coverage.2026-02-03T18-30.txt](2025-12-04-notes-regressions-26/remediation-baseline/coverage.2026-02-03T18-30.txt) | [Black](2025-12-04-notes-regressions-26/remediation-baseline/qa-black.2026-02-03T18-30.txt), [Ruff](2025-12-04-notes-regressions-26/remediation-baseline/qa-ruff.2026-02-03T18-30.txt), [Pyright](2025-12-04-notes-regressions-26/remediation-baseline/qa-pyright.2026-02-03T18-30.txt), [Pytest](2025-12-04-notes-regressions-26/remediation-baseline/qa-pytest.2026-02-03T18-30.txt) | Partial (implicit) | Notes transformation regression coverage |
| #27 | Formatters/parser tests | 3/4 tasks complete | [coverage.2026-02-03T18-30.txt](2025-12-04-formatters-parser-27/remediation-baseline/coverage.2026-02-03T18-30.txt) | [Black](2025-12-04-formatters-parser-27/remediation-baseline/qa-black.2026-02-03T18-30.txt), [Ruff](2025-12-04-formatters-parser-27/remediation-baseline/qa-ruff.2026-02-03T18-30.txt), [Pyright](2025-12-04-formatters-parser-27/remediation-baseline/qa-pyright.2026-02-03T18-30.txt), [Pytest](2025-12-04-formatters-parser-27/remediation-baseline/qa-pytest.2026-02-03T18-30.txt) | Partial (implicit) | Formatters and parser module coverage |
| #28 | CI coverage gate | 2/5 tasks complete | [ci-run.2026-02-03T18-30.md](2025-12-04-ci-coverage-gate-28/remediation-baseline/ci-run.2026-02-03T18-30.md) | Not yet captured | Partial (implicit) | CI enforcement of 80% coverage threshold |
