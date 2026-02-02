"""Tests for scripts.dev_tools.resolve_hard_lock_prompt."""

from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts.dev_tools.resolve_hard_lock_prompt import (
    main,
    resolve_prompt,
)


def test_resolve_prompt_basic() -> None:
    """Test basic resolution of ${plan-path} variable."""
    template = "Execute plan at: ${plan-path}"
    workspace_root = Path.cwd()
    target = workspace_root / "docs" / "features" / "active" / "plan.md"

    result = resolve_prompt(template, target, workspace_root)

    assert "docs/features/active/plan.md" in result
    assert "${plan-path}" not in result


def test_resolve_prompt_forward_slashes() -> None:
    """Test that backslashes are converted to forward slashes."""
    template = "Plan: ${plan-path}"
    workspace_root = Path.cwd()
    target = workspace_root / "subdir" / "nested" / "plan.md"

    result = resolve_prompt(template, target, workspace_root)

    # Should use forward slashes regardless of platform
    assert "subdir/nested/plan.md" in result
    assert "\\" not in result
    assert "${plan-path}" not in result


def test_resolve_prompt_outside_workspace() -> None:
    """Test fallback when target is outside workspace."""
    template = "External plan: ${plan-path}"
    workspace_root = Path("/workspace/A")
    target = Path("/workspace/B/plan.md")

    # Force relative_to to fail by mocking
    with patch("pathlib.Path.relative_to", side_effect=ValueError):
        result = resolve_prompt(template, target, workspace_root)

        # Should contain the full target path with forward slashes
        assert "workspace/B/plan.md" in result or str(target).replace("\\", "/") in result


def test_resolve_prompt_empty_template() -> None:
    """Test resolution with empty template."""
    template = ""
    workspace_root = Path.cwd()
    target = workspace_root / "plan.md"

    result = resolve_prompt(template, target, workspace_root)

    assert result == ""


def test_resolve_prompt_no_variables() -> None:
    """Test template without any variables."""
    template = "This is a static template with no variables."
    workspace_root = Path.cwd()
    target = workspace_root / "plan.md"

    result = resolve_prompt(template, target, workspace_root)

    assert result == template


def test_resolve_prompt_multiple_occurrences() -> None:
    """Test that all occurrences of ${plan-path} are replaced."""
    template = "First: ${plan-path}\n" "Second: ${plan-path}\n" "Third: ${plan-path}"
    workspace_root = Path.cwd()
    target = workspace_root / "docs" / "plan.md"

    result = resolve_prompt(template, target, workspace_root)

    # All occurrences should be replaced
    assert result.count("${plan-path}") == 0
    assert result.count("docs/plan.md") == 3


def test_resolve_prompt_nested_path() -> None:
    """Test resolution with deeply nested path."""
    template = "Path: ${plan-path}"
    workspace_root = Path.cwd()
    target = (
        workspace_root
        / "docs"
        / "features"
        / "active"
        / "2026-01-30-feature-123"
        / "v2"
        / "plan.md"
    )

    result = resolve_prompt(template, target, workspace_root)

    expected = "docs/features/active/2026-01-30-feature-123/v2/plan.md"
    assert expected in result
    assert "${plan-path}" not in result


def test_copy_to_clipboard_with_pyperclip_success() -> None:
    """Test successful clipboard copy with pyperclip."""
    mock_pyperclip = MagicMock()
    mock_pyperclip.copy = MagicMock()

    with patch.dict("sys.modules", {"pyperclip": mock_pyperclip}):
        # Force reimport to use the mock
        # Reload to pick up the patched pyperclip
        import importlib

        from scripts.dev_tools import resolve_hard_lock_prompt

        importlib.reload(resolve_hard_lock_prompt)

        result = resolve_hard_lock_prompt.copy_to_clipboard("test text")

        assert result is True
        mock_pyperclip.copy.assert_called_once_with("test text")


def test_copy_to_clipboard_pyperclip_failure_fallback() -> None:
    """Test fallback to system commands when pyperclip fails."""
    mock_pyperclip = MagicMock()
    mock_pyperclip.copy = MagicMock(side_effect=RuntimeError("pyperclip failed"))

    with (
        patch.dict("sys.modules", {"pyperclip": mock_pyperclip}),
        patch("shutil.which", return_value="/usr/bin/clip"),
        patch("subprocess.run") as mock_run,
    ):
        # Force reimport
        import importlib

        from scripts.dev_tools import resolve_hard_lock_prompt

        importlib.reload(resolve_hard_lock_prompt)

        result = resolve_hard_lock_prompt.copy_to_clipboard("test text")

        assert result is True
        assert mock_run.called


def test_copy_to_clipboard_no_mechanism() -> None:
    """Test failure when no clipboard mechanism is available."""
    # Mock pyperclip as unavailable
    with (
        patch.dict("sys.modules", {"pyperclip": None}),
        patch("shutil.which", return_value=None),
    ):
        import importlib

        from scripts.dev_tools import resolve_hard_lock_prompt

        importlib.reload(resolve_hard_lock_prompt)

        # Capture stderr to avoid test noise
        with patch("sys.stderr", new_callable=StringIO):
            result = resolve_hard_lock_prompt.copy_to_clipboard("test text")

        assert result is False


