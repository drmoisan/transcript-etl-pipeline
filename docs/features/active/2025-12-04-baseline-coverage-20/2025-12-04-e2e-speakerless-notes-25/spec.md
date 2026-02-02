# 2025-12-04-e2e-speakerless-notes — Spec

- **Issue:** #25
- **Parent (optional):** none
- **Owner:** drmoisan
- **Last Updated:** 2026-02-02T12-45
- **Status:** Draft
- **Version:** 0.1

## Overview

There is no end-to-end coverage for CLI speakerless + notes workflows, leaving output validation and integration behavior untested. This feature adds deterministic CLI integration tests that exercise speakerless detection and notes flows across DOCX/MD/RTF outputs, focusing on text-marker assertions instead of brittle binary snapshots.


## Behavior

Add pytest integration tests that run CLI-driven speakerless and notes pipelines for DOCX/MD/RTF outputs and assert on key output structure/text markers. Tests invoke the CLI entrypoint directly (no subprocess) with explicit arguments to avoid UI prompts, validate core output markers, and cover error paths (missing files, invalid arguments).


## Inputs / Outputs

- Inputs (CLI flags, files, env vars)
	- CLI flags exercised in tests: `--source file`, `--file <path>`, `--format docx|md|rtf`, `--num-speakers <n>` (speakerless), `--notes <path>`, `--mode update`.
	- Test data: speakerless transcripts from `tests/fixtures/multi_speaker.py` (SPACEX_DISCUSSION, GENERIC_MEETING_3SPEAKER, TEAM_STANDUP_3SPEAKER, PANEL_DISCUSSION_4SPEAKER).
- Outputs (artifacts, logs, telemetry)
	- Generated output documents (DOCX/MD/RTF) for each integration case.
	- Pytest logs showing pass/fail and assertion outcomes.
- Config keys and defaults:
	- No new config keys; uses existing CLI defaults.
- Versioning or backward-compatibility constraints:
	- No public API changes; tests only.

## API / CLI Surface

List commands, flags, request/response shapes, and examples.
- Example invocations with expected outputs (concise):
	- `transcript-etl --source file --file <transcript.txt> --format docx --num-speakers 3`
		- Expected: speakerless CLI run produces a DOCX with expected speaker labels/markers.
	- `transcript-etl --source file --file <transcript.txt> --notes <notes.txt> --format md`
		- Expected: notes + transcript output includes notes section markers and transcript content.
	- `transcript-etl --source file --file <transcript.txt> --notes <notes.txt> --mode update --format docx`
		- Expected: update mode replaces/augments notes or transcript content in an existing DOCX.
- Contracts and validation rules:
	- CLI invocations must complete without UI prompts when inputs are speakerless and arguments are explicit.
	- Output validation uses stable text markers (section headers, labels, known phrases) rather than binary diffs.
	- Error cases return non-zero exit behavior or raise CLI errors for missing files/invalid arguments.

## Data & State

Data flow, storage, or state changes introduced by this feature.
- Data transformations and invariants:
	- Speakerless flow assigns speakers via CLI pipeline; notes flow merges notes and transcript sections.
	- Invariants validated by tests: required sections present, speaker labels/markers appear, update mode applies changes.
- Caching or persistence details:
	- No new persistence; outputs are generated per test run.
- Migration or backfill requirements (if any):
	- None.

## Constraints & Risks

- End-to-end tests must remain deterministic and fast.
- Avoid fragile DOCX binary comparisons; prefer text marker assertions.
- Implementation summary notes filesystem use via test-generated documents; this conflicts with the unit-test policy prohibiting temporary files and should be resolved via an explicit exception or a non-filesystem test strategy.


## Implementation Strategy

- Implementation scope (what changes, not sequencing):
	- Add integration tests for CLI speakerless detection and notes workflows.
	- Cover DOCX/MD/RTF outputs, update mode, and CLI error paths.
- New classes/functions/commands to add or update:
	- New test modules:
		- `tests/integration/test_cli_e2e_speakerless.py`
		- `tests/integration/test_cli_e2e_notes.py`
- Dependency changes (new/removed packages) and rationale:
	- None.
- Logging/telemetry additions and locations:
	- None (use existing Pytest output).
- Rollout plan (feature flags, staged deploys, fallback path):
	- No runtime rollout; tests run in CI/local suites.

## Definition of Done

- [x] Acceptance criteria documented and mapped to tests or demos (evidence: 23 E2E tests listed in `implementation-summary.md`)
- [x] Behavior matches acceptance criteria in all documented environments (evidence: reported Pytest run for `tests/integration/` in `implementation-summary.md`)
- [x] Tests updated/added (unit/integration as applicable) (evidence: `tests/integration/test_cli_e2e_speakerless.py`, `tests/integration/test_cli_e2e_notes.py`)
- [x] Edge cases and error handling covered by tests (evidence: missing file and invalid argument tests listed in `implementation-summary.md`)
- [ ] Docs updated (README, docs/features/active/... links) (evidence: update still needed in this feature folder)
- [x] Telemetry/logging added or updated (if applicable) (evidence: N/A — relies on existing Pytest output)
- [x] Toolchain pass completed (format → lint → type-check → test) (evidence: quality checks reported in `implementation-summary.md`)

## Seeded Test Conditions (from potential)
- [ ] CLI-driven speakerless run producing DOCX/MD and validated via markers.
- [ ] Notes pipeline CLI run with expected structure/content markers.
- [ ] Assert key output fields without brittle binary snapshots.
