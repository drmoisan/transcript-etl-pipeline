# multi-speaker-fixtures — Spec

- **Issue:** #24
- **Parent (optional):** N/A
- **Owner:** Dan Moisan
- **Last Updated:** 2026-02-02T00-00
- **Status:** In Progress
- **Version:** 1.0

## Overview

Add reusable 3+ speaker transcript fixtures plus regression tests that validate grouping and speaker assignment behavior for speakerless and helper logic (e.g., SpaceX discussion).
- Target users/personas and primary use cases: Maintainers and contributors writing or debugging grouping logic who need deterministic, shared fixtures and regression coverage.
- Success metrics or expected impact: Fixture reuse across test suites; regression tests capture known failures and prevent reintroductions.

## Behavior

Regression tests consume shared multi-speaker fixtures to validate expected grouping behavior.
- Main user flow (happy path): Pytest loads fixtures from `tests/fixtures/multi_speaker.py`, runs `tests/transform/test_multi_speaker_regression.py`, and asserts expected speaker labeling, grouping, and content preservation for 3+ speaker inputs.
- Alternate/edge flows: Known gaps are captured with `xfail` tests to document limitations without breaking CI; fixtures span 3- and 4-speaker scenarios.
- Error handling and recovery behavior: Malformed fixture definitions or incorrect grouping outputs fail fast with clear assertions in fixture-validation and regression tests.

## Inputs / Outputs

- Inputs (CLI flags, files, env vars): Pytest invocation; fixture data embedded in `tests/fixtures/multi_speaker.py`.
- Outputs (artifacts, logs, telemetry): Pytest test results; standard test logs only.
- Config keys and defaults: None.
- Versioning or backward-compatibility constraints: Test-only change; no runtime API changes.

## API / CLI Surface

Test-only surface (Pytest).
- Example invocations with expected outputs (concise): `poetry run pytest tests/transform/test_multi_speaker_regression.py` → tests pass with documented `xfail` cases.
- Contracts and validation rules: Fixtures expose `MultiSpeakerFixture` data with `input_text`, `expected_lines`, and `num_speakers` ≥ 3; helper `get_fixture_by_name` provides name-based lookup for parametrized tests.

## Data & State

Fixture data is defined in-code and consumed by tests; no persistence or runtime state changes.
- Data transformations and invariants: Fixtures define expected speaker/content pairs; tests assert consistent ordering and count invariants.
- Caching or persistence details: None.
- Migration or backfill requirements (if any): None.

## Fixture Ownership & Reuse Governance

- **Owner:** The fixtures in `tests/fixtures/multi_speaker.py` are owned by the baseline coverage initiative owner (currently the #24 feature owner).
- **Update process:** Changes to existing fixtures require updating dependent tests and documenting the reason in the fixture docstring or issue note. Prefer additive changes; avoid breaking existing fixture contracts without a migration note.
- **Reuse rules:** Other tests should import fixtures via `get_fixture_by_name` or shared constants rather than duplicating text. When a new fixture is needed, add it to the shared module and reuse across suites.

## Constraints & Risks

- Limits (latency/throughput/memory) and acceptable trade-offs: Tests must stay fast; fixtures should remain compact.
- Security/privacy considerations: Fixtures must be synthetic and avoid sensitive or proprietary content.
- Operational/rollout risks and mitigations: Overly strict expectations can make tests brittle; mitigate by scoping assertions to stable grouping outcomes and documenting known gaps via `xfail`.

## Implementation Strategy

- Implementation scope (what changes, not sequencing): Add shared multi-speaker fixtures and regression tests covering grouping behavior for 3+ speakers.
- New classes/functions/commands to add or update: `ExpectedSpeakerLine`, `MultiSpeakerFixture`, `get_fixture_by_name` in `tests/fixtures/multi_speaker.py`; regression tests in `tests/transform/test_multi_speaker_regression.py`.
- Dependency changes (new/removed packages) and rationale: None.
- Logging/telemetry additions and locations: None (test-only).
- Rollout plan (feature flags, staged deploys, fallback path): None; merged tests run in CI.

## Definition of Done

- [x] Acceptance criteria documented and mapped to tests or demos (user story + regression suite)
- [ ] Behavior matches acceptance criteria in all documented environments (pending validation run)
- [x] Tests updated/added (unit/integration as applicable) (`tests/transform/test_multi_speaker_regression.py`)
- [x] Edge cases and error handling covered by tests (fixture validation + `xfail` gaps)
- [x] Docs updated (README, docs/features/active/... links) (this spec and user story)
- [ ] Telemetry/logging added or updated (if applicable) (not applicable for test-only changes)
- [ ] Toolchain pass completed (format → lint → type-check → test)
