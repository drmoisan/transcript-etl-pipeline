"""
Expectation resolution and test failure parsing helpers for atomic executor.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.dev_tools.atomic_executor.plan_parser import PlanModel

FAILED_NODEID_RE = re.compile(r"^FAILED\s+(?P<nodeid>\S+)")
COLLECTION_ERROR_RE = re.compile(r"^ERROR\s+collecting\s+", re.IGNORECASE)
JEST_FAIL_FILE_RE = re.compile(r"^FAIL\s+(?P<path>.+)$")
JEST_FAIL_TEST_RE = re.compile(r"^\u25cf\s+(?P<name>.+)$")
JEST_RUNTIME_ERROR_RE = re.compile(r"test suite failed to run", re.IGNORECASE)
JEST_UNEXPECTED_TOKEN_RE = re.compile(r"jest encountered an unexpected token", re.IGNORECASE)
# Matches "Tests: 2 skipped, 4 passed, 6 total" or "Tests: 4 passed, 6 total"
JEST_SUMMARY_LINE_RE = re.compile(
    r"^Tests:\s+"
    r"(?:(?P<skipped>\d+)\s+skipped,\s+)?"
    r"(?:(?P<passed>\d+)\s+passed,\s+)?"
    r"(?P<total>\d+)\s+total$"
)


def is_pytest_ref(test_ref: str) -> bool:
    """
    Check if a test reference is for pytest (not Jest/TypeScript).

    Purpose:
        Filter out non-Python test references before passing to pytest.

    Args:
        test_ref (str): Test reference extracted from a plan task.

    Returns:
        bool: True if the ref appears to be a pytest nodeid, False otherwise.

    Side Effects:
        None.
    """
    # Pytest nodeids typically reference .py files
    # Jest/TypeScript tests reference .test.ts, .spec.ts, etc.
    if (
        ".test.ts" in test_ref
        or ".spec.ts" in test_ref
        or ".test.tsx" in test_ref
        or ".spec.tsx" in test_ref
    ):
        return False
    if test_ref.endswith(".ts") or test_ref.endswith(".tsx"):
        return False
    # Assume Python test if it has .py or follows pytest nodeid pattern
    if ".py" in test_ref or "/" in test_ref or test_ref.startswith("tests"):
        return True
    return True  # Default to True for backward compatibility


def is_jest_ref(test_ref: str) -> bool:
    """
    Check if a test reference is for Jest/TypeScript (not pytest).

    Purpose:
        Route expectation-tagged tasks to the correct test runner.

    Args:
        test_ref (str): Test reference extracted from a plan task.

    Returns:
        bool: True if the ref appears to be a Jest/TypeScript test reference.
    """
    if (
        ".test.ts" in test_ref
        or ".spec.ts" in test_ref
        or ".test.tsx" in test_ref
        or ".spec.tsx" in test_ref
    ):
        return True
    return test_ref.endswith(".ts") or test_ref.endswith(".tsx")


@dataclass(frozen=True)
class ResolvedTestExpectations:
    """
    Resolved expectations for pytest outcomes derived from a plan.

    Purpose:
        Provide normalized expectation sets for QC gating decisions.

    Attributes:
        expected_fail_refs (set[str]): Pytest refs allowed to fail.
        expected_pass_refs (set[str]): Pytest refs required to pass.
        expected_fail_jest_refs (set[str]): Jest refs allowed to fail.
        expected_pass_jest_refs (set[str]): Jest refs required to pass.
        missing_test_refs (list[str]): Always empty; retained for API compatibility.
            Previously held task IDs for expectation-tagged tasks without test_ref,
            but these are now silently skipped (they are "run all" verification tasks).
    """

    expected_fail_refs: set[str]
    expected_pass_refs: set[str]
    expected_fail_jest_refs: set[str]
    expected_pass_jest_refs: set[str]
    missing_test_refs: list[str]


@dataclass(frozen=True)
class PytestFailureSummary:
    """
    Parsed summary of pytest failures from captured output.

    Purpose:
        Normalize pytest output into data used for QC gate decisions.

    Attributes:
        failed_nodeids (set[str]): Nodeids reported as failed.
        has_collection_error (bool): True when collection/import errors appear.
    """

    failed_nodeids: set[str]
    has_collection_error: bool


@dataclass(frozen=True)
class JestFailureSummary:
    """
    Parsed summary of Jest failures from captured output.

    Purpose:
        Normalize Jest output into data used for QC gate decisions.

    Attributes:
        failed_files (set[str]): Test file paths reported as failed.
        failed_tests (set[str]): Test names reported as failed.
        has_runtime_error (bool): True when Jest reports a runtime error.
        skipped_count (int): Number of tests that were skipped.
        output (str): Original Jest output for fallback matching.
    """

    failed_files: set[str]
    failed_tests: set[str]
    has_runtime_error: bool
    skipped_count: int
    output: str


def resolve_checked_test_expectations(plan: PlanModel) -> ResolvedTestExpectations:
    """
    Resolve expectation tags from checked plan tasks.

    Purpose:
        Collect expected-fail and expected-pass refs derived from checked tasks,
        routing refs to pytest or Jest expectation sets as appropriate.

    Args:
        plan (PlanModel): Parsed plan model to inspect.

    Returns:
        ResolvedTestExpectations: Normalized expectation sets and missing refs.

    """
    expected_fail_refs: set[str] = set()
    expected_pass_refs: set[str] = set()
    expected_fail_jest_refs: set[str] = set()
    expected_pass_jest_refs: set[str] = set()

    # Walk checked tasks with expectation tags and gather their test references.
    # Tasks without a test_ref (e.g., "run all tests" verification tasks) are
    # silently skipped - they have no specific test to check against.
    for task in plan.tasks:
        if not task.checked:
            continue
        if not (task.expect_fail or task.expect_pass):
            continue
        if not task.test_ref:
            continue
        if is_pytest_ref(task.test_ref):
            if task.expect_pass:
                expected_pass_refs.add(task.test_ref)
            elif task.expect_fail:
                expected_fail_refs.add(task.test_ref)
            continue

        if is_jest_ref(task.test_ref):
            if task.expect_pass:
                expected_pass_jest_refs.add(task.test_ref)
            elif task.expect_fail:
                expected_fail_jest_refs.add(task.test_ref)
            continue

    # Enforce override semantics so expected-pass wins for the same ref.
    expected_fail_refs.difference_update(expected_pass_refs)
    expected_fail_jest_refs.difference_update(expected_pass_jest_refs)

    return ResolvedTestExpectations(
        expected_fail_refs=expected_fail_refs,
        expected_pass_refs=expected_pass_refs,
        expected_fail_jest_refs=expected_fail_jest_refs,
        expected_pass_jest_refs=expected_pass_jest_refs,
        missing_test_refs=[],
    )


def parse_pytest_failure_output(output: str) -> PytestFailureSummary:
    """
    Parse pytest output into failing nodeids and collection status.

    Purpose:
        Identify failing tests and collection/import errors from pytest output.

    Args:
        output (str): Combined stdout/stderr captured from pytest.

    Returns:
        PytestFailureSummary: Parsed nodeids and collection error flag.

    """
    failed_nodeids: set[str] = set()
    has_collection_error = False

    lines = output.splitlines()

    # Scan pytest output line-by-line to extract failures and error conditions.
    for line in lines:
        stripped = line.strip()
        failed_match = FAILED_NODEID_RE.match(stripped)
        if failed_match:
            failed_nodeids.add(failed_match.group("nodeid"))
            continue

        # Flag collection/import errors so QC gates can fail fast.
        if COLLECTION_ERROR_RE.match(stripped):
            has_collection_error = True
            continue
        if stripped.lower().startswith("importerror while importing test module"):
            has_collection_error = True
            continue
        if stripped.lower().startswith("error during collection"):
            has_collection_error = True
            continue
        if stripped.lower().startswith("error "):
            has_collection_error = True

    return PytestFailureSummary(
        failed_nodeids=failed_nodeids,
        has_collection_error=has_collection_error,
    )


def parse_jest_failure_output(output: str) -> JestFailureSummary:
    """
    Parse Jest output into failing tests and runtime error status.

    Purpose:
        Identify failing test files and test names from Jest output.

    Args:
        output (str): Combined stdout/stderr captured from Jest.

    Returns:
        JestFailureSummary: Parsed failures and runtime error flag.
    """
    failed_files: set[str] = set()
    failed_tests: set[str] = set()
    has_runtime_error = False
    skipped_count = 0

    for line in output.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        file_match = JEST_FAIL_FILE_RE.match(stripped)
        if file_match:
            path = file_match.group("path").strip()
            if " (" in path:
                path = path.rsplit(" (", 1)[0].strip()
            failed_files.add(path)
            continue

        test_match = JEST_FAIL_TEST_RE.match(stripped)
        if test_match:
            failed_tests.add(test_match.group("name").strip())
            continue

        if JEST_RUNTIME_ERROR_RE.search(stripped):
            has_runtime_error = True
            continue
        if JEST_UNEXPECTED_TOKEN_RE.search(stripped):
            has_runtime_error = True
            continue

        # Extract skipped count from Jest summary line
        # (e.g., "Tests: 2 skipped, 4 passed, 6 total")
        summary_match = JEST_SUMMARY_LINE_RE.match(stripped)
        if summary_match:
            skipped_str = summary_match.group("skipped")
            if skipped_str:
                skipped_count = int(skipped_str)
            continue

    return JestFailureSummary(
        failed_files=failed_files,
        failed_tests=failed_tests,
        has_runtime_error=has_runtime_error,
        skipped_count=skipped_count,
        output=output,
    )


def matches_jest_expected_ref(summary: JestFailureSummary, expected_ref: str) -> bool:
    """
    Check whether a Jest failure summary matches an expected reference.

    Purpose:
        Allow expected Jest failures while flagging unexpected ones.

    Args:
        summary (JestFailureSummary): Parsed Jest failures.
        expected_ref (str): Expected test reference from the plan.

    Returns:
        bool: True when the expected ref matches the failures.
    """
    file_path, test_pattern = split_jest_expected_ref(expected_ref)

    if file_path and summary.failed_files and file_path not in summary.failed_files:
        return False

    if test_pattern:
        for name in summary.failed_tests:
            if test_pattern in name:
                return True
        return test_pattern in summary.output

    if file_path:
        return True

    return expected_ref in summary.output


def split_jest_expected_ref(expected_ref: str) -> tuple[str | None, str | None]:
    """
    Split a Jest expected ref into file path and test name pattern.

    Args:
        expected_ref (str): Expected ref from plan parsing.

    Returns:
        tuple[str | None, str | None]: (file_path, test_pattern)
    """
    if "::" in expected_ref:
        file_path, test_pattern = expected_ref.split("::", 1)
        return file_path.strip(), test_pattern.strip()

    if "--testNamePattern" in expected_ref:
        parts = expected_ref.split()
        file_path = parts[0] if parts else None
        pattern_match = re.search(
            r"--testNamePattern(?:=|\s+)(?P<pattern>\"[^\"]+\"|'[^']+'|\S+)",
            expected_ref,
        )
        if pattern_match:
            pattern = pattern_match.group("pattern").strip()
            if (pattern.startswith('"') and pattern.endswith('"')) or (
                pattern.startswith("'") and pattern.endswith("'")
            ):
                pattern = pattern[1:-1]
            return file_path, pattern
        return file_path, None

    if expected_ref.endswith((".test.ts", ".spec.ts", ".test.tsx", ".spec.tsx")):
        return expected_ref, None

    return None, None