def test_main_success(tmp_path: Path) -> None:
    """Test successful main execution."""
    # Create workspace structure
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    # Create template file
    template_dir = workspace / ".github" / "codex"
    template_dir.mkdir(parents=True)
    template_file = template_dir / "execute-hard-lock.prompt.md"
    template_file.write_text("Plan: ${plan-path}", encoding="utf-8")

    # Create target file
    target_dir = workspace / "docs"
    target_dir.mkdir()
    target_file = target_dir / "plan.md"
    target_file.write_text("# Plan", encoding="utf-8")

    with (
        patch(
            "sys.argv",
            ["script", "--target", str(target_file), "--workspace", str(workspace)],
        ),
        patch(
            "scripts.dev_tools.resolve_hard_lock_prompt.copy_to_clipboard",
            return_value=True,
        ),
        patch("sys.stdout", new_callable=StringIO) as mock_stdout,
        patch("sys.stderr", new_callable=StringIO) as mock_stderr,
    ):
        exit_code = main()

    assert exit_code == 0
    stdout_output = mock_stdout.getvalue()
    assert "docs/plan.md" in stdout_output
    assert "${plan-path}" not in stdout_output
    assert "✓ Copied to clipboard" in mock_stderr.getvalue()


def test_main_template_not_found(tmp_path: Path) -> None:
    """Test main when template file doesn't exist."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    target_file = workspace / "plan.md"
    target_file.write_text("# Plan", encoding="utf-8")

    with (
        patch(
            "sys.argv",
            ["script", "--target", str(target_file), "--workspace", str(workspace)],
        ),
        patch("sys.stderr", new_callable=StringIO) as mock_stderr,
    ):
        exit_code = main()

    assert exit_code == 1
    assert "Template not found" in mock_stderr.getvalue()


def test_main_target_not_found(tmp_path: Path) -> None:
    """Test main when target file doesn't exist."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    # Create template file
    template_dir = workspace / ".github" / "codex"
    template_dir.mkdir(parents=True)
    template_file = template_dir / "execute-hard-lock.prompt.md"
    template_file.write_text("Plan: ${plan-path}", encoding="utf-8")

    # Don't create target file
    target_file = workspace / "nonexistent.md"

    with (
        patch(
            "sys.argv",
            ["script", "--target", str(target_file), "--workspace", str(workspace)],
        ),
        patch("sys.stderr", new_callable=StringIO) as mock_stderr,
    ):
        exit_code = main()

    assert exit_code == 1
    assert "Target file not found" in mock_stderr.getvalue()


def test_main_clipboard_copy_fails(tmp_path: Path) -> None:
    """Test main when clipboard copy fails."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    # Create template file
    template_dir = workspace / ".github" / "codex"
    template_dir.mkdir(parents=True)
    template_file = template_dir / "execute-hard-lock.prompt.md"
    template_file.write_text("Plan: ${plan-path}", encoding="utf-8")

    # Create target file
    target_file = workspace / "plan.md"
    target_file.write_text("# Plan", encoding="utf-8")

    with (
        patch(
            "sys.argv",
            ["script", "--target", str(target_file), "--workspace", str(workspace)],
        ),
        patch(
            "scripts.dev_tools.resolve_hard_lock_prompt.copy_to_clipboard",
            return_value=False,
        ),
        patch("sys.stdout", new_callable=StringIO),
        patch("sys.stderr", new_callable=StringIO) as mock_stderr,
    ):
        exit_code = main()

    assert exit_code == 0  # Still succeeds, just warns
    assert "✗ Could not copy to clipboard" in mock_stderr.getvalue()


def test_main_default_workspace(tmp_path: Path) -> None:
    """Test main with default workspace (cwd)."""
    # Create template and target in tmp_path
    template_dir = tmp_path / ".github" / "codex"
    template_dir.mkdir(parents=True)
    template_file = template_dir / "execute-hard-lock.prompt.md"
    template_file.write_text("Plan: ${plan-path}", encoding="utf-8")

    target_file = tmp_path / "plan.md"
    target_file.write_text("# Plan", encoding="utf-8")

    with (
        patch("sys.argv", ["script", "--target", str(target_file)]),
        patch("pathlib.Path.cwd", return_value=tmp_path),
        patch(
            "scripts.dev_tools.resolve_hard_lock_prompt.copy_to_clipboard",
            return_value=True,
        ),
        patch("sys.stdout", new_callable=StringIO) as mock_stdout,
        patch("sys.stderr", new_callable=StringIO),
    ):
        exit_code = main()

    assert exit_code == 0
    assert "plan.md" in mock_stdout.getvalue()


def test_main_template_read_error(tmp_path: Path) -> None:
    """Test main when template file cannot be read."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    # Create template file
    template_dir = workspace / ".github" / "codex"
    template_dir.mkdir(parents=True)
    template_file = template_dir / "execute-hard-lock.prompt.md"
    template_file.write_text("Plan: ${plan-path}", encoding="utf-8")

    # Create target file
    target_file = workspace / "plan.md"
    target_file.write_text("# Plan", encoding="utf-8")

    with (
        patch(
            "sys.argv",
            ["script", "--target", str(target_file), "--workspace", str(workspace)],
        ),
        patch("pathlib.Path.read_text", side_effect=OSError("Read error")),
        patch("sys.stderr", new_callable=StringIO) as mock_stderr,
    ):
        exit_code = main()

    assert exit_code == 1
    assert "Error reading template" in mock_stderr.getvalue()
