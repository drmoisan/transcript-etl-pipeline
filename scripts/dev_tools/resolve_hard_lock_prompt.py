"""Resolve the execute-hard-lock prompt with the plan file path.

Purpose:
    This helper resolves the active plan file path from the target file,
    substitutes the ${plan-path} variable into the execute-hard-lock.prompt.md
    template, prints the result, and attempts to copy it to the clipboard for
    pasting into Copilot Chat.

Supported variables:
    - ${plan-path}: Workspace-relative path to the target plan file (forward
      slashes).

Usage:
    python resolve_hard_lock_prompt.py --target <path_to_plan_file>
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def copy_to_clipboard(text: str) -> bool:
    """Attempt to copy text to the clipboard using common tools.

    Purpose:
        Provides cross-platform clipboard support using either pyperclip
        (if installed) or native system clipboard commands.

    Args:
        text: The text to copy to the clipboard.

    Returns:
        True on success, False if no supported clipboard mechanism is found.

    Side Effects:
        Writes to the system clipboard.
        Prints error to stderr if pyperclip fails.
    """
    try:
        import pyperclip  # type: ignore[import-untyped]
    except ImportError:
        pyperclip = None  # type: ignore[assignment]

    pyperclip_error: Exception | None = None
    if pyperclip is not None:
        try:
            pyperclip.copy(text)
            return True
        except Exception as error:  # noqa: BLE001 - CLI top-level error handling
            pyperclip_error = error

    # Fallback chain: try common clipboard commands across platforms
    commands: tuple[list[str], ...] = (
        ["pbcopy"],  # macOS
        ["wl-copy"],  # Wayland
        ["xclip", "-selection", "clipboard"],  # X11
        ["xsel", "--clipboard", "--input"],  # X11 alternative
        ["clip"],  # Windows
        ["clip.exe"],  # WSL
    )

    for command in commands:
        executable = shutil.which(command[0])
        if executable is None:
            continue
        try:
            # S603: validated above via shutil.which
            subprocess.run(  # noqa: S603 - static analysis can't verify runtime validation
                [executable, *command[1:]],
                input=text,
                text=True,
                check=True,
            )
            return True
        except subprocess.CalledProcessError:
            continue

    if pyperclip_error is not None:
        print(f"pyperclip copy failed: {pyperclip_error}", file=sys.stderr)

    return False


def _try_relative_to_workspace(path: Path, workspace_root: Path) -> Path:
    """Return path relative to workspace_root when possible.

    Args:
        path: The path to make relative.
        workspace_root: The workspace root directory.

    Returns:
        The relative path if possible, otherwise the original path.
    """
    try:
        return path.resolve().relative_to(workspace_root.resolve())
    except ValueError:
        return path


def resolve_prompt(template_content: str, target_path: Path, workspace_root: Path) -> str:
    """Resolve ${plan-path} in the template with the target file path.

    Purpose:
        Substitutes the ${plan-path} variable with the workspace-relative path
        to the target file, using forward slashes for consistency.

    Args:
        template_content: The raw template content containing ${plan-path}.
        target_path: The path to the plan file.
        workspace_root: The workspace root directory.

    Returns:
        The resolved template with ${plan-path} replaced.

    Side Effects:
        None. Pure function.
    """
    # Resolve target path relative to workspace
    relative_target = _try_relative_to_workspace(target_path, workspace_root)

    # Convert to forward slashes for cross-platform consistency
    plan_path_value = relative_target.as_posix()

    # Substitute the variable
    resolved = template_content.replace("${plan-path}", plan_path_value)

    return resolved


def main() -> int:
    """Main CLI entry point.

    Returns:
        Exit code: 0 on success, 1 on error.

    Side Effects:
        Reads files, writes to clipboard, prints to stdout/stderr.
    """
    parser = argparse.ArgumentParser(
        description="Resolve execute-hard-lock prompt with plan file path"
    )
    parser.add_argument(
        "--target",
        type=Path,
        required=True,
        help="Path to the plan file",
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=None,
        help="Workspace root directory (default: current working directory)",
    )

    args = parser.parse_args()

    # Determine workspace root
    workspace_root = args.workspace if args.workspace else Path.cwd()

    # Locate the template file
    template_path = workspace_root / ".github" / "codex" / "execute-hard-lock.prompt.md"

    if not template_path.exists():
        print(f"Error: Template not found at {template_path}", file=sys.stderr)
        return 1

    if not args.target.exists():
        print(f"Error: Target file not found at {args.target}", file=sys.stderr)
        return 1

    # Read template
    try:
        template_content = template_path.read_text(encoding="utf-8")
    except OSError as error:
        print(f"Error reading template: {error}", file=sys.stderr)
        return 1

    # Resolve the prompt
    resolved_prompt = resolve_prompt(template_content, args.target, workspace_root)

    # Print the resolved prompt
    print(resolved_prompt)

    # Attempt to copy to clipboard
    if copy_to_clipboard(resolved_prompt):
        print("\n✓ Copied to clipboard", file=sys.stderr)
    else:
        print(
            "\n✗ Could not copy to clipboard (no supported mechanism found)",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
