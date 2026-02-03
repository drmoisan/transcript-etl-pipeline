"""
QC toolchain execution for atomic task verification.

Supports both scoped QC (changed files only, fast task gate) and full QC
(entire codebase, phase gate).
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from typing import TYPE_CHECKING

from scripts.dev_tools.atomic_executor.pytest_expectations import (
    JestFailureSummary,
    ResolvedTestExpectations,
    parse_jest_failure_output,
    parse_pytest_failure_output,
    split_jest_expected_ref,
)
from scripts.dev_tools.atomic_executor.qc_toolchain import (
    TOOLCHAIN_COMMANDS,
    QCToolchain,
)

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path


class QCRunner:
    """
    Execute scoped and full QC toolchains.

    Purpose:
        Runs Python (Black/Ruff/Pyright/Pytest) and TypeScript
        (format/lint/typecheck/Jest) toolchains for scoped or full QC.

    Usage:
        runner = QCRunner(workspace)
        runner.run_scoped()   # After each task
        runner.run_full()     # After each phase

    Flow:
        Scoped QC:
          1. Detect changed Python files via git status
          2. Run Black/Ruff/Pyright on those files only
          3. Run Pytest only on changed test files (fast path)

        Full QC:
          - Python: Black/Ruff/Pyright/Pytest on entire codebase
          - TypeScript: format/lint/typecheck/test:unit on entire codebase

    Invariants:
        - workspace must be a git repository
        - Poetry environment must be active and have required tools

    Side Effects:
        - Calls subprocess commands (git, poetry, black, ruff, pyright, pytest)
        - Raises CalledProcessError if any QC step fails
    """

    # Full toolchain commands for phase gates (Python)
    FULL_FMT = ["poetry", "run", "black", "--check", "."]
    FULL_LINT = ["poetry", "run", "ruff", "check"]
    FULL_TYPE = ["poetry", "run", "pyright"]
    FULL_TEST = [
        "poetry",
        "run",
        "pytest",
        "--color=no",
        "--cov=src/lexile_corpus_tuner",
        "--cov-report=xml",
        "--cov-report=term-missing",
    ]

    # Full toolchain commands for phase gates (TypeScript)
    FULL_TS_FMT = TOOLCHAIN_COMMANDS[QCToolchain.TYPESCRIPT]["format"]
    FULL_TS_LINT = TOOLCHAIN_COMMANDS[QCToolchain.TYPESCRIPT]["lint"]
    FULL_TS_TYPE = TOOLCHAIN_COMMANDS[QCToolchain.TYPESCRIPT]["typecheck"]
    FULL_TS_TEST = TOOLCHAIN_COMMANDS[QCToolchain.TYPESCRIPT]["test-unit"]

    AUTO_QC_STEP_ORDER = ["black", "ruff", "pyright", "pytest"]
    EXECUTOR_LOCK_BYPASS_ENV = "ATOMIC_EXECUTOR_SKIP_LOCK"

    def __init__(self, workspace: Path) -> None:
        """
        Initialize the QC runner with workspace path.

        Args:
            workspace (Path): Repository root directory.
        """
        self.workspace = workspace

    def run_scoped(self, *, expectations: ResolvedTestExpectations | None = None) -> None:
        """
        Run toolchain on changed files only (task gate).

        Purpose:
            Fast QC verification after a single task completes.

        Args:
            expectations (ResolvedTestExpectations | None): Optional expected
                pytest failures derived from the active plan.

        Raises:
            CalledProcessError: If any QC command fails.

        Side Effects:
            Runs git status, black, ruff, pyright, pytest on changed files.
        """
        files = self.changed_files()
        py_files = self._filter_python_files(files)
        test_files = self._filter_test_files(files)
        ts_files = self._filter_ts_files(files)
        ts_test_files = self._filter_ts_test_files(files)

        # No-op if no relevant changes
        if not (py_files or test_files or ts_files or ts_test_files):
            return

        # Run formatter, linter, type checker on changed Python files
        if py_files:
            self._run(["poetry", "run", "black", "--check", *py_files])
            self._run(["poetry", "run", "ruff", "check", *py_files])
            self._run(["poetry", "run", "pyright", *py_files])

        # Run tests only for changed test files (fast path)
        if test_files:
            self._run_pytest_scoped_with_expectations(
                test_files=test_files, expectations=expectations
            )

        # Run Jest unit tests for changed TypeScript test files
        if ts_test_files:
            self._run_jest_scoped_with_expectations(
                test_files=ts_test_files, expectations=expectations
            )

    def run_full(
        self,
        *,
        expectations: ResolvedTestExpectations | None = None,
        toolchain: QCToolchain = QCToolchain.PYTHON,
    ) -> None:
        """
        Run full toolchain on entire codebase (phase gate).

        Purpose:
            Comprehensive QC verification after a phase completes.

        Args:
            expectations (ResolvedTestExpectations | None): Optional expected
                test failures derived from the active plan.
            toolchain (QCToolchain): Toolchain to run (Python or TypeScript).

        Raises:
            CalledProcessError: If any QC command fails.

        Side Effects:
            Runs black, ruff, pyright, pytest with full coverage.
        """
        if toolchain is QCToolchain.PYTHON:
            self._run(self.FULL_FMT)
            self._run(self.FULL_LINT)
            self._run(self.FULL_TYPE)
            self._run_pytest_with_expectations(expectations)
            return

        if toolchain is QCToolchain.TYPESCRIPT:
            self._run(self.FULL_TS_FMT)
            self._run(self.FULL_TS_LINT)
            self._run(self.FULL_TS_TYPE)
            self._run_jest_with_expectations(cmd=self.FULL_TS_TEST, expectations=expectations)
            return

        raise RuntimeError(f"Unsupported QC toolchain: {toolchain}")

    def _run_pytest_with_expectations(
        self,
        expectations: ResolvedTestExpectations | None,
    ) -> None:
        """
        Run pytest and apply expectation filtering to failures.

        Purpose:
            Allow expected-fail tests to fail while still failing on unexpected
            errors or expected-pass overrides.

        Args:
            expectations (ResolvedTestExpectations | None): Optional expected
                pytest failures derived from the active plan.

        Raises:
            CalledProcessError: If pytest fails unexpectedly.
        """
        env = self._merge_env(self._lock_bypass_env())
        if expectations is None:
            self._run(self.FULL_TEST, env=env)
            return

        if expectations.missing_test_refs:
            missing_refs = ", ".join(expectations.missing_test_refs)
            raise RuntimeError(
                "Missing test reference for expectation-tagged tasks: " f"{missing_refs}"
            )

        result = subprocess.run(  # noqa: S603 - argv constructed from trusted constants
            self.FULL_TEST,
            cwd=self.workspace,
            check=False,
            capture_output=True,
            text=True,
            errors="replace",
            env=env,
        )
        combined = (result.stdout or "") + (result.stderr or "")
        if result.returncode == 0:
            return

        summary = parse_pytest_failure_output(combined)
        if summary.has_collection_error:
            raise subprocess.CalledProcessError(result.returncode, self.FULL_TEST, output=combined)

        unexpected_failures: list[str] = []
        expected_pass_hits: list[str] = []

        # Compare failing nodeids against expected refs with prefix matching.
        for nodeid in summary.failed_nodeids:
            if _matches_expected_ref(nodeid, expectations.expected_pass_refs):
                expected_pass_hits.append(nodeid)
                unexpected_failures.append(nodeid)
            elif _matches_expected_ref(nodeid, expectations.expected_fail_refs):
                continue
            else:
                unexpected_failures.append(nodeid)

        if unexpected_failures or expected_pass_hits:
            raise subprocess.CalledProcessError(result.returncode, self.FULL_TEST, output=combined)

    def _run_pytest_scoped_with_expectations(
        self,
        *,
        test_files: list[str],
        expectations: ResolvedTestExpectations | None,
    ) -> None:
        """
        Run pytest on specific test files with expectation filtering.

        Purpose:
            Allow expected-fail tests to fail during scoped QC checks
            (mid-execution project state).

        Args:
            test_files (list[str]): Test file paths to run.
            expectations (ResolvedTestExpectations | None): Optional expected
                pytest failures derived from the active plan.

        Raises:
            CalledProcessError: If pytest fails unexpectedly.
        """
        env = self._merge_env(self._lock_bypass_env())
        cmd = ["poetry", "run", "pytest", *test_files]

        if expectations is None:
            self._run(cmd, env=env)
            return

        if expectations.missing_test_refs:
            missing_refs = ", ".join(expectations.missing_test_refs)
            raise RuntimeError(
                "Missing test reference for expectation-tagged tasks: " f"{missing_refs}"
            )

        result = subprocess.run(  # noqa: S603 - argv constructed from trusted constants
            cmd,
            cwd=self.workspace,
            check=False,
            capture_output=True,
            text=True,
            errors="replace",
            env=env,
        )
        combined = (result.stdout or "") + (result.stderr or "")
        if result.returncode == 0:
            return

        summary = parse_pytest_failure_output(combined)
        if summary.has_collection_error:
            raise subprocess.CalledProcessError(result.returncode, cmd, output=combined)

        unexpected_failures: list[str] = []
        expected_pass_hits: list[str] = []

        # Compare failing nodeids against expected refs with prefix matching.
        for nodeid in summary.failed_nodeids:
            if _matches_expected_ref(nodeid, expectations.expected_pass_refs):
                expected_pass_hits.append(nodeid)
                unexpected_failures.append(nodeid)
            elif _matches_expected_ref(nodeid, expectations.expected_fail_refs):
                continue
            else:
                unexpected_failures.append(nodeid)

        if unexpected_failures or expected_pass_hits:
            raise subprocess.CalledProcessError(result.returncode, cmd, output=combined)

    def _run_jest_with_expectations(
        self,
        *,
        cmd: list[str],
        expectations: ResolvedTestExpectations | None,
    ) -> None:
        """
        Run Jest with expectation filtering for known failures.

        Purpose:
            Allow expected-fail Jest tests to fail while still failing on
            unexpected errors or expected-pass overrides.

        Args:
            cmd (list[str]): Jest command to execute.
            expectations (ResolvedTestExpectations | None): Optional expected
                Jest failures derived from the active plan.

        Raises:
            CalledProcessError: If Jest fails unexpectedly.
        """
        if expectations is None:
            self._run(cmd)
            return

        if expectations.missing_test_refs:
            missing_refs = ", ".join(expectations.missing_test_refs)
            raise RuntimeError(
                "Missing test reference for expectation-tagged tasks: " f"{missing_refs}"
            )

        try:
            self._run(cmd, capture_output=True)
            return
        except subprocess.CalledProcessError as exc:
            combined = (exc.stdout or "") + (exc.stderr or "")
            summary = parse_jest_failure_output(combined)
            if summary.has_runtime_error:
                raise subprocess.CalledProcessError(exc.returncode, cmd, output=combined) from exc
            if not summary.failed_tests and not summary.failed_files:
                raise subprocess.CalledProcessError(exc.returncode, cmd, output=combined) from exc

            unexpected_failures: list[str] = []
            expected_pass_hits: list[str] = []

            if summary.failed_tests:
                for test_name in summary.failed_tests:
                    if _jest_test_matches_expected(test_name, expectations.expected_pass_jest_refs):
                        expected_pass_hits.append(test_name)
                        unexpected_failures.append(test_name)
                    elif _jest_test_matches_expected(
                        test_name, expectations.expected_fail_jest_refs
                    ):
                        continue
                    else:
                        unexpected_failures.append(test_name)
            else:
                for file_path in summary.failed_files:
                    if _jest_file_matches_expected(file_path, expectations.expected_pass_jest_refs):
                        expected_pass_hits.append(file_path)
                        unexpected_failures.append(file_path)
                    elif _jest_file_matches_expected(
                        file_path, expectations.expected_fail_jest_refs
                    ):
                        continue
                    else:
                        unexpected_failures.append(file_path)

            if unexpected_failures or expected_pass_hits:
                raise subprocess.CalledProcessError(exc.returncode, cmd, output=combined) from exc

    def _run_jest_scoped_with_expectations(
        self,
        *,
        test_files: list[str],
        expectations: ResolvedTestExpectations | None,
    ) -> None:
        """
        Run Jest on specific test files with expectation filtering.

        Purpose:
            Allow expected-fail Jest tests to fail during scoped QC checks.

        Args:
            test_files (list[str]): Jest test file paths to run.
            expectations (ResolvedTestExpectations | None): Optional expected
                Jest failures derived from the active plan.

        Raises:
            CalledProcessError: If Jest fails unexpectedly.
        """
        cmd = ["npm", "run", "test:unit", "--", *test_files]
        self._run_jest_with_expectations(cmd=cmd, expectations=expectations)

    def check_jest_skipped_tests(
        self, *, test_files: list[str] | None = None
    ) -> JestFailureSummary:
        """
        Run Jest and return a summary including skipped test count.

        Purpose:
            Check whether Jest tests were skipped (e.g., describe.skip()),
            which is relevant for TDD Red tasks where tests should fail but
            may be skipped if the implementation doesn't exist.

        Args:
            test_files (list[str] | None): Optional list of test files to run.
                If None, runs the full Jest test suite.

        Returns:
            JestFailureSummary: Summary including skipped_count and output.

        Side Effects:
            Runs Jest via subprocess. Does NOT raise on test failures.
        """
        cmd = ["npm", "run", "test:unit", "--", *test_files] if test_files else self.FULL_TS_TEST

        # Resolve executable for Windows compatibility
        exe = shutil.which(cmd[0])
        if exe is None:
            raise FileNotFoundError(f"Required executable not found on PATH: {cmd[0]}")
        resolved_cmd = [exe, *cmd[1:]]

        # Run Jest, capturing output regardless of exit code
        result = subprocess.run(  # noqa: S603 - static analysis can't verify runtime validation
            resolved_cmd,
            cwd=self.workspace,
            check=False,
            capture_output=True,
            text=True,
            errors="replace",
        )
        combined = (result.stdout or "") + (result.stderr or "")
        return parse_jest_failure_output(combined)

    def run_full_loop_with_artifacts(
        self,
        *,
        artifact_paths: dict[str, Path],
        max_loops: int | None = 10,
        toolchain: QCToolchain = QCToolchain.PYTHON,
    ) -> QCLoopResult:
        """
        Run the full QC toolchain loop and capture outputs to artifact files.

        Purpose:
            Execute Black/Ruff/Pyright/Pytest in the required order, restarting
            the loop when formatting changes occur, and record each step's output
            to the specified artifact file.

        Args:
            artifact_paths (dict[str, Path]): Map from step name to output file.
            max_loops (int | None): Maximum loop iterations before aborting.
            toolchain (QCToolchain): Toolchain to run (Python or TypeScript).

        Returns:
            QCLoopResult: Success flag and failure details if applicable.

        Raises:
            RuntimeError: If loop iteration exceeds max_loops.

        Side Effects:
            Runs subprocess commands and writes output files under artifacts/.
        """
        loop_count = 0

        if toolchain is QCToolchain.PYTHON:
            format_step = "black"
            lint_step = "ruff"
            type_step = "pyright"
            test_step = "pytest"
            format_cmd = ["poetry", "run", "black", "."]
            lint_cmd = ["poetry", "run", "ruff", "check"]
            type_cmd = ["poetry", "run", "pyright"]
            test_cmd = [
                "poetry",
                "run",
                "pytest",
                "--cov=src/lexile_corpus_tuner",
                "--cov=scripts/dev_tools",
                "--cov-report=term-missing",
            ]
            test_env = self._merge_env(self._lock_bypass_env())
        elif toolchain is QCToolchain.TYPESCRIPT:
            format_step = "format"
            lint_step = "lint"
            type_step = "typecheck"
            test_step = "test-unit"
            format_cmd = self.FULL_TS_FMT
            lint_cmd = self.FULL_TS_LINT
            type_cmd = self.FULL_TS_TYPE
            test_cmd = self.FULL_TS_TEST
            test_env = None
        else:
            raise RuntimeError(f"Unsupported QC toolchain: {toolchain}")

        # Repeat the toolchain until it completes without formatting changes.
        while True:
            loop_count += 1
            if max_loops is not None and loop_count > max_loops:
                raise RuntimeError("QC loop exceeded maximum iterations " f"({max_loops}).")

            # Capture the current diff signature so we can detect Black changes
            # even when the working tree already has edits.
            before_black = self._diff_signature(exclude_paths=artifact_paths.values())

            # Run Black in write mode and restart the loop if files changed.
            format_result = self._run_and_record(
                argv=format_cmd,
                output_path=artifact_paths[format_step],
            )
            # Formatting failure must be fixed before continuing to other steps.
            if format_result.returncode != 0:
                return QCLoopResult(
                    success=False,
                    failure=QCLoopFailure(
                        step=format_step,
                        returncode=format_result.returncode,
                        output=format_result.output,
                    ),
                    loop_count=loop_count,
                )

            # Detect formatting changes by comparing diffs before/after Black.
            after_black = self._diff_signature(exclude_paths=artifact_paths.values())
            if after_black != before_black:
                continue

            # Run Ruff, Pyright, and Pytest in order.
            lint_result = self._run_and_record(
                argv=lint_cmd,
                output_path=artifact_paths[lint_step],
            )
            # Fail fast if linting fails.
            if lint_result.returncode != 0:
                return QCLoopResult(
                    success=False,
                    failure=QCLoopFailure(
                        step=lint_step,
                        returncode=lint_result.returncode,
                        output=lint_result.output,
                    ),
                    loop_count=loop_count,
                )

            type_result = self._run_and_record(
                argv=type_cmd,
                output_path=artifact_paths[type_step],
            )
            # Type-checking failures should be fixed before testing.
            if type_result.returncode != 0:
                return QCLoopResult(
                    success=False,
                    failure=QCLoopFailure(
                        step=type_step,
                        returncode=type_result.returncode,
                        output=type_result.output,
                    ),
                    loop_count=loop_count,
                )

            test_result = self._run_and_record(
                argv=test_cmd,
                output_path=artifact_paths[test_step],
                env=test_env,
            )
            # Test failures must be fixed before the loop can complete.
            if test_result.returncode != 0:
                return QCLoopResult(
                    success=False,
                    failure=QCLoopFailure(
                        step=test_step,
                        returncode=test_result.returncode,
                        output=test_result.output,
                    ),
                    loop_count=loop_count,
                )

            return QCLoopResult(success=True, failure=None, loop_count=loop_count)

    def changed_files(self) -> list[str]:
        """
        Detect changed files via git status.

        Purpose:
            Identify files modified/added/deleted for scoped QC.

        Returns:
            list[str]: Relative paths of changed files.

        Side Effects:
            Calls git status --porcelain.
        """
        result = self._run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            errors="replace",
        )
        files: list[str] = []
        # Extract the path column so scoped QC targets only changed files.
        for line in result.stdout.splitlines():
            # Format: XY <path>
            parts = line.strip().split(maxsplit=1)
            if len(parts) == 2:
                files.append(parts[1])
        return files

    def _git_has_changes(self, *, exclude_paths: Iterable[Path] | None = None) -> bool:
        """
        Check if the git working tree has uncommitted changes.

        Purpose:
            Detect formatter modifications so the QC loop can restart from the
            beginning after Black rewrites files.

        Args:
            exclude_paths (Iterable[Path] | None): Paths to ignore when
                determining whether changes occurred. Useful when QC writes
                artifacts that should not trigger a retry loop.

        Returns:
            bool: True if there are uncommitted changes beyond exclusions,
                False otherwise.
        """
        result = self._run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            errors="replace",
        )

        excluded = self._normalize_excluded_paths(exclude_paths)

        # Scan git status output and ignore excluded paths when requested.
        for line in result.stdout.splitlines():
            parts = line.strip().split(maxsplit=1)
            if len(parts) != 2:
                continue
            changed_path = parts[1]
            if changed_path in excluded:
                continue
            return True

        return False

    def _diff_signature(
        self, *, exclude_paths: Iterable[Path] | None = None
    ) -> tuple[tuple[str, str, str], ...]:
        """
        Build a diff signature for the working tree.

        Purpose:
            Capture a stable fingerprint of current diffs so the QC loop can
            determine whether Black introduced changes even when files were
            already modified.

        Args:
            exclude_paths (Iterable[Path] | None): Paths to ignore when building
                the signature.

        Returns:
            tuple[tuple[str, str, str], ...]: Sorted tuples of
                (path, additions, deletions) for each changed file.
        """
        result = self._run(
            ["git", "diff", "--numstat"],
            capture_output=True,
            text=True,
            errors="replace",
        )
        excluded = self._normalize_excluded_paths(exclude_paths)

        signature: list[tuple[str, str, str]] = []
        # Capture line-level change counts per file for a stable diff fingerprint.
        for line in result.stdout.splitlines():
            parts = line.split("\t")
            if len(parts) < 3:
                continue
            additions, deletions, path = parts[0], parts[1], parts[2]
            if " => " in path:
                path = path.split(" => ")[-1].strip()
            if path in excluded:
                continue
            signature.append((path, additions, deletions))

        return tuple(sorted(signature))

    def _normalize_excluded_paths(self, exclude_paths: Iterable[Path] | None) -> set[str]:
        """
        Normalize excluded paths to repo-relative POSIX strings.

        Purpose:
            Ensure consistent comparisons between path objects and git output.

        Args:
            exclude_paths (Iterable[Path] | None): Paths to normalize.

        Returns:
            set[str]: Normalized paths in POSIX form.
        """
        excluded: set[str] = set()
        if exclude_paths is None:
            return excluded

        # Normalize paths to repo-relative strings for comparison.
        for path in exclude_paths:
            try:
                rel_path = path.relative_to(self.workspace)
            except ValueError:
                rel_path = path
            excluded.add(rel_path.as_posix())

        return excluded

    def _lock_bypass_env(self) -> dict[str, str]:
        """
        Provide an env flag that bypasses the executor lock in tests.

        Purpose:
            The executor holds a lock file during execute-all runs. When QC
            runs pytest in-process, tests that call the executor should not
            fail due to the existing lock, so we set a bypass env var for
            the pytest subprocess only.

        Returns:
            dict[str, str]: Environment overrides enabling lock bypass.
        """
        return {self.EXECUTOR_LOCK_BYPASS_ENV: "1"}

    def _merge_env(self, extra_env: dict[str, str] | None) -> dict[str, str] | None:
        """
        Merge extra environment variables into the current process env.

        Purpose:
            Ensure subprocesses inherit the current environment plus any
            explicit overrides.

        Args:
            extra_env (dict[str, str] | None): Environment overrides to apply.

        Returns:
            dict[str, str] | None: Merged environment or None if no overrides.
        """
        if not extra_env:
            return None

        env = dict(os.environ)
        env.update(extra_env)
        return env

    def _filter_python_files(self, paths: Iterable[str]) -> list[str]:
        """Filter to .py files only."""
        return [p for p in paths if p.endswith(".py")]

    def _filter_test_files(self, paths: Iterable[str]) -> list[str]:
        """Filter to python test files only (tests/ directory)."""
        return [
            p for p in paths if (p.startswith("tests/") or "/tests/" in p) and p.endswith(".py")
        ]

    def _filter_ts_files(self, paths: Iterable[str]) -> list[str]:
        """Filter to .ts/.tsx files only."""
        return [p for p in paths if p.endswith(".ts") or p.endswith(".tsx")]

    def _filter_ts_test_files(self, paths: Iterable[str]) -> list[str]:
        """Filter to typescript test files only (tests/ directory)."""
        return [
            p
            for p in paths
            if (p.startswith("tests/") or "/tests/" in p)
            and (p.endswith(".test.ts") or p.endswith(".spec.ts"))
        ]

    def resolve_executable(self, argv: list[str]) -> list[str]:
        """
        Resolve a command argv to a full executable path.

        Purpose:
            Ensure PATH and PATHEXT resolution works on Windows
            (e.g., npm.cmd, poetry.exe) to avoid WinError 2.

        Args:
            argv (list[str]): Command argv where argv[0] is the executable.

        Returns:
            list[str]: Resolved argv with full executable path.

        Raises:
            FileNotFoundError: If the executable is not found on PATH.
            ValueError: If argv is empty.
        """
        if not argv:
            raise ValueError("Command argv must not be empty.")

        exe = shutil.which(argv[0])
        if exe is None:
            raise FileNotFoundError(f"Required executable not found on PATH: {argv[0]}")

        return [exe, *argv[1:]]

    def run_command(
        self,
        argv: list[str],
        *,
        capture_output: bool = False,
        text: bool = True,
        errors: str | None = "replace",
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        """
        Run a subprocess command using the QC runner execution defaults.

        Purpose:
            Provide a public wrapper around the internal subprocess handling
            to support integration tests and external callers.

        Args:
            argv (list[str]): Command and arguments to execute.
            capture_output (bool): Whether to capture stdout/stderr.
            text (bool): Whether to decode output as text.
            errors (str | None): Text decoding error handler
                ('replace', 'ignore', etc.). Defaults to "replace" when
                text output is enabled.
            env (dict[str, str] | None): Environment overrides for the command.

        Returns:
            CompletedProcess: Result of subprocess execution.

        Raises:
            FileNotFoundError: If executable is not found on PATH.
            CalledProcessError: If command exits with non-zero status.
        """
        return self._run(
            argv,
            capture_output=capture_output,
            text=text,
            errors=errors,
            env=env,
        )

    def _run(
        self,
        argv: list[str],
        *,
        capture_output: bool = False,
        text: bool = True,
        errors: str | None = "replace",
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        """
        Execute a subprocess command with consistent settings.

        Purpose:
            Cross-platform subprocess execution with PATH-based executable
            resolution for Windows compatibility (e.g., npm.cmd, poetry.exe).

        Args:
            argv (list[str]): Command and arguments to execute.
            capture_output (bool): Whether to capture stdout/stderr.
            text (bool): Whether to decode output as text.
            errors (str | None): Text decoding error handler
                ('replace', 'ignore', etc.). Defaults to "replace" when
                text output is enabled.
            env (dict[str, str] | None): Environment overrides for the command.

        Returns:
            CompletedProcess: Result of subprocess execution.

        Raises:
            FileNotFoundError: If executable is not found on PATH.
            CalledProcessError: If command exits with non-zero status.
        """
        # Resolve executable via PATH/PATHEXT for cross-platform compatibility.
        resolved_argv = self.resolve_executable(argv)
        return subprocess.run(  # noqa: S603 - static analysis can't verify runtime validation
            resolved_argv,
            cwd=self.workspace,
            check=True,
            capture_output=capture_output,
            text=text,
            errors=errors if text else None,
            env=env,
        )

    def _run_and_record(
        self,
        *,
        argv: list[str],
        output_path: Path,
        env: dict[str, str] | None = None,
    ) -> QCToolResult:
        """
        Execute a command, capture output, and write it to a file.

        Purpose:
            Run a QC step with output capture for artifact logging.

        Args:
            argv (list[str]): Command and arguments to execute.
            output_path (Path): File path for captured output.
            env (dict[str, str] | None): Environment overrides for the command.

        Returns:
            QCToolResult: Captured output and exit status.

        Side Effects:
            Creates parent directories and writes output to disk.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        resolved_argv = self.resolve_executable(argv)
        result = subprocess.run(  # noqa: S603 - argv constructed from trusted constants
            resolved_argv,
            cwd=self.workspace,
            check=False,
            capture_output=True,
            text=True,
            errors="replace",
            env=env,
        )

        output = (result.stdout or "") + (result.stderr or "")
        header = " ".join(argv)
        output_path.write_text(
            f"$ {header}\n(exit {result.returncode})\n\n{output}",
            encoding="utf-8",
        )

        return QCToolResult(
            step=argv[2] if len(argv) > 2 else "command",
            returncode=result.returncode,
            output=output,
        )


