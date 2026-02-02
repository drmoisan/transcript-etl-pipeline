Agent E Objective: Add end-to-end CLI tests for speakerless + notes workflows (DOCX/MD outputs) to protect key flows.

## Policies: Always Follow These

CRITICAL: When implementing any code, tests, or tasks, you must adhere to these repo policies without exception. These are not guidelines-they are requirements.

Read each policy document thoroughly before starting work. Implement them exactly as written. Do not interpret, modify, or skip any requirements.

* Coding Standards, Workflow, PR/commit procedures:  
  [code-change.instructions.md](../../../code-change.instructions.md)
  
  This document defines the complete development workflow including:  
  - Pre-implementation requirements (clarify objectives, document plans)  
  - Python coding standards (formatting, linting, typing, testing)  
  - Design principles (simplicity, reusability, extensibility, separation of concerns)  
  - Post-implementation requirements (quality checks, documentation updates)

* Developer Tooling: Poetry, Black, Ruff, Pyright, Pytest, pytest-cov, coverage, pre-commit, VSCode tasks:  
  [developer-tooling.md](../../../developer-tooling.md)
  
  This document covers all tooling setup and usage.

* Unit Test Policy (independence, determinism, clarity, AAA, etc.):  
  [unit-test-policy.md](../../../unit-test-policy.md)
  
  This document defines mandatory testing standards. Every test must comply.

Do not guess. Do not omit steps. Do not introduce inconsistencies. Follow the policies exactly.

## Workplan
- ✅ Identify representative speakerless and notes transcripts for CLI E2E runs.
- ✅ Add pytest integration tests (e.g., under `tests/integration/`) that invoke the CLI to produce DOCX/MD.
- ✅ Assert on outputs via text extraction/markers (golden files optional if brittle).
- ✅ Ensure tests are deterministic and runnable via existing tasks.
- Link scenarios, PR(s), and results in issue #25; note any runtime/env considerations.

## Implementation Summary

Created two new test modules with 23 E2E tests total:

### test_cli_e2e_speakerless.py (11 tests)
- TestCLISpeakerless3SpeakersDOCX: 3 tests using SPACEX_DISCUSSION, GENERIC_MEETING_3SPEAKER, TEAM_STANDUP_3SPEAKER fixtures
- TestCLISpeakerless4SpeakersDOCX: 1 test using PANEL_DISCUSSION_4SPEAKER fixture  
- TestCLISpeakerlessMarkdown: 2 tests for MD output
- TestCLISpeakerlessRTF: 2 tests for RTF output
- TestCLISpeakerlessAutoDetect: 1 test for auto-detection without --num-speakers flag
- TestCLIErrorHandling: 2 tests for missing files and invalid arguments

### test_cli_e2e_notes.py (12 tests)
- TestCLINotesOnly: 3 tests for notes-only documents (DOCX/MD/RTF)
- TestCLINotesAndTranscript: 2 tests for combined notes + transcript workflows
- TestCLIUpdateModeNotes: 2 tests for adding/replacing notes in existing documents
- TestCLIUpdateModeTranscript: 2 tests for adding/replacing transcript in existing documents
- TestCLIUpdateModeDOCX: 1 test for DOCX update (exercises reader.py)
- TestCLINotesErrorHandling: 2 tests for error conditions

## Coverage Results

**Before:**
- cli.py: 11% (244 lines uncovered)
- document/reader.py: 8% (190 lines uncovered)
- extract/from_file.py: 14%
- formatters: 11-28% 
- transform/notes.py: 14%

**After:**
- **cli.py: 67%** (+56 percentage points) - Exercises argument parsing, validation, main flow
- **document/reader.py: 47%** (+39 percentage points) - Via update mode tests reading DOCX/MD files
- **extract/from_file.py: 68%** (+54 percentage points) - Via --source file flag
- **formatters: docx 95%, md 82%, rtf 93%** (+60-80 percentage points) - All three formats tested
- **transform/notes.py: 73%** (+59 percentage points) - Via notes workflows

**Overall test coverage: 45%** (up from 16%)

All tests pass (23/23) with proper AAA structure, docstrings, and type annotations.



## Acceptance Criteria
- New E2E tests cover at least one speakerless and one notes CLI flow.
- Tests pass reliably in CI and locally; assertions verify key outputs.
- Issue #25 updated with PR/test links and a brief scenario description.
