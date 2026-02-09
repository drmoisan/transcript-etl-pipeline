from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

from .models import FeatureDocExcerpt, section, truncate

if TYPE_CHECKING:
    from collections.abc import Iterable


_VERSION_DIR_PATTERN = re.compile(r"^v(\d+)$", flags=re.IGNORECASE)


def _is_excluded_nested_child(name: str) -> bool:
    return name == "evidence" or name.startswith("audit-")


def _version_number(name: str) -> int | None:
    match = _VERSION_DIR_PATTERN.match(name)
    if not match:
        return None
    return int(match.group(1))


def _select_latest_version_dir(base_dir: Path) -> Path:
    """Select the latest vN directory under a feature folder.

    If the feature folder contains subdirectories named v1, v2, v3, ...,
    resolve documentation paths from the numerically highest version folder.
    Otherwise, return the feature folder itself.
    """

    best_version: int | None = None
    best_dir: Path | None = None

    if not base_dir.exists():
        return base_dir

    for child in sorted(base_dir.iterdir()):
        if not child.is_dir():
            continue

        version = _version_number(child.name)
        if version is None:
            continue

        if best_version is None or version > best_version:
            best_version = version
            best_dir = child

    return best_dir or base_dir


def _feature_key_from_active_parts(parts: tuple[str, ...]) -> str | None:
    """Compute the feature key for docs/features/active paths.

    Supported patterns:
        1) docs/features/active/<feature>/<filename>
        2) docs/features/active/<epic>/<feature>/<filename>
        3) docs/features/active/<epic>/<feature>/vN/<filename>

    The returned key is either <feature> or <epic>/<feature>. Returns None
    for excluded audit/evidence folders.
    """

    if len(parts) < 4:
        raise ValueError("Expected parts to include docs/features/active/<...>")

    # Exclude top-level audit/evidence folders from feature detection.
    if _is_excluded_nested_child(parts[3]):
        return None

    # Ignore top-level files (like README.md) under docs/features/active.
    if len(parts) == 4 and Path(parts[3]).suffix:
        return None

    # Versioned child folders are treated as part of the epic/feature scope.
    if len(parts) >= 6 and _version_number(parts[5]) is not None:
        if _is_excluded_nested_child(parts[4]):
            return None
        return f"{parts[3]}/{parts[4]}"

    # Non-versioned epic children become feature scopes unless excluded.
    if len(parts) >= 5:
        child = parts[4]
        if child.endswith(".md") or _version_number(child) is not None:
            return parts[3]
        if _is_excluded_nested_child(child):
            return None
        return f"{parts[3]}/{child}"

    return parts[3]


def parse_section(markdown: str, heading: str) -> str:
    escaped = re.escape(heading)
    pattern = rf"^##\s+{escaped}\s*\r?\n(.*?)(?=^##\s+|\Z)"
    match = re.search(pattern, markdown, flags=re.MULTILINE | re.DOTALL)
    if not match:
        return ""
    return match.group(1).strip()


def completed_plan_tasks(markdown: str, *, limit: int = 10) -> list[str]:
    tasks: list[str] = []
    for line in markdown.splitlines():
        if re.search(r"\[x\]", line, flags=re.IGNORECASE):
            cleaned = re.sub(r"^[-*]\s*\[[xX]\]\s*", "", line).strip()
            tasks.append(cleaned)
        if len(tasks) >= limit:
            break
    return tasks


def extract_issue_references(text: str) -> list[str]:
    if not text:
        return []
    matches = re.findall(r"(?<!\w)#\d+|\b[A-Z][A-Z0-9]+-\d+\b", text)
    seen: set[str] = set()
    ordered: list[str] = []
    for item in matches:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def _resolve_feature_dir(base_dir: Path, feature: str) -> Path | None:
    direct = base_dir / feature
    if direct.exists():
        return direct

    pattern = re.compile(rf"(?:^|[-_]){re.escape(feature)}(?:[-_]|$)")
    strong_matches: list[Path] = []
    weak_matches: list[Path] = []

    for candidate in sorted(base_dir.iterdir()):
        if not candidate.is_dir():
            continue
        name = candidate.name
        if pattern.search(name):
            strong_matches.append(candidate)
        elif feature in name:
            weak_matches.append(candidate)

    if strong_matches:
        return strong_matches[0]
    if weak_matches:
        return weak_matches[0]
    return None


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _verification_text(plan_text: str) -> str:
    for heading in ("Verification", "Test Plan"):
        section_text = parse_section(plan_text, heading)
        if section_text:
            return section_text
    return ""


