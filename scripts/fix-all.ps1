#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Runs all code quality checks with auto-fix and intelligent retry logic.

.DESCRIPTION
    This script runs Black, Ruff, Pyright, and Pytest in sequence with the following logic:
    1. Run Black (auto-fix formatting)
    2. Run Ruff with --fix (auto-fix linting), retry if needed
    3. Re-run Black and Ruff to ensure consistency
    4. Run Pyright (halt on failure)
    5. Run Pytest with coverage (halt on failure)
    6. Confirm all checks pass if successful

.PARAMETER MaxRuffRetries
    Maximum number of times to retry Ruff fix before halting (default: 3)
#>

[CmdletBinding()]
param(
    [int]$MaxRuffRetries = 3
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Information ("`n==> {0}" -f $Message) -InformationAction Continue
}

function Write-Success {
    param([string]$Message)
    Write-Information ("OK: {0}" -f $Message) -InformationAction Continue
}

function Write-Failure {
    param([string]$Message)
    Write-Information ("FAIL: {0}" -f $Message) -InformationAction Continue
}

function Invoke-Command-WithStatus {
    param(
        [string[]]$Command,
        [string]$StepName
    )

    Write-Step $StepName
    $exe = $Command[0]
    $commandArgs = @()
    if ($Command.Count -gt 1) {
        $commandArgs = $Command[1..($Command.Count - 1)]
    }
    $output = & $exe @commandArgs 2>&1
    $exitCode = $LASTEXITCODE

    if ($output) {
        Write-Output $output
    }

    return $exitCode
}

# Step 1: Run Black formatting
Write-Step "Step 1: Running Black formatting..."
$exitCode = Invoke-Command-WithStatus @("poetry", "run", "black", ".") "Black: format"
if ($exitCode -ne 0) {
    Write-Failure "Black formatting failed. Please review errors above."
    exit 1
}
Write-Success "Black formatting completed successfully"

# Step 2: Run Ruff with fix, retry if needed
Write-Step "Step 2: Running Ruff linting with auto-fix..."
$ruffAttempt = 0
$ruffSuccess = $false

while ($ruffAttempt -lt $MaxRuffRetries) {
    $ruffAttempt++
    Write-Information ("Ruff attempt {0} of {1}..." -f $ruffAttempt, $MaxRuffRetries) -InformationAction Continue

    $exitCode = Invoke-Command-WithStatus @("poetry", "run", "ruff", "check", "--fix") "Ruff: fix"

    if ($exitCode -eq 0) {
        $ruffSuccess = $true
        Write-Success "Ruff linting passed"
        break
    }

    if ($ruffAttempt -lt $MaxRuffRetries) {
        Write-Information "Ruff found issues. Retrying..." -InformationAction Continue
    }
}

if (-not $ruffSuccess) {
    Write-Failure "Ruff linting failed after $MaxRuffRetries attempts. Please review errors above."
    exit 1
}

# Step 3: Re-run Black and Ruff to ensure consistency
Write-Step "Step 3: Re-running Black to ensure consistency..."
$exitCode = Invoke-Command-WithStatus @("poetry", "run", "black", ".") "Black: format (verify)"
if ($exitCode -ne 0) {
    Write-Failure "Black formatting failed on verification pass."
    exit 1
}
Write-Success "Black formatting verified"

Write-Step "Step 4: Re-running Ruff to verify fixes..."
$exitCode = Invoke-Command-WithStatus @("poetry", "run", "ruff", "check") "Ruff: lint (verify)"
if ($exitCode -ne 0) {
    Write-Failure "Ruff linting still has issues after fixes. Please review errors above."
    exit 1
}
Write-Success "Ruff linting verified"

# Step 5: Run Pyright type checking
Write-Step "Step 5: Running Pyright type checking..."
$exitCode = Invoke-Command-WithStatus @("poetry", "run", "pyright") "Pyright: type-check"
if ($exitCode -ne 0) {
    Write-Failure "Pyright type checking failed. Please review errors above."
    exit 1
}
Write-Success "Pyright type checking passed"

# Step 6: Run Pytest with coverage
Write-Step "Step 6: Running Pytest with coverage..."
$exitCode = Invoke-Command-WithStatus @(
    "poetry",
    "run",
    "pytest",
    "--cov=src/transcript_etl_pipeline",
    "--cov-report=term-missing"
) "Pytest: test with coverage"
if ($exitCode -ne 0) {
    Write-Failure "Pytest failed. Please review errors above."
    exit 1
}
Write-Success "Pytest passed"

# All checks passed
Write-Information "`n" -InformationAction Continue
Write-Information "========================================" -InformationAction Continue
Write-Information "ALL CHECKS PASSED" -InformationAction Continue
Write-Information "========================================" -InformationAction Continue
Write-Information "- Black formatting: PASS" -InformationAction Continue
Write-Information "- Ruff linting: PASS" -InformationAction Continue
Write-Information "- Pyright type checking: PASS" -InformationAction Continue
Write-Information "- Pytest with coverage: PASS" -InformationAction Continue
Write-Information "========================================`n" -InformationAction Continue

exit 0
