# Scripts Directory

This directory contains utility scripts for the transcript-etl-pipeline project.

## Available Scripts

### collect-commit-context.ps1

Collects comprehensive Git context for generating commit messages.

**Usage:**
```powershell
.\scripts\collect-commit-context.ps1 [-Output <path>]
```

**Parameters:**
- `-Output` (optional): Output file path (default: `artifacts/commit_context.txt`)

**Features:**
- Repository remotes and current branch information
- Staged and unstaged changes with diffs
- Untracked files listing
- Diff statistics (staged + unstaged)
- Changed Python files
- Last commit information
- Placeholder for commit message intent

**Output:**
Creates a comprehensive context file suitable for generating conventional commit messages with AI assistance.

**Example:**
```powershell
# Default output location
.\scripts\collect-commit-context.ps1

# Custom output location
.\scripts\collect-commit-context.ps1 -Output "my-commit-context.txt"
```

---

### collect-pull-request-context.ps1

Collects comprehensive Git context for generating pull request descriptions.

**Usage:**
```powershell
.\scripts\collect-pull-request-context.ps1 [-Base <ref>] [-Head <ref>] [-Out <path>] [-RepoRoot <path>] [-Append] [-NoUntracked]
```

**Parameters:**
- `-Base` (optional): Base branch/ref for comparison (auto-detects main/master if not provided)
- `-Head` (optional): Head branch/ref for comparison (defaults to current branch)
- `-Out` (optional): Output file path (default: `artifacts\pr_context.txt`)
- `-RepoRoot` (optional): Repository root path (default: `.`)
- `-Append`: Append to existing output file instead of overwriting
- `-NoUntracked`: Skip listing untracked files

**Features:**
- Repository remotes and branch metadata
- Current branch and upstream information
- Working tree status (staged/unstaged/untracked files)
- Complete diffs for staged and unstaged changes
- PR comparison context:
  - Commits in range with authors and dates
  - Conventional commit type summary
  - Changed files with name-status
  - Diff statistics (additions/deletions)
  - Files grouped by extension
  - Referenced issues (#123, PROJ-456)
  - Complete diff stat

**Output:**
Creates a comprehensive context file suitable for generating detailed pull request descriptions with AI assistance.

**Examples:**
```powershell
# Default: Compare current branch with main/master
.\scripts\collect-pull-request-context.ps1

# Explicit base and head branches
.\scripts\collect-pull-request-context.ps1 -Base origin/main -Head feature/new-feature

# Custom output location
.\scripts\collect-pull-request-context.ps1 -Out "pr-context.txt"

# Skip untracked files for cleaner output
.\scripts\collect-pull-request-context.ps1 -NoUntracked

# Append to existing context file
.\scripts\collect-pull-request-context.ps1 -Append
```

---

## Output Directory

Both scripts write to the `artifacts/` directory by default, which is included in `.gitignore` to avoid committing generated context files.

## Requirements

- **PowerShell 5.1 or later** (both scripts are compatible with Windows PowerShell 5.1 and PowerShell 7+)
- **Git** must be installed and available in PATH
- Must be run from within a Git repository

## Notes

- Both scripts use UTF-8 encoding for output files
- Scripts automatically detect the repository root
- Error handling ensures graceful failures with informative messages
- Output is formatted for readability and AI processing
