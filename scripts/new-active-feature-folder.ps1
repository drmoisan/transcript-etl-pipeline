# Creates an active feature folder from the template.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string] $FeatureName,
    [switch] $Force,
    [string] $IssueNumber
)

function Format-Checklist {
    param([string] $Text)
    $lines = @()
    foreach ($line in ($Text -split "`r?`n")) {
        $trim = $line.Trim()
        if (-not [string]::IsNullOrWhiteSpace($trim)) {
            if ($trim -match '^\-\s*\[?\s*\]') {
                $lines += $trim
            } elseif ($trim -match '^\-') {
                $lines += $trim
            } else {
                $lines += "- [ ] $trim"
            }
        }
    }
    return ($lines -join "`r`n")
}

function Get-Section {
    param(
        [string] $Content,
        [string] $Name
    )
    $escaped = [regex]::Escape($Name)
    $pattern = "^\s*##\s+$escaped\s*\r?\n(.*?)(?=^\s*##\s+|\z)"
    $match = [regex]::Match(
        $Content,
        $pattern,
        [System.Text.RegularExpressions.RegexOptions]::Singleline -bor [System.Text.RegularExpressions.RegexOptions]::Multiline
    )
    if ($match.Success) {
        return $match.Groups[1].Value.Trim()
    }
    return ''
}

if ([string]::IsNullOrWhiteSpace($FeatureName)) {
    Write-Host 'Aborted: no feature name provided. Use -FeatureName.'
    exit 1
}

$namePattern = '^[a-z0-9]+([-_][a-z0-9]+)*$'
if ($FeatureName -notmatch $namePattern) {
    Write-Host "Aborted: '$FeatureName' is invalid. Use kebab/underscore-case letters/numbers (e.g., notes-feature or notes_feature)."
    exit 1
}

$workspace = Split-Path -Parent $PSScriptRoot
$template = Join-Path $workspace 'docs/features/templates/feature'
$target = Join-Path $workspace "docs/features/active/$FeatureName"

if (-not (Test-Path $template)) {
    Write-Host "Template folder not found: $template"
    exit 1
}

if ((Test-Path $target) -and -not $Force) {
    Write-Host "Target exists: $target. Use -Force to overwrite."
    exit 1
}

if (-not (Test-Path $target)) {
    New-Item -ItemType Directory -Path $target | Out-Null
}

Copy-Item $template\* $target -Recurse -Force
Write-Host "Created/updated: $target"

$filesToOpen = @()
$filesToOpen += (Join-Path $target 'user-story.md')
$filesToOpen += (Join-Path $target 'spec.md')
$filesToOpen += (Join-Path $target 'plan.md')

# Seed from a similarly named potential feature, if present
$normalizedName = $FeatureName -replace '_', '-'
$potentialDir = Join-Path $workspace 'docs/features/potential'
$potentialFile = $null
if (Test-Path $potentialDir) {
    $potentialFile = Get-ChildItem $potentialDir -File |
        Where-Object {
            $_.Name -like "*$normalizedName*.md" -and
            $_.Name -notin @('template.md', 'README.md')
        } |
        Sort-Object Name -Descending |
        Select-Object -First 1
}

