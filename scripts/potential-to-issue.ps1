# Creates a GitHub issue from a potential feature file using gh.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string] $PotentialPath
)

function Fail($msg) {
    Write-Host $msg
    exit 1
}

$resolved = $null
try {
    $resolved = (Resolve-Path $PotentialPath -ErrorAction Stop).Path
} catch {
    Fail "Potential file not found: $PotentialPath"
}

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Fail "gh CLI not found on PATH. Install gh and authenticate first."
}

$content = Get-Content -Raw -Path $resolved
if ([string]::IsNullOrWhiteSpace($content)) {
    Fail "Potential file is empty: $resolved"
}

$headingMatch = [regex]::Match(
    $content,
    '^\s*#\s+(.+)$',
    [System.Text.RegularExpressions.RegexOptions]::Multiline
)
$featureName = $null
if ($headingMatch.Success) {
    $featureName = $headingMatch.Groups[1].Value.Trim()
    $featureName = $featureName -replace '\(Potential\)', ''
    $featureName = $featureName.Trim()
}
if (-not $featureName) {
    $featureName = (Split-Path $resolved -Leaf) -replace '\.md$', ''
}
$issueTitle = "Feature: $featureName"

function Get-Section([string] $name) {
    $escaped = [regex]::Escape($name)
    $pattern = "^##\s+$escaped\s*\r?\n(.*?)(?=^##\s+|\z)"
    $m = [regex]::Match(
        $content,
        $pattern,
        [System.Text.RegularExpressions.RegexOptions]::Singleline -bor [System.Text.RegularExpressions.RegexOptions]::Multiline
    )
    if ($m.Success) { return $m.Groups[1].Value.Trim() }
    return ''
}

$problem = Get-Section 'Problem / Why'
$behavior = Get-Section 'Proposed Behavior'
$criteria = Get-Section 'Acceptance Criteria (early draft)'
$constraints = Get-Section 'Constraints & Risks'
$tests = Get-Section 'Test Conditions to Consider'

if (-not $problem) { $problem = '(not provided in potential file)' }
if (-not $behavior) { $behavior = '(not provided in potential file)' }
if (-not $criteria) { $criteria = '(not provided in potential file)' }
if (-not $constraints) { $constraints = '(not provided in potential file)' }
if (-not $tests) { $tests = '(not provided in potential file)' }

$workspace = Split-Path -Parent $PSScriptRoot
$relativePath = $resolved
if (Test-Path $workspace) {
    $relativePath = [System.IO.Path]::GetRelativePath($workspace, $resolved)
}

$body = @"
## Problem / Why
$problem

## Proposed Behavior
$behavior

## Acceptance Criteria
$criteria

## Constraints & Risks
$constraints

## Test Conditions
$tests

## Source
From: $relativePath
"@

$tmp = [System.IO.Path]::ChangeExtension([System.IO.Path]::GetTempFileName(), '.md')
Set-Content -Path $tmp -Value $body -Encoding UTF8

Write-Host "Creating issue: $issueTitle"
& gh issue create --title "$issueTitle" --body-file "$tmp" --label "enhancement"
$exit = $LASTEXITCODE

Remove-Item $tmp -ErrorAction SilentlyContinue
exit $exit
