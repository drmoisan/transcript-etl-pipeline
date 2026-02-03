# 2025-12-04-notes-regressions — Spec

- **Issue:** #26
- **Parent (optional):** none
- **Owner:** drmoisan
- **Last Updated:** 2026-02-02T13-09
- **Status:** Draft
- **Version:** 0.1

## Overview

Known notes conversion edge cases lack regression tests, allowing past bugs to reappear and leaving transform/notes.py under-covered.

- Target users/personas and primary use cases: Maintainers and contributors who need regression protection and explicit expectations for notes conversion behavior.
- Success metrics or expected impact: Regression tests document known failure modes, and coverage for notes-related paths measurably improves.


## Behavior

Capture known notes conversion issues and add regression tests that document the prior failure and validate current behavior, improving coverage in notes-related paths.

- Main user flow (happy path): Pytest runs new tests in `tests/transform/` that convert representative notes inputs and assert on parsed sections, bullets, and ordering.
- Alternate/edge flows: Tests include tricky inputs from prior reports (e.g., mixed bullets, blank lines, label-like prefixes) and assert normalization and section segmentation behavior.
- Error handling and recovery behavior: Tests verify deterministic outputs without filesystem or network dependencies.

## Regression Cases

1. Markdown cleanup removes formatting markers while preserving literal symbols.
   - Input:
     ```
     \$100 **bold** __strong__
     ```
   - Expected output snippet:
     ```
     $100 bold strong
     ```
2. Bullet indentation levels are mapped consistently.
   - Input:
     ```
     - Item
       - Nested
     ```
   - Expected output snippet:
     ```
     (level=1, text="Item")
     (level=2, text="Nested")
     ```
3. Heading level detection ignores leading whitespace.
   - Input:
     ```
       ## Heading
     ```
   - Expected output snippet:
     ```
     level=2, text="Heading"
     ```
4. Notes label is inserted as H2 after an H1 title when a label is provided.
   - Input:
     ```
     # Title

     - Bullet
     ```
   - Expected output snippet:
     ```
     ## Meeting Notes
     ```
5. Mixed heading/bullet ordering is preserved.
   - Input:
     ```
     # Title
     - One
     ## Section
     - Two
     ```
   - Expected output snippet:
     ```
     Title -> Bullet("One") -> Section -> Bullet("Two")
     ```


## Inputs / Outputs

- Inputs (CLI flags, files, env vars): In-memory notes strings supplied by unit tests; no CLI flags or env vars.
- Outputs (artifacts, logs, telemetry): Pytest assertions and coverage reports from the existing test toolchain.
- Config keys and defaults: None.
- Versioning or backward-compatibility constraints: No public API changes; tests only.

## API / CLI Surface

List commands, flags, request/response shapes, and examples.

- Example invocations with expected outputs (concise): `poetry run pytest tests/transform/` runs the new regression tests.
- Contracts and validation rules: Tests assert expected `DocumentSection` and `Paragraph` outputs from notes conversion functions.

## Data & State

Data flow, storage, or state changes introduced by this feature.

- Data transformations and invariants: Notes conversion maintains expected section ordering, bullet detection, and label handling for known edge cases.
- Caching or persistence details: None.
- Migration or backfill requirements (if any): None.

## Constraints & Risks

- Tests must be deterministic and avoid external dependencies.
- Keep scope limited to notes conversion edge cases and related code paths.

- Limits (latency/throughput/memory) and acceptable trade-offs: Keep fixtures small and focused to keep tests fast.
- Security/privacy considerations: No external services or sensitive data.
- Operational/rollout risks and mitigations: Risk of ambiguous expectations; mitigate by encoding expected outputs in assertions.


## Implementation Strategy

- Implementation scope (what changes, not sequencing): Add regression tests in `tests/transform/` for notes conversion edge cases.
- New classes/functions/commands to add or update: New Pytest test functions targeting `transform/notes.py` conversion behavior.
- Dependency changes (new/removed packages) and rationale: None.
- Logging/telemetry additions and locations: None.
- Rollout plan (feature flags, staged deploys, fallback path): Not applicable; tests only.

## Definition of Done

- [ ] Acceptance criteria documented and mapped to tests or demos
- [ ] Behavior matches acceptance criteria in all documented environments
- [ ] Tests updated/added (unit/integration as applicable)
- [ ] Edge cases and error handling covered by tests
- [ ] Docs updated (README, docs/features/active/... links)
- [ ] Telemetry/logging added or updated (if applicable)
- [ ] Toolchain pass completed (format → lint → type-check → test)

## Seeded Test Conditions (from potential)
- [ ] Unit/regression tests for transform/notes.py edge cases from prior reports.
- [ ] Coverage checks for notes-related paths.
- [ ] Representative inputs reflecting known failure modes.
