---
name: evidence-and-timestamp-conventions
description: 'Evidence storage and timestamp naming conventions for audits and remediation. Use when storing baseline/regression/QA evidence or naming audit artifacts with ISO-8601 timestamps.'
---

# Evidence and Timestamp Conventions

Reusable conventions for evidence storage locations and ISO-8601 timestamped artifacts.

## When to Use This Skill

Use this skill when:
- You create audit or remediation artifacts that must be timestamped.
- You store baseline, regression, or QA evidence under canonical folders.
- Multiple agents need the same naming and evidence-location rules.

## ISO-8601 Timestamp Format

Use `yyyy-MM-ddTHH-mm` for all audit, remediation, and evidence artifacts.
Example: `2026-02-06T14-30`.

## Canonical Evidence Locations

- Baseline evidence: `evidence/baseline/`
- Regression testing evidence: `evidence/regression-testing/`
- Other QA gate evidence: `evidence/qa-gates/`
- Issue update mirrors: `evidence/issue-updates/`

Epic rollups may mirror these under the epic root when needed.

## Canonical Evidence Discovery Order

When locating evidence artifacts for audits or plan reconciliation, use this order:

1) `<FEATURE>/evidence/issue-updates/` (issue update mirrors)
2) `<FEATURE>/evidence/regression-testing/`
3) `<FEATURE>/evidence/qa-gates/`
4) `<FEATURE>/evidence/baseline/`
5) `<FEATURE>/evidence/remediation-baseline/`
6) `<EPIC>/evidence/issue-updates/` (issue update mirrors)
7) `<EPIC>/evidence/regression-testing/` (optional rollup)
8) `<EPIC>/evidence/qa-gates/` (optional rollup)
9) `<EPIC>/evidence/baseline/` (optional rollup)
10) `<EPIC>/evidence/remediation-baseline/` (optional rollup)

Rule:
- Use the list order by default for audit fidelity.
- If the task is explicitly remediation reconciliation, you may prefer `remediation-baseline` over `baseline`, but still record the original baseline as the authoritative audit reference.

If evidence or issue-update mirrors are found elsewhere, record it as non-canonical and include a remediation step to move/copy it into the first applicable canonical location.

## Evidence Artifact Schema (Machine-Checkable)

When evidence artifacts are used for automated checking or plan reconciliation, include:
- `Timestamp: <ISO-8601>`
- `Command: <exact command>`
- `EXIT_CODE: <int>`

If a fail-before run is required but impossible, include a short exception dossier with:
- `WhyFailingRunImpossible: <1–3 sentences>`
- An alternative proof section (e.g., absence-of-test proof)

Fail-before exception dossiers should be stored under `evidence/regression-testing/`.

## Evidence-First Audit Writing

When marking FAIL or PARTIAL in audit artifacts, include:
- Concrete file + location (line/hunk/section when possible)
- The violated rule or expected behavior
- The verification command and its output (or why it could not be run)

## Issue Update Mirroring (Canonical Location)

When work involves updating a GitHub issue, create a local mirror artifact at:
- `<FEATURE>/evidence/issue-updates/issue-<N>.<timestamp>.md`

Required contents:
- `Timestamp: <ISO-8601>`
- The exact text intended/posted
- `PostedAs: body` or `PostedAs: comment` (preferred), or `PostedAs: unknown`
- If posted as a comment: the GitHub URL to the comment
- If posted as an issue body update: the GitHub URL to the issue and `IssueUpdatedAt: <ISO-8601>`
- If not posted: a `POSTING BLOCKED` header and the reason

If `PostedAs: body`, mirror the same update into the local feature `issue.md` (current version folder if present; otherwise feature root).
