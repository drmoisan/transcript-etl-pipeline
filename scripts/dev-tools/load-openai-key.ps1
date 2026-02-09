<#
.SYNOPSIS
Loads an OpenAI API key from LastPass and sets it as an environment variable.

.DESCRIPTION
This script is a developer convenience for workflows that depend on an OpenAI API key
(e.g., running local tools that call the OpenAI API). It retrieves a secret value from
LastPass using the `lpass` CLI and stores it in the current process environment via
the `Env:` drive.

The secret retrieval is implemented in small functions to keep the behavior testable
via Pester with mocks.

.NOTES
- Requires the LastPass CLI (`lpass`) to be installed and authenticated.
- State-changing behavior is guarded by ShouldProcess so you can use -WhatIf.
#>

[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'Medium')]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $ItemName,

    [Parameter()]
    [ValidateNotNullOrEmpty()]
    [string] $EnvVar = 'OPENAI_API_KEY'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-LPassExe {
    <#
    .SYNOPSIS
    Invokes the `lpass` CLI with the provided arguments.

    .DESCRIPTION
    Wraps `lpass` execution to provide consistent error handling and to allow unit
    tests to mock the external process.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [string[]] $LpassArgs
    )

    $output = & lpass @LpassArgs
    if ($LASTEXITCODE -ne 0) {
        throw ("lpass exited with code {0}. Args: {1}" -f $LASTEXITCODE, ($LpassArgs -join ' '))
    }

    return $output
}

function Get-LPassSecret {
    <#
    .SYNOPSIS
    Retrieves a secret value from LastPass.

    .PARAMETER ItemName
    The LastPass item name to retrieve.

    .OUTPUTS
    System.String
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [string] $ItemName
    )

    # We explicitly verify that `lpass` is available so failures are immediate and actionable.
    $null = Get-Command -Name 'lpass' -ErrorAction Stop

    # We expect the item to be stored as a note; adjust flags if your LastPass item differs.
    $secret = Invoke-LPassExe -LpassArgs @('show', '--notes', $ItemName)

    if ([string]::IsNullOrWhiteSpace($secret)) {
        throw "LastPass returned an empty secret for item: $ItemName"
    }

    return $secret
}

function Invoke-LoadOpenAIKey {
    <#
    .SYNOPSIS
    Loads an OpenAI API key from LastPass and sets it into the Env: drive.

    .PARAMETER ItemName
    LastPass item name containing the secret.

    .PARAMETER EnvVar
    Environment variable name to set.
    #>

    [CmdletBinding(SupportsShouldProcess = $true)]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [string] $ItemName,

        [Parameter(Mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [string] $EnvVar
    )

    $secret = Get-LPassSecret -ItemName $ItemName
    $envPath = "Env:$EnvVar"

    if ($PSCmdlet.ShouldProcess($envPath, "Set environment variable from LastPass secret")) {
        Set-Item -Path $envPath -Value $secret
    }
}

Invoke-LoadOpenAIKey -ItemName $ItemName -EnvVar $EnvVar
