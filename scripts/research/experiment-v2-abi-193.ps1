param([ValidateRange(1,99)][int]$Attempt=1)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '../tool-env.ps1')
$abiRoot = Join-Path $PorscheProjectRoot 'local/experiments/v2-abi-analysis-193'
$abiSource = Join-Path $PorscheProjectRoot 'local/experiments/binary-index-ghidra'
$abiProject = Join-Path $abiRoot ('project-{0:D3}' -f $Attempt)
$abiOutput = Join-Path $PorscheProjectRoot ('iterations/v2/001-original-recovery/runs/193-abi-storage-pilot/export/attempt-{0:D3}' -f $Attempt)
if ((Test-Path -LiteralPath $abiProject) -or (Test-Path -LiteralPath $abiOutput)) { throw 'Attempt exists; use a fresh attempt number' }
function Get-AbiManifest {
    $abiFiles = @(Get-Item -LiteralPath (Join-Path $abiSource 'binary-index.gpr'))
    $abiFiles += @(Get-ChildItem -LiteralPath (Join-Path $abiSource 'binary-index.rep') -File -Recurse | Sort-Object FullName)
    @($abiFiles | ForEach-Object { [ordered]@{ path=$_.FullName.Substring($abiSource.Length+1).Replace('\','/'); bytes=$_.Length; sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant() } })
}
$abiBefore = Get-AbiManifest
New-Item -ItemType Directory -Path $abiProject -Force | Out-Null
New-Item -ItemType Directory -Path $abiOutput -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $abiSource 'binary-index.gpr') -Destination $abiProject
Copy-Item -LiteralPath (Join-Path $abiSource 'binary-index.rep') -Destination $abiProject -Recurse
$abiPins = @('scripts/research/experiment-v2-abi-193.ps1','scripts/research/ghidra/ExperimentAbiAnalysis193.java','local/tools/ghidra_12.1.3_PUBLIC/Ghidra/Features/Decompiler/lib/Decompiler.jar','local/tools/ghidra_12.1.3_PUBLIC/Ghidra/Features/Decompiler/os/win_x86_64/decompile.exe') | ForEach-Object { [ordered]@{path=$_; sha256=(Get-FileHash -LiteralPath (Join-Path $PorscheProjectRoot $_) -Algorithm SHA256).Hash.ToLowerInvariant()} }
$abiArgs = @($abiProject,'binary-index','-process','Porsche.exe','-noanalysis','-readOnly','-max-cpu','2','-scriptPath',(Join-Path $PSScriptRoot 'ghidra'),'-postScript','ExperimentAbiAnalysis193.java',$abiOutput,$abiRoot,'-log',(Join-Path $abiRoot ('headless-{0:D3}.log' -f $Attempt)))
$ErrorActionPreference = 'Continue'
& (Join-Path $env:GHIDRA_INSTALL_DIR 'support/analyzeHeadless.bat') @abiArgs *> (Join-Path $abiRoot ('console-{0:D3}.log' -f $Attempt))
$abiExit = $LASTEXITCODE
$ErrorActionPreference = 'Stop'
$abiAfter = Get-AbiManifest
$abiUnchanged = (($abiBefore | ConvertTo-Json -Depth 5 -Compress) -ceq ($abiAfter | ConvertTo-Json -Depth 5 -Compress))
[ordered]@{schema=1; original_project_unchanged=$abiUnchanged; original_project_before=$abiBefore; original_project_after=$abiAfter; files=$abiPins; command=$abiArgs; headless_exit_code=$abiExit; copy_only_mutation=$true; autoanalysis=$false} | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath (Join-Path $abiOutput 'provenance.json') -Encoding UTF8
if (-not $abiUnchanged) { throw 'Original project mutation detected' }
if ($abiExit -ne 0 -or -not (Test-Path -LiteralPath (Join-Path $abiOutput 'result.json'))) { throw "Pilot incomplete; inspect $abiRoot/console.log" }
Get-Content -LiteralPath (Join-Path $abiOutput 'result.json')