if ($potentialFile) {
    $potentialContent = Get-Content -Raw -Path $potentialFile.FullName
    $problem = Get-Section -Content $potentialContent -Name 'Problem / Why'
    $behavior = Get-Section -Content $potentialContent -Name 'Proposed Behavior'
    $criteriaRaw = Get-Section -Content $potentialContent -Name 'Acceptance Criteria (early draft)'
    $constraints = Get-Section -Content $potentialContent -Name 'Constraints & Risks'
    $tests = Get-Section -Content $potentialContent -Name 'Test Conditions to Consider'

    $criteria = if ($criteriaRaw) { Format-Checklist $criteriaRaw } else { '' }
    $testsFormatted = if ($tests) { Format-Checklist $tests } else { '' }

    $issueMeta = $null
    if ($IssueNumber -and (Get-Command gh -ErrorAction SilentlyContinue)) {
        $json = & gh issue view $IssueNumber --json number,title,url,author,updatedAt
        if ($LASTEXITCODE -eq 0 -and $json) {
            $issueMeta = $json | ConvertFrom-Json
        }
    }

    $issueField = if ($issueMeta.number) { "#$($issueMeta.number)" } elseif ($IssueNumber) { "#$IssueNumber" } else { "#<id>" }
    $ownerField = if ($issueMeta.author.login) { $issueMeta.author.login } else { "name" }
    $updatedField = if ($issueMeta.updatedAt) { ([datetime]$issueMeta.updatedAt).ToString('yyyy-MM-dd') } else { "YYYY-MM-DD" }

    $userStoryPath = Join-Path $target 'user-story.md'
    $specPath = Join-Path $target 'spec.md'
    $planPath = Join-Path $target 'plan.md'

    $userStoryContent = @"
# $FeatureName - User Story

- Issue: $issueField
- Owner: $ownerField
- Status: Draft | In Progress | Complete
- Last Updated: $updatedField

## Problem / Why

$problem

## Personas & Scenarios

- Persona: ...
  - Scenario: ...

## User Stories

- As a ..., I want ..., so that ...
- As a ..., I want ..., so that ...

## Acceptance Criteria

$criteria

## Non-Goals

Call out what is explicitly excluded from this feature.
"@

    $specContent = @"
# $FeatureName - Spec

- Issue: $issueField
- Owner: $ownerField
- Last Updated: $updatedField

## Overview

$problem

## Behavior

$behavior

## Inputs / Outputs

- Inputs (CLI flags, files, env vars)
- Outputs (artifacts, logs, telemetry)

## API / CLI Surface

List commands, flags, request/response shapes, and examples.

## Data & State

Data flow, storage, or state changes introduced by this feature.

## Constraints & Risks

$constraints

## Definition of Done

- [ ] Behavior matches acceptance criteria (see user story)
- [ ] Tests updated/added
- [ ] Docs updated (README, docs/features/active/... links)
- [ ] Telemetry/logging (if applicable)

## Seeded Test Conditions (from potential)

$testsFormatted
"@

    $planContent = @"
# $FeatureName - Plan

- Issue: $issueField
- Owner: $ownerField
- Last Updated: $updatedField

## Required References (read, do not restate)

- Coding workflow and standards: [`docs/code-change.instructions.md`](../../code-change.instructions.md)
- Unit test policy: [`docs/unit-test-policy.md`](../../unit-test-policy.md)

**All work must comply with these policies; do not duplicate their content here.**

## Phases (nest work under each phase)

- Phase 1: <scope/goal>
  - [ ] Work item 1 (small enough for one prompt/session)
  - [ ] Work item 2
  - [ ] Tests/docs for this phase
- Phase 2: <scope/goal>
  - [ ] Work item 1
  - [ ] Work item 2
- Phase 3: <scope/goal>
  - [ ] Work item 1
  - [ ] Work item 2

## Test Plan

- Unit: ...
- Integration: ...
- CLI/UX examples: ...
- Performance/edge cases: ...

## Open Questions / Notes

Document decisions, risks, and follow-ups here.
"@

    Set-Content -Path $userStoryPath -Value $userStoryContent -Encoding UTF8
    Set-Content -Path $specPath -Value $specContent -Encoding UTF8
    Set-Content -Path $planPath -Value $planContent -Encoding UTF8

    Write-Host "Seeded user-story.md and spec.md from potential: $($potentialFile.Name)"
}

$codeCmd = Get-Command code -ErrorAction SilentlyContinue
if ($codeCmd) {
    $args = $filesToOpen | Where-Object { Test-Path $_ }
    if ($args.Count -gt 0) {
        Start-Process code -ArgumentList $args
    }
} else {
    Write-Host "VS Code 'code' command not found. Files to edit:"
    $filesToOpen | ForEach-Object { Write-Host "  $_" }
}