def gather_feature_excerpts(root: Path, changed_files: Iterable[str]) -> list[FeatureDocExcerpt]:
    features: set[str] = set()
    for raw in changed_files:
        parts = Path(raw).parts
        if len(parts) < 4:
            continue

        if parts[0:3] == ("docs", "features", "active"):
            feature_key = _feature_key_from_active_parts(parts)
            if feature_key:
                features.add(feature_key)

    excerpts: list[FeatureDocExcerpt] = []
    base_dir = root / "docs" / "features" / "active"
    promoted_dir = root / "docs" / "features" / "potential" / "promoted"
    for feature in sorted(features):
        feature_dir: Path | None = _resolve_feature_dir(base_dir, feature)
        promoted_feature_dir: Path | None = _resolve_feature_dir(promoted_dir, feature)
        if feature_dir is None and promoted_feature_dir is None:
            continue

        active_dir = feature_dir or promoted_feature_dir
        if active_dir is None:
            continue

        resolved_dir = _select_latest_version_dir(active_dir)
        spec_path = resolved_dir / "spec.md"
        plan_path = resolved_dir / "plan.md"
        user_story_path: Path = resolved_dir / "user-story.md"

        promoted_resolved_dir = (
            _select_latest_version_dir(promoted_feature_dir)
            if promoted_feature_dir is not None
            else None
        )
        promoted_story_path = (
            promoted_resolved_dir / "user-story.md" if promoted_resolved_dir is not None else None
        )

        promoted_story_text = _read_text(promoted_story_path) if promoted_story_path else ""
        if promoted_story_path is not None and not user_story_path.exists():
            user_story_path = promoted_story_path

        user_story_text = _read_text(user_story_path)
        if not user_story_text and promoted_story_text and promoted_story_path is not None:
            user_story_text = promoted_story_text
            user_story_path = promoted_story_path

        spec_text = _read_text(spec_path)
        plan_text = _read_text(plan_path)

        spec_parts: list[str] = []
        for heading in (
            "Context",
            "Root Cause",
            "Root Cause/Problem",
            "Problem",
            "Proposed Fix",
            "Acceptance Criteria",
            "Constraints & Risks",
            "Behavior",
            "Overview",
        ):
            section_text = parse_section(spec_text, heading)
            if section_text:
                spec_parts.append(f"{heading}: {truncate(section_text)}")

        plan_tasks = completed_plan_tasks(plan_text)
        plan_section = "\n".join(f"- {task}" for task in plan_tasks) if plan_tasks else ""
        verification_text = _verification_text(plan_text)
        verification_block = (
            "Plan verification notes:\n" + truncate(verification_text) if verification_text else ""
        )

        story_parts: list[str] = []
        story_statements = parse_section(user_story_text, "Story Statement")
        if story_statements:
            story_lines = [
                line.strip("- ") for line in story_statements.splitlines() if line.strip()
            ]
            if story_lines:
                story_parts.append(
                    "Story Statement:\n" + "\n".join(f"- {line}" for line in story_lines)
                )
        problem_section = parse_section(user_story_text, "Problem / Why")
        if problem_section:
            story_parts.append("Problem / Why:\n" + truncate(problem_section))
        if not story_parts and promoted_story_text:
            promoted_problem = parse_section(promoted_story_text, "Problem / Why")
            if not promoted_problem:
                promoted_problem = parse_section(promoted_story_text, "Summary")
            if promoted_problem:
                story_parts.append("Problem / Why:\n" + truncate(promoted_problem))

        lines: list[str] = [section(f"Feature doc: {feature}")]
        if story_parts:
            lines.append("User story excerpts:\n" + "\n\n".join(story_parts))
        if spec_parts:
            lines.append("Spec excerpts:\n" + "\n\n".join(spec_parts))
        if plan_section:
            lines.append("Plan completed tasks:\n" + plan_section)
        if verification_block:
            lines.append(verification_block)
        if len(lines) == 1:
            lines.append("(no spec/plan/user-story excerpts found)")

        context_files = [
            str(path.relative_to(root))
            for path in (spec_path, plan_path, user_story_path)
            if path.exists()
        ]
        issue_refs = extract_issue_references("\n".join([spec_text, plan_text, user_story_text]))
        excerpts.append(
            FeatureDocExcerpt(
                feature=feature,
                excerpt="\n".join(lines),
                issue_refs=issue_refs,
                context_files=sorted(set(context_files)),
            )
        )

    return excerpts
