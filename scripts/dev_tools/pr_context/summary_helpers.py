"""Helper routines for PR context rendering and summarization."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Final

from .feature_docs import extract_issue_references
from .models import (
    AuditDocumentSummary,
    IssueDetails,
    PullRequestDetails,
    format_list,
    section,
    truncate_lines,
)

UTC: Final[timezone] = timezone.utc  # noqa: UP017 - datetime.UTC unavailable before Python 3.11

AUDIT_PREFIXES: Final[tuple[str, ...]] = (
    "epic-audit",
    "feature-delivery-inventory",
    "policy-audit",
    "feature-audit",
)

AUDIT_TIMESTAMP_PATTERN: Final[re.Pattern[str]] = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{2}-\d{2})")


def _matches_audit_filename(filename: str) -> bool:
    """Check whether a filename matches expected audit artifact prefixes.

    Args:
        filename (str): File name to evaluate.

    Returns:
        bool: True if the file name starts with a known audit prefix.
    """

    lower = filename.lower()
    # Audit artifacts are named with known prefixes to enable deterministic discovery.
    return any(lower.startswith(prefix) for prefix in AUDIT_PREFIXES)


def _extract_audit_timestamp(path: Path) -> str | None:
    """Extract the audit timestamp from a path.

    Purpose:
        Parse ISO-8601 timestamps from audit directory or file names to
        group related audit artifacts.

    Args:
        path (Path): Audit artifact path.

    Returns:
        str | None: Timestamp string if found.
    """

    # First, prefer timestamps in audit-<timestamp> folder names.
    for part in path.parts:
        if part.startswith("audit-"):
            match = AUDIT_TIMESTAMP_PATTERN.search(part)
            if match:
                return match.group(1)

    # Fall back to timestamps embedded in the file name.
    match = AUDIT_TIMESTAMP_PATTERN.search(path.name)
    return match.group(1) if match else None


def _audit_scope_for_path(path: Path, root: Path) -> Path | None:
    """Determine the epic or feature scope for an audit artifact.

    Purpose:
        Identify the scope root so we can select the latest audit group per
        epic and per feature.

    Args:
        path (Path): Audit artifact path.
        root (Path): Repository root for normalization.

    Returns:
        Path | None: Scope root within docs/features/active.
    """

    try:
        rel = path.relative_to(root)
    except ValueError:
        return None

    parts = rel.parts
    if len(parts) < 4:
        return None
    if parts[0:3] != ("docs", "features", "active"):
        return None

    epic_root = Path(*parts[:4])
    if len(parts) < 5:
        return epic_root

    next_part = parts[4]
    # If the audit artifact is under a feature subfolder, treat that as feature scope.
    if not next_part.startswith("audit-") and not _matches_audit_filename(next_part):
        return epic_root / next_part
    return epic_root


def _audit_scope_candidates(changed_paths: list[str]) -> list[Path]:
    """Infer audit scope roots from changed paths.

    Args:
        changed_paths (list[str]): Changed file paths from PR context.

    Returns:
        list[Path]: Scope roots derived from changed paths.
    """

    scopes: set[Path] = set()
    # Use changed paths to focus audit discovery on touched epics/features.
    for raw in changed_paths:
        parts = Path(raw).parts
        if len(parts) < 4 or parts[0:3] != ("docs", "features", "active"):
            continue
        scopes.add(Path(*parts[:4]))
        if len(parts) >= 5 and not parts[4].endswith(".md"):
            scopes.add(Path(*parts[:5]))
    return sorted(scopes)


def find_audit_documents(root: Path, changed_paths: list[str]) -> list[Path]:
    """Locate audit artifacts relevant to the current PR context.

    Purpose:
        Prefer audit artifacts already changed in the PR, then fall back to
        scanning active feature folders to find canonical audit evidence.

    Args:
        root (Path): Repository root.
        changed_paths (list[str]): Workspace-relative changed file paths.

    Returns:
        list[Path]: Absolute paths to discovered audit artifacts.
    """

    audit_root = root / "docs" / "features" / "active"
    if not audit_root.exists():
        return []

    scope_candidates = _audit_scope_candidates(changed_paths)
    if not scope_candidates:
        # Default to top-level active folders if the PR has no feature changes.
        scope_candidates = [path for path in audit_root.iterdir() if path.is_dir()]

    audit_candidates: list[Path] = []
    # Collect audit artifacts under the relevant epic/feature scopes.
    for scope in scope_candidates:
        # Normalize scope roots to absolute paths so globbing is anchored to the repo root.
        scope_root = scope if scope.is_absolute() else root / scope
        for path in scope_root.rglob("*.md"):
            if _matches_audit_filename(path.name):
                audit_candidates.append(path)

    grouped: dict[Path, dict[str, list[Path]]] = {}
    # Group audits by scope and timestamp so we can select the latest per scope.
    for path in audit_candidates:
        timestamp = _extract_audit_timestamp(path)
        if not timestamp:
            continue
        scope = _audit_scope_for_path(path, root)
        if scope is None:
            continue
        grouped.setdefault(scope, {}).setdefault(timestamp, []).append(path)

    selected: list[Path] = []
    # Keep the latest audit group per scope while preserving all files in that group.
    for _scope, by_timestamp in grouped.items():
        latest_timestamp = max(by_timestamp)
        selected.extend(by_timestamp[latest_timestamp])

    return sorted({path.resolve() for path in selected})


def _extract_commands(text: str) -> list[str]:
    """Extract verification commands captured in audit documentation.

    Args:
        text (str): Audit document content.

    Returns:
        list[str]: Unique command strings discovered in the document.
    """

    commands: list[str] = []
    # Audit documents capture commands in backticks; filter to toolchain commands.
    for match in re.findall(r"`([^`]+)`", text):
        cleaned = match.strip()
        if not cleaned:
            continue
        if any(
            token in cleaned for token in ("poetry ", "pwsh ", "pytest", "ruff", "pyright", "black")
        ):
            commands.append(cleaned)
    return sorted(set(commands))


def _extract_evidence_paths(text: str) -> list[str]:
    """Extract evidence file paths cited by audit documentation.

    Args:
        text (str): Audit document content.

    Returns:
        list[str]: Unique evidence paths referenced in the document.
    """

    pattern = re.compile(
        r"(?P<path>(?:docs/features/[^\s)]+|[^\s)]+/evidence/[^\s)]+|evidence/[^\s)]+))"
    )
    matches = [match.group("path") for match in pattern.finditer(text)]
    return sorted({path for path in matches if path})


def _extract_delivered_issue_refs(text: str) -> list[str]:
    """Extract delivered issue references from feature delivery inventories.

    Args:
        text (str): Feature delivery inventory content.

    Returns:
        list[str]: Issue references that are marked delivered in summary tables.
    """

    delivered: list[str] = []
    # Feature delivery inventories use markdown tables with issue + delivered ratios.
    for line in text.splitlines():
        if not line.strip().startswith("|") or "#" not in line:
            continue
        issue_match = re.search(r"#\d+", line)
        ratio_match = re.search(r"(\d+)\s*/\s*(\d+)", line)
        if not issue_match or not ratio_match:
            continue
        delivered_count = int(ratio_match.group(1))
        total_count = int(ratio_match.group(2))
        if total_count > 0 and delivered_count == total_count:
            delivered.append(issue_match.group(0))
    return sorted(set(delivered))


def _filter_audit_issue_refs(issue_refs: list[str]) -> list[str]:
    """Filter audit issue references to GitHub issue numbers.

    Purpose:
        Audit documents may include tokens that look like issue IDs but are not
        GitHub issues (e.g., ISO-8601). Restrict to numeric issue references.

    Args:
        issue_refs (list[str]): Raw issue references extracted from audit text.

    Returns:
        list[str]: GitHub issue references in #NNN format.
    """

    filtered: list[str] = []
    # Keep only numeric issue references to avoid non-issue tokens.
    for ref in issue_refs:
        if re.fullmatch(r"#?\d+", ref):
            filtered.append(ref if ref.startswith("#") else f"#{ref}")
    return sorted(set(filtered))


def summarize_audit_documents(paths: list[Path], root: Path) -> list[AuditDocumentSummary]:
    """Build structured summaries for audit artifacts.

    Purpose:
        Convert audit markdown into structured summaries for PR context output.

    Args:
        paths (list[Path]): Absolute audit artifact paths.
        root (Path): Repository root for path normalization.

    Returns:
        list[AuditDocumentSummary]: Summaries with issue references and evidence.
    """

    summaries: list[AuditDocumentSummary] = []
    # Process each audit artifact into a concise summary payload.
    for path in paths:
        text = path.read_text(encoding="utf-8")
        issue_refs = _filter_audit_issue_refs(extract_issue_references(text))
        delivered_refs = (
            _extract_delivered_issue_refs(text)
            if path.name.lower().startswith("feature-delivery-inventory")
            else []
        )
        evidence_paths = _extract_evidence_paths(text)
        commands = _extract_commands(text)
        excerpt = truncate_lines(text, 120)
        summaries.append(
            AuditDocumentSummary(
                path=str(path.relative_to(root)),
                issue_refs=issue_refs,
                delivered_issue_refs=delivered_refs,
                evidence_paths=evidence_paths,
                commands=commands,
                excerpt=excerpt,
            )
        )
    return summaries


def format_audit_summaries(summaries: list[AuditDocumentSummary]) -> str:
    """Format audit summaries for the PR context summary section.

    Args:
        summaries (list[AuditDocumentSummary]): Summaries to format.

    Returns:
        str: Formatted summary block for audit evidence.
    """

    if not summaries:
        return "(none)"

    lines: list[str] = []
    # Emit each audit summary with issue refs, evidence paths, and commands.
    for summary in summaries:
        lines.append(f"- {summary.path}")
        lines.append(
            f"  Issues: {', '.join(summary.issue_refs) if summary.issue_refs else '(none)'}"
        )
        lines.append(
            "  Delivered issues: "
            + (
                ", ".join(summary.delivered_issue_refs)
                if summary.delivered_issue_refs
                else "(none)"
            )
        )
        lines.append(
            "  Evidence paths: "
            + (", ".join(summary.evidence_paths) if summary.evidence_paths else "(none)")
        )
        lines.append(
            "  Verification commands: "
            + ("; ".join(summary.commands) if summary.commands else "(none)")
        )
    return "\n".join(lines)


def audit_appendix(summaries: list[AuditDocumentSummary]) -> str:
    """Build appendix text containing audit artifact excerpts.

    Args:
        summaries (list[AuditDocumentSummary]): Audit summaries to include.

    Returns:
        str: Appendix section with truncated audit artifacts.
    """

    if not summaries:
        return "(none)"

    blocks: list[str] = []
    # Include truncated excerpts so PR authors can cite audit evidence directly.
    for summary in summaries:
        blocks.append(section(f"Audit artifact: {summary.path}"))
        blocks.append(summary.excerpt)
    return "\n\n".join(blocks)


if TYPE_CHECKING:
    from .git import GitClient

__all__ = [
    "append_generation_timestamp",
    "audit_appendix",
    "bucket_text",
    "extract_digest_bullets",
    "find_audit_documents",
    "is_scoping_doc",
    "issue_appendix",
    "issue_digest",
    "last_with_truncation",
    "parse_name_status_map",
    "parse_numstat_detailed",
    "parse_section",
    "format_audit_summaries",
    "pr_appendix",
    "pr_digest",
    "scoping_doc_changes",
    "summarize_audit_documents",
]


def last_with_truncation(items: list[str], limit: int) -> tuple[list[str], bool]:
    if len(items) <= limit:
        return items, False
    return items[-limit:], True


def extract_digest_bullets(body: str, *, headings: list[str], limit: int) -> list[str]:
    bullets: list[str] = []
    for heading in headings:
        section_text = parse_section(body, heading)
        if not section_text:
            continue
        for line in section_text.splitlines():
            if not line.strip():
                continue
            cleaned = line.lstrip("-*").strip()
            bullets.append(f"{heading}: {cleaned}")
            if len(bullets) >= limit:
                return bullets
    return bullets[:limit]


def issue_digest(issue: IssueDetails) -> str:
    bullets = extract_digest_bullets(
        issue.body,
        headings=[
            "Why",
            "Context",
            "Root Cause",
            "Constraints",
            "Acceptance Criteria",
            "Test Strategy",
            "Risks",
            "Verification",
            "Follow-ups",
        ],
        limit=8,
    )
    if not bullets:
        bullets.append(f"State: {issue.state}")
        if issue.labels:
            bullets.append(f"Labels: {', '.join(issue.labels)}")

    selected_comments, truncated = last_with_truncation(issue.comments, 3)
    comment_block = (
        "\n".join(f"- {comment}" for comment in selected_comments)
        if selected_comments
        else "(no comments)"
    )
    if truncated:
        comment_block += "\nTRUNCATED: last 3 comments shown"

    metadata = [
        f"Identifier: {issue.number}",
        f"Title: {issue.title}",
        f"Author: {issue.author}",
        f"Assignees: {', '.join(issue.assignees) if issue.assignees else '(none)'}",
        f"Labels: {', '.join(issue.labels) if issue.labels else '(none)'}",
        f"State: {issue.state}",
        f"Last updated: {issue.updated_at}",
    ]
    return "\n".join(
        [
            "\n".join(metadata),
            "Key bullets:",
            "\n".join(f"- {entry}" for entry in bullets),
            "",
            "Recent comments:",
            comment_block,
        ]
    )


def pr_digest(pr: PullRequestDetails) -> str:
    bullets = extract_digest_bullets(
        pr.body,
        headings=[
            "Why",
            "Context",
            "Root Cause",
            "Constraints",
            "Acceptance Criteria",
            "Test Strategy",
            "Risks",
            "Verification",
            "Follow-ups",
        ],
        limit=8,
    )
    if not bullets:
        if pr.files_changed:
            bullets.append(
                f"Touches files: {', '.join(pr.files_changed[:3])}"
                + (" ..." if len(pr.files_changed) > 3 else "")
            )
        bullets.append(f"State: {pr.state}")

    metadata = [
        f"Identifier: {pr.number}",
        f"Title: {pr.title}",
        f"Author: {pr.author}",
        f"Base/Head: {pr.base_ref} <- {pr.head_ref}",
        f"Last updated: {pr.updated_at}",
    ]
    return "\n".join(
        [
            "\n".join(metadata),
            "Key bullets:",
            "\n".join(f"- {entry}" for entry in bullets),
        ]
    )


def issue_appendix(issue: IssueDetails) -> str:
    body_text = truncate_lines(issue.body, 120)
    comments, truncated = last_with_truncation(issue.comments, 10)
    comment_text = "\n".join(f"- {c}" for c in comments) if comments else "(no comments)"
    if truncated:
        comment_text += "\nTRUNCATED: last 10 comments shown"
    user_story_block = ""
    if issue.user_story_content:
        user_story_block = "\n".join(
            [
                "",
                f"User story ({issue.user_story_path or 'user-story.md'}):",
                truncate_lines(issue.user_story_content, 120),
            ]
        )
    return "\n".join(
        [
            section(f"Issue {issue.number}: {issue.title}"),
            f"State: {issue.state}",
            f"Labels: {', '.join(issue.labels) if issue.labels else '(none)'}",
            f"Assignees: {', '.join(issue.assignees) if issue.assignees else '(none)'}",
            f"Author: {issue.author}",
            f"Created: {issue.created_at}",
            f"Updated: {issue.updated_at}",
            "",
            body_text,
            "",
            "Comments:",
            comment_text,
            user_story_block,
        ]
    )


def pr_appendix(pr: PullRequestDetails) -> str:
    body_text = truncate_lines(pr.body, 120)
    return "\n".join(
        [
            section(f"Pull Request {pr.number}: {pr.title}"),
            f"State: {pr.state}",
            f"Author: {pr.author}",
            f"Base: {pr.base_ref}",
            f"Head: {pr.head_ref}",
            f"Created: {pr.created_at}",
            f"Updated: {pr.updated_at}",
            f"Merged: {pr.merged_at or '(not merged)'}",
            f"Labels: {', '.join(pr.labels) if pr.labels else '(none)'}",
            f"Assignees: {', '.join(pr.assignees) if pr.assignees else '(none)'}",
            "",
            body_text,
            "",
            "Auto-close issues (from this PR):",
            format_list(pr.closing_issues, "(none)"),
            "",
            "Files (first 25):",
            format_list(pr.files_changed[:25], "(none)"),
        ]
    )


def parse_numstat_detailed(
    numstat_text: str,
) -> tuple[int, int, dict[str, tuple[int, int]]]:
    adds_total = 0
    dels_total = 0
    per_file: dict[str, tuple[int, int]] = {}
    for raw_line in numstat_text.splitlines():
        if not raw_line.strip():
            continue
        parts = raw_line.split("\t")
        if len(parts) < 3:
            continue
        add_part, del_part, file_part = parts[0], parts[1], parts[2]
        add_count = int(add_part) if add_part.isdigit() else 0
        del_count = int(del_part) if del_part.isdigit() else 0
        adds_total += add_count
        dels_total += del_count
        per_file[format_diff_path(file_part)] = (add_count, del_count)
    return adds_total, dels_total, per_file


def parse_name_status_map(name_status_text: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for raw_line in name_status_text.splitlines():
        if not raw_line.strip():
            continue
        parts = raw_line.split("\t")
        if len(parts) < 2:
            continue
        status = parts[0].strip()
        path = format_diff_path(parts[-1].strip())
        mapping[path] = status
    return mapping


def is_scoping_doc(path: str) -> bool:
    lowered = path.lower()
    return bool(
        lowered.startswith("docs/features/")
        and (
            lowered.endswith("/spec.md")
            or lowered.endswith("/plan.md")
            or lowered.endswith("/bug-remediation-plan.md")
            or lowered.endswith("/user-story.md")
            or lowered.endswith("/readme.md")
        )
    )


def scoping_doc_changes(
    *,
    git: GitClient,
    merge_base: str | None,
    head_sha: str | None,
    root: Path,
    name_status_text: str,
    numstat_details: dict[str, tuple[int, int]],
) -> list[tuple[str, bool, list[str], str | None]]:
    if not merge_base or not head_sha:
        return []
    changes: list[tuple[str, bool, list[str], str | None]] = []
    name_status_map = parse_name_status_map(name_status_text)
    for path, status in name_status_map.items():
        if not is_scoping_doc(path):
            continue
        additions, deletions = numstat_details.get(path, (0, 0))
        reasons: list[str] = []
        material = False
        if status.startswith("A"):
            material = True
            reasons.append("new scoping doc")
        if additions + deletions >= 15:
            material = True
            reasons.append(">=15 lines changed")

        diff_text = git.diff_range(["--unified=0", merge_base, head_sha, "--", path])
        heading_touched = False
        for line in diff_text.splitlines():
            if not line.startswith("+") or line.startswith("+++"):
                continue
            stripped = line.lstrip("+").strip()
            if any(
                stripped.lower().startswith(prefix.lower())
                for prefix in (
                    "## Context",
                    "## Root Cause",
                    "## Proposed Fix",
                    "## Acceptance Criteria",
                    "## Test Strategy",
                    "## Risks",
                )
            ):
                heading_touched = True
                break
        if heading_touched:
            material = True
            reasons.append("key section touched")

        added_lines = [
            line.lstrip("+").strip()
            for line in diff_text.splitlines()
            if line.startswith("+") and not line.startswith("+++")
        ]
        if added_lines and all(
            (not line or line.startswith("[") or line.startswith("http")) for line in added_lines
        ):
            reasons.append("link/whitespace-only changes")
            if not heading_touched and additions + deletions < 15 and not status.startswith("A"):
                material = False

        excerpt = None
        doc_path = root / path
        if material and doc_path.exists():
            content = doc_path.read_text(encoding="utf-8")
            excerpt_parts: list[str] = []
            for heading in (
                "Acceptance Criteria",
                "Root Cause",
                "Proposed Fix",
                "Test Strategy",
            ):
                section_text = parse_section(content, heading)
                if section_text:
                    excerpt_parts.append(f"{heading}:\n{truncate_lines(section_text, 40)}")
            excerpt = "\n\n".join(excerpt_parts[:3]) if excerpt_parts else None

        changes.append((path, material, reasons, excerpt))
    return changes


def bucket_text(name: str, entries: list[tuple[str, tuple[int, int]]]) -> str:
    if not entries:
        return f"{name}: 0 files"
    sorted_entries = sorted(entries, key=lambda item: item[1][0] + item[1][1], reverse=True)
    lines = [
        f"{name}: {len(entries)} files",
        *(f"- {path} (+{adds}/-{dels})" for path, (adds, dels) in sorted_entries[:10]),
    ]
    return "\n".join(lines)


def parse_section(markdown: str, heading: str) -> str:
    escaped = re.escape(heading)
    pattern = rf"^##\s+{escaped}\s*\r?\n(.*?)(?=^##\s+|\Z)"
    match = re.search(pattern, markdown, flags=re.MULTILINE | re.DOTALL)
    if not match:
        return ""
    return match.group(1).strip()


def format_diff_path(path_text: str | None) -> str:
    from .render import format_diff_path as _fmt

    return _fmt(path_text) if path_text is not None else ""


def append_generation_timestamp() -> str:
    """Generate a timestamp section showing when context was collected.

    Returns:
        Formatted timestamp section with UTC time
    """
    timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S %Z")
    return section("Context generated") + "\n" + timestamp + "\n"
