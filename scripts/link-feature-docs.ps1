# Updates a GitHub issue body to include links to feature docs (user story, spec, plan).
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory = $true)]
    [string] $IssueNumber,
    [Parameter(Mandatory = $true)]
    [string] $FeatureName
)

function Write-ScriptError($msg) {
    Write-Error $msg
    exit 1
}

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-ScriptError "gh CLI not found on PATH. Install gh and authenticate first."
}

$issueJson = & gh issue view $IssueNumber --json body
if ($LASTEXITCODE -ne 0 -or -not $issueJson) {
    Write-ScriptError "Unable to fetch issue #$IssueNumber. Check the number and gh auth."
}

$issue = $issueJson | ConvertFrom-Json
$body = $issue.body
if ([string]::IsNullOrWhiteSpace($body)) {
    Write-ScriptError "Issue #$IssueNumber has an empty body; aborting to avoid overwriting content."
}

# Normalize feature name to both underscore and hyphen variants for paths
$featurePath = $FeatureName

$docsBlock = @"
## Feature Docs
- [User Story](docs/features/active/$featurePath/user-story.md)
- [Spec](docs/features/active/$featurePath/spec.md)
- [Plan](docs/features/active/$featurePath/plan.md)
"@

function Format-OrAppendSection {
    param(
        [string] $Content,
        [string] $SectionHeading,
        [string] $Replacement
    )
    $pattern = "(?ms)^" + [regex]::Escape($SectionHeading) + "\s*\r?\n.*?(?=^\#\#\s+|\z)"
    $regex = New-Object System.Text.RegularExpressions.Regex(
        $pattern,
        [System.Text.RegularExpressions.RegexOptions]::Multiline -bor [System.Text.RegularExpressions.RegexOptions]::Singleline
    )
    if ($regex.IsMatch($Content)) {
        return $regex.Replace($Content, $Replacement.TrimEnd())
    }
    if ($Content.Trim().Length -eq 0) {
        return $Replacement.TrimEnd()
    }
    return $Content.TrimEnd() + "`n`n" + $Replacement.TrimEnd()
}

$newBody = Format-OrAppendSection -Content $body -SectionHeading "## Feature Docs" -Replacement $docsBlock

$tmp = [System.IO.Path]::ChangeExtension([System.IO.Path]::GetTempFileName(), '.md')
if ($PSCmdlet.ShouldProcess($tmp, "Write updated issue body")) {
    Set-Content -Path $tmp -Value $newBody -Encoding UTF8
}

if ($PSCmdlet.ShouldProcess("Issue #$IssueNumber", "Update issue body from temp file")) {
    & gh issue edit $IssueNumber --body-file $tmp
    $exit = $LASTEXITCODE
} else {
    $exit = 0
}

if ($PSCmdlet.ShouldProcess($tmp, "Remove temporary file")) {
    Remove-Item $tmp -ErrorAction SilentlyContinue
}

if ($exit -eq 0) {
    Write-Information ("Updated issue #{0} with Feature Docs links." -f $IssueNumber) -InformationAction Continue
} else {
    Write-ScriptError "Failed to update issue #$IssueNumber."
}
