"""
Tests for pytest expectation resolution and failure parsing helpers.
"""

from scripts.dev_tools.atomic_executor.plan_parser import PlanModel, PlanTask
from scripts.dev_tools.atomic_executor.pytest_expectations import (
    is_jest_ref,
    is_pytest_ref,
    parse_jest_failure_output,
    parse_pytest_failure_output,
    resolve_checked_test_expectations,
)


class TestIsPytestRef:
    """Tests for is_pytest_ref helper function."""

    def test_identifies_typescript_test_files(self) -> None:
        """
        TypeScript test file references should be excluded from pytest.

        Purpose:
            Ensure Jest/TypeScript tests don't get passed to pytest.
        """
        assert is_pytest_ref("tests/unit/task-execution-spec.test.ts") is False
        assert is_pytest_ref("tests/unit/task-execution-spec.spec.ts") is False
        assert (
            is_pytest_ref("tests/unit/task-execution-spec.test.ts::getTaskExecutionSpec") is False
        )

    def test_identifies_python_test_files(self) -> None:
        """
        Python test file references should be accepted by pytest.

        Purpose:
            Ensure pytest nodeids pass through filtering.
        """
        assert is_pytest_ref("tests/bugs/2026/test_issue_98.py::test_foo") is True
        assert is_pytest_ref("tests/unit/test_module.py") is True
        assert is_pytest_ref("tests/integration/test_flow.py::TestClass") is True

    def test_handles_ambiguous_refs(self) -> None:
        """
        References without clear file extensions default to pytest.

        Purpose:
            Preserve backward compatibility for prose-style refs.
        """
        assert is_pytest_ref("test_something") is True
        assert is_pytest_ref("tests/module::test_name") is True


class TestIsJestRef:
    """Tests for is_jest_ref helper function."""

    def test_identifies_typescript_test_refs(self) -> None:
        """TypeScript/Jest refs should be detected for npm test gating."""
        assert is_jest_ref("tests/unit/task-execution-spec.test.ts") is True
        assert is_jest_ref("tests/unit/task-execution-spec.spec.ts") is True
        assert is_jest_ref("tests/unit/task-execution-spec.test.tsx") is True
        assert is_jest_ref("tests/unit/task-execution-spec.test.ts::getTaskExecutionSpec") is True

    def test_rejects_python_refs(self) -> None:
        """Python refs should not be classified as Jest."""
        assert is_jest_ref("tests/bugs/2026/test_issue_98.py::test_expected_fail") is (False)


class TestResolveCheckedTestExpectations:
    """Tests for resolve_checked_test_expectations."""

    def test_expect_fail_without_test_ref_is_silently_skipped(self) -> None:
        """
        Expect-fail tasks without test_ref should be skipped, not flagged as missing.

        Purpose:
            Support "run all tests" verification tasks (like P1-T5) that don't
            reference a specific test but are still tagged [expect-fail].

        Context:
            Bug: Tasks like "Run the new tests to confirm the regression coverage
            fails" are tagged [expect-fail] but don't match any test_ref extraction
            pattern. Previously these were added to missing_test_refs, causing
            QC runner to raise RuntimeError. The fix skips them silently.
        """
        plan = PlanModel(
            tasks=[
                PlanTask(
                    "P1-T1",
                    1,
                    1,
                    "Add Jest test in `tests/unit/foo.test.ts` for `bar`",
                    True,
                    0,
                    expect_fail=True,
                    test_ref="tests/unit/foo.test.ts::bar",
                ),
                PlanTask(
                    "P1-T5",
                    1,
                    5,
                    "Run the new tests to confirm the regression coverage fails",
                    True,
                    1,
                    expect_fail=True,
                    # No test_ref - this is a "run all" verification task
                    test_ref=None,
                ),
            ],
            phases=[1],
        )

        expectations = resolve_checked_test_expectations(plan)

        # P1-T5 should NOT be in missing_test_refs since it has no specific ref to check
        assert expectations.missing_test_refs == []
        # P1-T1's ref should still be captured
        assert expectations.expected_fail_jest_refs == {"tests/unit/foo.test.ts::bar"}

    def test_expect_pass_overrides_expect_fail(self) -> None:
        """
        Expected-pass overrides expected-fail for the same test ref.

        Purpose:
            Ensure the override rule keeps a ref in expected-pass only.
        """
        test_ref = "tests/bugs/2026/test_issue_98.py::test_expected_fail"
        plan = PlanModel(
            tasks=[
                PlanTask(
                    "P1-T1",
                    1,
                    1,
                    "pytest tests/bugs/2026/test_issue_98.py::test_expected_fail",
                    True,
                    0,
                    expect_fail=True,
                    test_ref=test_ref,
                ),
                PlanTask(
                    "P1-T2",
                    1,
                    2,
                    "pytest tests/bugs/2026/test_issue_98.py::test_expected_fail",
                    True,
                    1,
                    expect_pass=True,
                    test_ref=test_ref,
                ),
            ],
            phases=[1],
        )

        expectations = resolve_checked_test_expectations(plan)

        assert expectations.expected_fail_refs == set()
        assert expectations.expected_pass_refs == {test_ref}
        assert expectations.missing_test_refs == []

    def test_only_checked_tasks_contribute_expectations(self) -> None:
        """
        Unchecked tasks should not contribute to expectation sets.

        Purpose:
            Guard against uncompleted work affecting QC behavior.
        """
        plan = PlanModel(
            tasks=[
                PlanTask(
                    "P1-T1",
                    1,
                    1,
                    "pytest tests/bugs/2026/test_issue_98.py::test_expected_fail",
                    False,
                    0,
                    expect_fail=True,
                    test_ref="tests/bugs/2026/test_issue_98.py::test_expected_fail",
                ),
                PlanTask(
                    "P1-T2",
                    1,
                    2,
                    "pytest tests/bugs/2026/test_issue_98.py::test_expected_pass",
                    True,
                    1,
                    expect_pass=True,
                    test_ref="tests/bugs/2026/test_issue_98.py::test_expected_pass",
                ),
            ],
            phases=[1],
        )

        expectations = resolve_checked_test_expectations(plan)

        assert expectations.expected_fail_refs == set()
        assert expectations.expected_pass_refs == {
            "tests/bugs/2026/test_issue_98.py::test_expected_pass"
        }
        assert expectations.missing_test_refs == []

    def test_filters_out_jest_typescript_test_refs(self) -> None:
        """
        Jest/TypeScript test references should be routed to Jest expectations.

        Purpose:
            Prevent pytest from attempting to run TypeScript test files.
        """
        plan = PlanModel(
            tasks=[
                PlanTask(
                    "P1-T1",
                    1,
                    1,
                    "jest tests/unit/task-execution-spec.test.ts",
                    True,
                    0,
                    expect_fail=True,
                    test_ref="tests/unit/task-execution-spec.test.ts::getTaskExecutionSpec",
                ),
                PlanTask(
                    "P1-T2",
                    1,
                    2,
                    "pytest tests/bugs/2026/test_issue_98.py::test_expected_fail",
                    True,
                    1,
                    expect_fail=True,
                    test_ref="tests/bugs/2026/test_issue_98.py::test_expected_fail",
                ),
            ],
            phases=[1],
        )

        expectations = resolve_checked_test_expectations(plan)

        # Python test ref should be included for pytest
        assert expectations.expected_fail_refs == {
            "tests/bugs/2026/test_issue_98.py::test_expected_fail"
        }
        assert expectations.expected_pass_refs == set()
        # Jest test ref should be routed to jest expectations
        assert expectations.expected_fail_jest_refs == {
            "tests/unit/task-execution-spec.test.ts::getTaskExecutionSpec"
        }
        assert expectations.expected_pass_jest_refs == set()
        assert expectations.missing_test_refs == []


