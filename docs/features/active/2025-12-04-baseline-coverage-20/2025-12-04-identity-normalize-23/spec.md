# 2025-12-04-identity-normalize — Spec

- **Issue:** [#23](https://github.com/drmoisan/transcript-etl-pipeline/issues/23)
- **Parent (optional):** none
- **Owner:** drmoisan
- **Last Updated:** 2026-02-02T12-45
- **Status:** Draft
- **Version:** 0.1

## Overview

Add targeted Pytest unit coverage for identity constraint extraction and text normalization to prevent regressions in `src/transcript_etl_pipeline/transform/identity_constraints.py` and `src/transcript_etl_pipeline/transform/normalize.py`.

- Target users/personas and primary use cases: Maintainers and contributors validating name extraction, constraint application, and normalization edge cases without altering production behavior.
- Success metrics or expected impact: Combined coverage for the two modules reaches $\ge 75\%$, and tests explicitly assert expected constraints and normalized outputs for tricky inputs.

## Behavior

Tests codify existing logic in `detect_self_identification`, `detect_addresses_to_person`, `extract_identity_constraints`, and `normalize_text` without changing implementation.

- Main user flow (happy path): Pytest runs new unit tests in `tests/transform/` that verify self-identification patterns (e.g., "I'm Name"), direct address patterns (e.g., "Thanks Name"), and normalization rules (line endings, whitespace, labels).
- Alternate/edge flows: Tests cover exclusion rules for questions like "Is Name a...", standalone "Name?" questions, mid-sentence "is Name a..." cases, and whitespace/punctuation normalization edge cases.
- Error handling and recovery behavior: Tests verify deterministic outputs for tricky inputs without filesystem or network dependencies.

## Inputs / Outputs

- Inputs (CLI flags, files, env vars): In-memory strings and sentence lists provided by unit tests; no CLI flags, files, or env vars required.
- Outputs (artifacts, logs, telemetry): Pytest assertions and coverage reports from the existing test toolchain.
- Config keys and defaults: None.
- Versioning or backward-compatibility constraints: No public API changes; tests only.

## API / CLI Surface

No public API or CLI changes.

- Example invocations with expected outputs (concise): `poetry run pytest tests/transform/` runs unit tests for identity and normalization behavior.
- Contracts and validation rules: Tests assert exact constraint lists from `extract_identity_constraints` and normalized text outputs from `normalize_text` for specified inputs.

## Data & State

No new data storage or state.

- Data transformations and invariants: Tests verify that normalization enforces CRLF line endings, cleans whitespace, and normalizes labels; identity extraction respects inclusion/exclusion rules for direct address and self-identification.
- Caching or persistence details: None.
- Migration or backfill requirements (if any): None.

## Constraints & Risks

Tests must be deterministic, isolated, and avoid filesystem/temp files per unit-test policy.

- Limits (latency/throughput/memory) and acceptable trade-offs: Keep test inputs small and focused to avoid slow execution.
- Security/privacy considerations: No external services or sensitive data.
- Operational/rollout risks and mitigations: Risk of ambiguous inputs; mitigate by encoding expected behavior in assertions.

## Implementation Strategy

- Implementation scope (what changes, not sequencing): Add unit tests in `tests/transform/` for identity constraint extraction and text normalization edge cases.
- New classes/functions/commands to add or update: New Pytest test functions covering `detect_self_identification`, `detect_addresses_to_person`, `extract_identity_constraints`, `_normalize_line_endings`, `_clean_whitespace`, `_normalize_labels`, and `normalize_text`.
- Dependency changes (new/removed packages) and rationale: None.
- Logging/telemetry additions and locations: None.
- Rollout plan (feature flags, staged deploys, fallback path): Not applicable; tests only.

## Definition of Done

- [ ] Acceptance criteria documented and mapped to tests or demos (link test names in `tests/transform/`).
- [ ] Behavior matches acceptance criteria in all documented environments (local runs per `docs/developer-tooling.md`).
- [ ] Tests updated/added (unit/integration as applicable) in `tests/transform/` with identity/normalize coverage.
- [ ] Edge cases and error handling covered by tests (direct address exclusions, label normalization, whitespace handling).
- [ ] Docs updated (README, docs/features/active/... links) if any test/coverage guidance changes.
- [ ] Telemetry/logging added or updated (if applicable) — not applicable for test-only changes.
- [ ] Toolchain pass completed (format → lint → type-check → test) per `docs/developer-tooling.md`.
