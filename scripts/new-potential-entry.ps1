# Creates a dated potential feature file from the template and opens it plus backlog.md.
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string] $ShortName
)

if ([string]::IsNullOrWhiteSpace($ShortName)) {
    Write-Error 'Aborted: no name provided. (Pass -ShortName or use the VS Code task prompt.)'
    exit 1
}

$shortPattern = '^[a-z0-9]+(-[a-z0-9]+)*$'
if ($ShortName -notmatch $shortPattern) {
    Write-Error "Aborted: '$ShortName' is invalid. Use kebab-case letters/numbers only (e.g., notes-feature)."
    exit 1
}

$workspace = Split-Path -Parent $PSScriptRoot
$today = Get-Date -Format 'yyyy-MM-dd'
$target = Join-Path $workspace "docs/features/potential/$today-$ShortName.md"
$template = Join-Path $workspace 'docs/features/potential/template.md'
$backlog = Join-Path $workspace 'docs/features/backlog.md'

if ($PSCmdlet.ShouldProcess($target, "Copy template file")) {
    Copy-Item $template $target -Force
}
Write-Information ("Created: {0}" -f $target) -InformationAction Continue

# Populate placeholders in the new file
$author = (git config user.name) 2>$null
if (-not $author -or [string]::IsNullOrWhiteSpace($author)) {
    $author = $env:USERNAME
}
if (-not $author) { $author = 'Unknown' }

$content = Get-Content -Raw -Path $target
$content = $content -replace '<feature-name>', $ShortName
$content = $content -replace 'YYYY-MM-DD', $today
$content = $content -replace '- Author: name', "- Author: $author"
if ($PSCmdlet.ShouldProcess($target, "Update template placeholders")) {
    Set-Content -Path $target -Value $content -Encoding UTF8
}

$codeCmd = Get-Command code -ErrorAction SilentlyContinue
if ($codeCmd) {
    if ($PSCmdlet.ShouldProcess("VS Code", "Open potential entry and backlog")) {
        Start-Process code -ArgumentList @($target, $backlog)
    }
} else {
    Write-Warning "VS Code 'code' command not found. Open files manually:"
    Write-Information ("  {0}" -f $target) -InformationAction Continue
    Write-Information ("  {0}" -f $backlog) -InformationAction Continue
}