class TestParsePytestFailureOutput:
    """Tests for parse_pytest_failure_output."""

    def test_parses_failing_nodeids(self) -> None:
        """
        Pytest failing nodeids should be extracted from summary output.

        Purpose:
            Ensure parameterized nodeids are captured verbatim.
        """
        output = "\n".join(
            [
                ("========================= short test summary info " "========================="),
                (
                    "FAILED tests/bugs/2026/test_issue_98.py::"
                    "test_preflight_respects_expectations - AssertionError"
                ),
                (
                    "FAILED tests/bugs/2026/test_issue_98.py::"
                    "test_preflight_respects_expectations[param0] - AssertionError"
                ),
                ("FAILED tests/other/test_other.py::test_unrelated " "- AssertionError"),
                ("====================== 3 failed, 10 passed in 0.21s " "======================"),
            ]
        )
        summary = parse_pytest_failure_output(output)

        assert summary.failed_nodeids == {
            "tests/bugs/2026/test_issue_98.py::test_preflight_respects_expectations",
            "tests/bugs/2026/test_issue_98.py::test_preflight_respects_expectations[param0]",
            "tests/other/test_other.py::test_unrelated",
        }
        assert summary.has_collection_error is False

    def test_detects_collection_errors(self) -> None:
        """
        Collection/import errors should be treated as gate failures.

        Purpose:
            Ensure collection errors are flagged separately from test failures.
        """
        output = "\n".join(
            [
                (
                    "============================= test session starts "
                    "============================="
                ),
                "ERROR collecting tests/bugs/2026/test_issue_98.py",
                (
                    "ImportError while importing test module "
                    "'/workspaces/.../tests/bugs/2026/test_issue_98.py'."
                ),
                "E   ModuleNotFoundError: No module named 'some_missing_dep'",
                (
                    "=========================== short test summary info "
                    "============================"
                ),
                "ERROR tests/bugs/2026/test_issue_98.py",
                (
                    "!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection "
                    "!!!!!!!!!!!!!!!!!!!!"
                ),
            ]
        )
        summary = parse_pytest_failure_output(output)

        assert summary.failed_nodeids == set()
        assert summary.has_collection_error is True


class TestParseJestFailureOutput:
    """Tests for parse_jest_failure_output."""

    def test_parses_failing_files_and_tests(self) -> None:
        """Jest failures should capture file paths and test names."""
        output = "\n".join(
            [
                "FAIL tests/unit/task-execution-spec.test.ts",
                "  \u25cf getTaskExecutionSpec returns QC black",
                "",
                "Test Suites: 1 failed, 1 total",
            ]
        )

        summary = parse_jest_failure_output(output)

        assert summary.failed_files == {"tests/unit/task-execution-spec.test.ts"}
        assert summary.failed_tests == {"getTaskExecutionSpec returns QC black"}
        assert summary.has_runtime_error is False

    def test_detects_runtime_errors(self) -> None:
        """Runtime errors should be flagged to fail QC immediately."""
        output = "\n".join(
            [
                "FAIL tests/unit/task-execution-spec.test.ts",
                "Test suite failed to run",
                "SyntaxError: Unexpected token",
            ]
        )

        summary = parse_jest_failure_output(output)

        assert summary.failed_files == {"tests/unit/task-execution-spec.test.ts"}
        assert summary.has_runtime_error is True
