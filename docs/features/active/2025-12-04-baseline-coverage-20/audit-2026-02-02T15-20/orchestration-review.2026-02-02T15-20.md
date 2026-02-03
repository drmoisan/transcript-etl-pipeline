# Orchestration Review — 2025-12-04-baseline-coverage-20

Timestamp: 2026-02-02T15-20

## Orchestration summary

`orchestration.md` defines parallel tracks for #21/#22/#23/#27/#28, with #24 coordinating with #22, and #25/#26 proceeding in parallel with #24. This remains a reasonable dependency layout for coverage work and reduces critical-path bottlenecks.

## Cross-check against feature plans

- **Parallelization alignment:** Feature plans for #21/#22/#23/#27/#28 exist and do not declare hard dependencies that contradict the orchestration sequence.
- **Dependency declarations:**
  - #24 depends on shared heuristics inputs from #22 (aligned).
  - #25 references fixtures from #24 (aligned).
  - #26 is independent (aligned).
- **Status mismatch:** `initiative.md` claims M1 “complete issues #24–#27,” but plans for #24–#27 remain “Planned” or “Draft.” This is a sequencing/reporting inconsistency.

## Integration & rollout concerns

1. **Test policy conflict (temporary files + external downloads)**
   - Evidence: `tests/integration/test_cli_e2e_*.py` and formatter tests use `tmp_path`/`tempfile`; `tests/transform/test_speaker_helpers.py` calls `ensure_nltk_data()` which may download.
   - Impact: Unit-test policy violation blocks merge readiness.
   - Action: Replace filesystem/network usage with in-memory stubs or document an approved exception.

2. **Coverage gate sequencing criteria not explicit**
   - Evidence: `orchestration.md` suggests sequencing, but no explicit ratchet thresholds tied to milestones.
   - Impact: Gate increases could block progress or be delayed without measurable criteria.
   - Action: Add explicit coverage gate ratchet criteria tied to delivery milestones.

3. **MVP delivery gaps despite CI gate presence**
   - Evidence: CI coverage gate exists in `.github/workflows/ci.yml` and `pyproject.toml`, but core module coverage targets for #21–#23 are not met (coverage.xml shows line-rate < 0.50).
   - Impact: CI gate is present but MVP coverage objectives are not achieved.
   - Action: Complete tests and coverage targets before advancing gate thresholds.

## Verdict

**NEEDS REVISION** — Dependency layout is coherent, but delivery gaps, policy conflicts, and status mismatches require resolution before merge readiness.
