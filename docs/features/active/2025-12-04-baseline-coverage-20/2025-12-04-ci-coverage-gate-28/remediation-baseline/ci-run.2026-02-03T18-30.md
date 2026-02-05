# CI Run Evidence for Issue #28

**Date:** 2026-02-03T18:30 (captured)

## Status

Issue #28 is for adding a CI coverage gate. The repository does not currently have a ci.yml workflow that runs quality checks with coverage enforcement.

## Current CI Configuration

**Available Workflows:**
- Codex Web Setup (active, ID: 229853623)
- Copilot coding agent (active, ID: 208991571)

**Recent Run:** 
- Run ID: 21615784014
- URL: https://github.com/drmoisan/transcript-etl-pipeline/actions/runs/21615784014
- Event: pull_request
- Status: completed (failure)
- Created: 2026-02-03T03:30:33Z
- Workflow: Codex Web Setup
- Title: "Improve parser metadata handling, add in-memory formatter/notes tests, and update baseline coverage docs"

This run does not include coverage checks or quality gates. The run failed at the "Run codex-web setup script" step.

## Implementation Plan

Per Issue #28 specification, the following needs to be implemented:

1. **Add `.github/workflows/ci.yml`** with:
   - Pytest-cov invocation with coverage reporting
   - Configurable fail_under threshold from pyproject.toml
   - Coverage summary in CI logs
   - GitHub Actions step summary with coverage table
   - Upload HTML/XML coverage artifacts

2. **Configure coverage threshold** in `pyproject.toml`:
   - Initial floor: `fail_under = 15` (aligned to baseline ~16%)
   - Ratchet upward as coverage improves per milestone completion

3. **Expected CI behavior:**
   - Job fails when total coverage < fail_under threshold
   - Coverage artifacts uploaded to CI run
   - Coverage summary visible in logs and step summary

## Validation Criteria

Once ci.yml is implemented, validate:
- [ ] CI runs pytest with coverage flags
- [ ] CI fails when coverage is below threshold
- [ ] CI passes when coverage meets/exceeds threshold
- [ ] Coverage HTML/XML artifacts are uploaded
- [ ] GitHub Actions step summary shows coverage table

## References

- Issue: https://github.com/drmoisan/transcript-etl-pipeline/issues/28
- Spec: docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-ci-coverage-gate-28/spec.md
- Current workflows: https://github.com/drmoisan/transcript-etl-pipeline/actions

---
EvidenceSchemaAddendum:
Timestamp: 2026-02-05T02:54:58Z
Command: documentation-only
EXIT_CODE: 0
Superseded by: ci-run.2026-02-04T16-53.md
