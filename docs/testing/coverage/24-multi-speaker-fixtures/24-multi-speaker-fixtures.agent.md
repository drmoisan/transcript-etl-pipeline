Agent D Objective: Build reusable 3+ speaker fixtures (e.g., SpaceX) and regression tests to prevent grouping regressions.

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
- [x] Create/reuse 3+ speaker fixtures (e.g., SpaceX discussion) suitable for regression tests.
- [x] Add regression tests (likely under `tests/integration/` or `tests/transform/`) that fail-before/pass-after for known grouping issues.
- [x] Ensure fixtures are reusable by other tests; document locations/usage here.
- [ ] Run coverage/tests to confirm stability; link PR(s) and results in issue #24.

## Acceptance Criteria
- [x] Fixtures added and referenced by regression tests in `tests/...`.
- [x] Regression tests capture previous failures and now pass.
- [x] Documentation of fixture location and usage is present here and in issue #24.
- [ ] Issue #24 updated with PR/test links and evidence of improved robustness.

---

## Implementation Complete

### Fixture Locations

**Multi-Speaker Fixtures Module:** `tests/fixtures/multi_speaker.py`

This module provides standardized, reusable fixtures for 3+ speaker transcript testing. It includes:

1. **Data Classes:**
   - `ExpectedSpeakerLine`: Represents expected speaker/content pairs
   - `MultiSpeakerFixture`: Complete fixture with input text, expected output, and characteristics

2. **Available Fixtures:**
   | Fixture Name | Speakers | Description |
   |-------------|----------|-------------|
   | `SPACEX_DISCUSSION` | 3 | Technical conversation about SpaceX launch |
   | `GENERIC_MEETING_3SPEAKER` | 3 | Business meeting with introductions and identity constraints |
   | `TEAM_STANDUP_3SPEAKER` | 3 | Daily standup with meeting lead pattern |
   | `PANEL_DISCUSSION_4SPEAKER` | 4 | AI ethics panel with moderator and panelists |

3. **Fixture Collections:**
   - `ALL_3SPEAKER_FIXTURES`: Tuple of all 3-speaker fixtures
   - `ALL_4SPEAKER_FIXTURES`: Tuple of all 4-speaker fixtures
   - `ALL_MULTI_SPEAKER_FIXTURES`: Combined tuple of all fixtures

### Usage Example

```python
from tests.fixtures.multi_speaker import (
    SPACEX_DISCUSSION,
    GENERIC_MEETING_3SPEAKER,
    ALL_MULTI_SPEAKER_FIXTURES,
    get_fixture_by_name,
)

# Use directly
result = assign_speaker_labels(SPACEX_DISCUSSION.input_text, num_speakers=3)

# Use in parametrized tests
@pytest.mark.parametrize("fixture", ALL_MULTI_SPEAKER_FIXTURES)
def test_assigns_correct_speakers(fixture: MultiSpeakerFixture) -> None:
    result = assign_speaker_labels(fixture.input_text, num_speakers=fixture.num_speakers)
    # Verify result...

# Look up by name
fixture = get_fixture_by_name("spacex_discussion")
```

### Regression Tests

**Test Module:** `tests/transform/test_multi_speaker_regression.py`

Contains 45 tests organized into categories:

1. **Fixture Validation (14 tests):** Verify fixture structure and content
2. **Speaker Detection (7 tests):** Test change detection for 3+ speakers
3. **Speaker Assignment (8 tests):** Test correct number of speakers assigned
4. **Content Preservation (4 tests):** Verify content is preserved during labeling
5. **Identity-Aware Assignment (3 tests):** Test identity constraint enforcement
6. **Scenario-Specific Regression (9 tests):** SpaceX, Standup, Panel regressions

### Known Gaps (Captured as xfail Tests)

Four tests are marked as `xfail` to capture known algorithmic limitations:

1. **Identity constraint ordering:** First speaker identification may not map to Speaker A
2. **Addresses-other enforcement:** May not work when identity is established mid-conversation
3. **Perfect rotation pattern:** Natural conversations have ambiguous turn-taking
4. **Address constraint detection:** Algorithm may miss "Sarah, you're next" patterns

These tests serve as regression markers - when the algorithm is improved, they will start passing.

### Test Results

```
============================================ 41 passed, 4 xfailed =============================================
```

All tests pass, with 4 xfail tests capturing known gaps for future improvement.
