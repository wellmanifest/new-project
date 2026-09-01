param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9a-f]{40}$')]
    [string]$SourceRevision
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$fixtureRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('new project windows ' + [guid]::NewGuid())
$targetRoot = Join-Path $fixtureRoot 'target repository'

try {
    New-Item -ItemType Directory -Path $targetRoot -Force | Out-Null
    & python (Join-Path $repoRoot 'scripts/create_adoption_lock.py') `
        --target-root $targetRoot --source-revision $SourceRevision `
        --allow-unpublished-for-testing
    if ($LASTEXITCODE -ne 0) {
        throw "adoption failed with exit code $LASTEXITCODE"
    }

    & (Join-Path $targetRoot 'project.bat') --help *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "project.bat did not forward --help successfully: $LASTEXITCODE"
    }

    & (Join-Path $targetRoot 'project/governance-check.bat') --help *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "governance-check.bat did not forward --help successfully: $LASTEXITCODE"
    }

    $continuityRuntime = Join-Path $targetRoot '.governance/work_continuity.py'
    $continuitySchema = Join-Path $targetRoot '.governance/work-continuity.schema.json'
    if (-not (Test-Path $continuitySchema -PathType Leaf)) {
        throw 'work continuity schema was not adopted'
    }
    & python $continuityRuntime --help *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "work continuity runtime did not start successfully: $LASTEXITCODE"
    }

    Remove-Item (Join-Path $targetRoot '.governance/manifest.json')
    & (Join-Path $targetRoot 'project.bat') *> $null
    if ($LASTEXITCODE -eq 0) {
        throw 'project.bat did not propagate the missing-manifest failure'
    }

    Write-Host 'windows governance: PASS'
}
finally {
    Remove-Item -Recurse -Force $fixtureRoot -ErrorAction SilentlyContinue
}

exit 0