@dataclass(frozen=True)
class QCToolResult:
    """
    Captured output and exit status for a QC step.

    Attributes:
        step (str): Step name or command identifier.
        returncode (int): Process exit code.
        output (str): Combined stdout/stderr text.
    """

    step: str
    returncode: int
    output: str


@dataclass(frozen=True)
class QCLoopFailure:
    """
    Failure details for a QC loop.

    Attributes:
        step (str): Step that failed.
        returncode (int): Process exit code.
        output (str): Captured output from the failed step.
    """

    step: str
    returncode: int
    output: str


@dataclass(frozen=True)
class QCLoopResult:
    """
    Result for a QC loop execution.

    Attributes:
        success (bool): True if all steps passed.
        failure (QCLoopFailure | None): Failure details when success is False.
        loop_count (int): Number of iterations executed.
    """

    success: bool
    failure: QCLoopFailure | None
    loop_count: int


def _matches_expected_ref(nodeid: str, expected_refs: set[str]) -> bool:
    """
    Check whether a failing nodeid matches any expected ref prefix.

    Purpose:
        Support prefix matching to handle parameterized pytest nodeids.

    Args:
        nodeid (str): Failing pytest nodeid.
        expected_refs (set[str]): Expected nodeid prefixes to match against.

    Returns:
        bool: True when a prefix match is found.
    """
    # Scan the expected refs to allow prefix matching for parametrized tests.
    return any(nodeid.startswith(expected_ref) for expected_ref in expected_refs)


def _jest_test_matches_expected(test_name: str, expected_refs: set[str]) -> bool:
    """
    Check whether a Jest test name matches any expected ref pattern.

    Purpose:
        Support substring matching for Jest test names.
    """
    for expected_ref in expected_refs:
        _, test_pattern = split_jest_expected_ref(expected_ref)
        if test_pattern and test_pattern in test_name:
            return True
    return False


def _jest_file_matches_expected(file_path: str, expected_refs: set[str]) -> bool:
    """
    Check whether a Jest file path matches any expected ref file path.

    Purpose:
        Support file-level matching when Jest output lacks test names.
    """
    for expected_ref in expected_refs:
        expected_file, _ = split_jest_expected_ref(expected_ref)
        if expected_file and expected_file == file_path:
            return True
    return False
