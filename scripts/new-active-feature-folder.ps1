# Creates an active feature folder from the template.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string] $FeatureName,
    [switch] $Force
)

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

$filesToOpen = @(
    Join-Path $target 'user-story.md',
    Join-Path $target 'spec.md',
    Join-Path $target 'plan.md'
)

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
