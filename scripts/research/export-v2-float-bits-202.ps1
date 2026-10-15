$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '../tool-env.ps1')
$floatRoot = Join-Path $PorscheProjectRoot 'local/experiments/v2-float-bits-202'
$floatExport = Join-Path $floatRoot 'export'
$floatProject = Join-Path $PorscheProjectRoot 'local/experiments/binary-index-ghidra'
if ((Test-Path -LiteralPath $floatExport) -and @(Get-ChildItem -LiteralPath $floatExport -File).Count) { throw 'Preserve existing capture; no automatic re-export' }
New-Item -ItemType Directory -Force -Path $floatRoot | Out-Null
$floatBaseline = Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $PorscheProjectRoot 'iterations/v2/001-original-recovery/runs/193-abi-storage-pilot/export/attempt-002/provenance.json') | ConvertFrom-Json
function Test-FloatOriginalProject {
    foreach ($floatFile in $floatBaseline.original_project_before) {
        $floatPath = Join-Path $floatProject $floatFile.path
        if ((Get-Item -LiteralPath $floatPath).Length -ne $floatFile.bytes -or (Get-FileHash -LiteralPath $floatPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $floatFile.sha256) { throw "Original project identity changed: $($floatFile.path)" }
    }
}
Test-FloatOriginalProject
$floatPins = @('scripts/research/export-v2-float-bits-202.ps1','scripts/research/ghidra/ExportRawFloatStores202.java','local/tools/ghidra_12.1.3_PUBLIC/Ghidra/Features/Decompiler/lib/Decompiler.jar','local/tools/ghidra_12.1.3_PUBLIC/Ghidra/Features/Decompiler/os/win_x86_64/decompile.exe') | ForEach-Object { [ordered]@{path=$_;sha256=(Get-FileHash -LiteralPath (Join-Path $PorscheProjectRoot $_) -Algorithm SHA256).Hash.ToLowerInvariant()} }
$floatArgs = @($floatProject,'binary-index','-process','Porsche.exe','-noanalysis','-readOnly','-max-cpu','2','-scriptPath',(Join-Path $PSScriptRoot 'ghidra'),'-postScript','ExportRawFloatStores202.java',$floatExport,'-log',(Join-Path $floatRoot 'headless.log'))
# Native Java warnings on stderr must not abort PowerShell's capture pipeline.
$ErrorActionPreference = 'Continue'
& (Join-Path $env:GHIDRA_INSTALL_DIR 'support/analyzeHeadless.bat') @floatArgs *> (Join-Path $floatRoot 'headless-console.log')
$floatExit = $LASTEXITCODE
$ErrorActionPreference = 'Stop'
Test-FloatOriginalProject
$floatConsole = Join-Path $floatRoot 'headless-console.log'
$floatText = [IO.File]::ReadAllText($floatConsole).Replace("`r`n","`n")
[IO.File]::WriteAllText($floatConsole,$floatText,[Text.UTF8Encoding]::new($false))
$floatProvenance = [ordered]@{schema=1;command=$floatArgs;files=$floatPins;headless_exit_code=$floatExit;original_project_unchanged=$true;project_manifest_files=79;project_manifest_bytes=572766909;original_project_baseline='iterations/v2/001-original-recovery/runs/193-abi-storage-pilot/export/attempt-002/provenance.json';read_only=$true;autoanalysis=$false}
$floatJson = ($floatProvenance | ConvertTo-Json -Depth 7).Replace("`r`n","`n") + "`n"
[IO.File]::WriteAllText((Join-Path $floatRoot 'capture-provenance.json'),$floatJson,[Text.UTF8Encoding]::new($false))
if ($floatExit -ne 0 -or -not (Test-Path -LiteralPath (Join-Path $floatExport 'result.json'))) { throw 'Incomplete202 capture; inspect preserved console' }
Write-Output 'RAW202_CAPTURE_COMPLETE functions=1 original_project_unchanged=True'
