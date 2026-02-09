"""
Integration regression coverage for Unicode subprocess output handling.
"""

from __future__ import annotations

import os
from pathlib import Path

from scripts.dev_tools.atomic_executor.qc_runner import QCRunner


def _repo_root() -> Path:
    """
    Resolve the repository root by walking up to the pyproject.toml file.

    Purpose:
        Provide a stable workspace path for integration tests without relying
        on the current working directory.

    Returns:
        Path: Repository root directory containing pyproject.toml.

    Raises:
        FileNotFoundError: If the repository root cannot be located.
    """
    current = Path(__file__).resolve()

    # Walk upward until the repo root (pyproject.toml) is located.
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent

    raise FileNotFoundError("Unable to locate repo root (pyproject.toml not found).")


def test_qc_runner_subprocess_handles_invalid_bytes() -> None:
    """
    Ensure QCRunner subprocess output decodes invalid bytes without crashing.

    Purpose:
        Reproduce the UnicodeDecodeError seen on Windows when subprocess output
        contains bytes that are invalid in cp1252. The QCRunner should use a
        tolerant decoding strategy so the executor doesn't crash mid-run.

    Steps:
        - Run a Python subprocess that writes an invalid byte (0x8f) directly
          to stdout.
        - Verify the subprocess completes and the output is captured.

    Raises:
        AssertionError: If the subprocess fails or output is missing.
    """
    runner = QCRunner(_repo_root())
    command = [
        "python",
        "-c",
        'import sys; sys.stdout.buffer.write(b"Test output: \\x8f invalid")',
    ]

    result = runner.run_command(command, capture_output=True)

    assert "Test output:" in (result.stdout or "")
    assert result.returncode == 0


def test_resolve_executable_handles_cmd_tools_on_windows() -> None:
    """
    Ensure executable resolution works for Windows PATHEXT tools.

    Purpose:
        Reproduce the WinError 2 failure caused by passing an unresolved
        command (like npm) directly to CreateProcess. The resolver should
        return a concrete executable path (e.g., npm.cmd).

    Raises:
        AssertionError: If resolution fails or returns an empty path.
    """
    runner = QCRunner(_repo_root())
    resolved = runner.resolve_executable(["npm", "--version"])

    resolved_exe = Path(resolved[0]).name.lower()

    # Validate resolved executable naming for Windows vs non-Windows paths.
    if os.name == "nt":
        assert resolved_exe.endswith(".cmd") or resolved_exe.endswith(".exe")
    else:
        assert resolved_exe == "npm"
