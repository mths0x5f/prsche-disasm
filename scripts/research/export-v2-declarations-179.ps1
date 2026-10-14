param([ValidateRange(1,3600)][int]$FunctionTimeout=30,[ValidateRange(0,5772)][int]$Limit=0,[ValidatePattern('^$|^[0-9a-f]{64}$')][string]$FinalizeCapturedIdentity='')
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot '../tool-env.ps1')
$declarationsOutput=Join-Path $PorscheProjectRoot 'iterations/v2/001-original-recovery/runs/179-ghidra-declarations/export'
$declarationsProject=Join-Path $PorscheProjectRoot 'local/experiments/binary-index-ghidra'
$declarationsScripts=Join-Path $PSScriptRoot 'ghidra'
$declarationsLog=Join-Path $PorscheProjectRoot 'local/reports/179-ghidra-declarations.log'
$declarationsCheckpoints=Join-Path $PorscheProjectRoot 'local/experiments/v2-declarations-179/checkpoints'
if(-not(Test-Path -LiteralPath (Join-Path $declarationsProject 'binary-index.gpr'))){throw 'Existing analyzed project missing'}
New-Item -ItemType Directory -Force -Path $declarationsOutput | Out-Null
$declarationsPins=@('scripts/research/ghidra/ExportRecoveryDeclarations179.java','scripts/research/export-v2-declarations-179.ps1','local/tools/ghidra_12.1.3_PUBLIC/Ghidra/Features/Decompiler/lib/Decompiler.jar','local/tools/ghidra_12.1.3_PUBLIC/Ghidra/Features/Decompiler/os/win_x86_64/decompile.exe','local/tools/ghidra_12.1.3_PUBLIC/Ghidra/Framework/SoftwareModeling/lib/SoftwareModeling.jar','local/tools/ghidra_12.1.3_PUBLIC/Ghidra/Features/Base/lib/Base.jar','local/tools/ghidra_12.1.3_PUBLIC/Ghidra/Framework/Utility/lib/Utility.jar') | ForEach-Object { [ordered]@{path=$_;sha256=(Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $PorscheProjectRoot $_)).Hash.ToLowerInvariant()} }
$declarationsPinText=$declarationsPins | ConvertTo-Json -Compress
$declarationsHash=[System.Security.Cryptography.SHA256]::Create()
try { $declarationsIdentity=([BitConverter]::ToString($declarationsHash.ComputeHash([Text.Encoding]::UTF8.GetBytes($declarationsPinText)))).Replace('-','').ToLowerInvariant() } finally { $declarationsHash.Dispose() }
$declarationsCaptured=$declarationsIdentity
if($FinalizeCapturedIdentity){
    $declarationsCapturePath=Join-Path $declarationsOutput 'capture-provenance.json'
    if(-not(Test-Path -LiteralPath $declarationsCapturePath)){Copy-Item -LiteralPath (Join-Path $declarationsOutput 'provenance.json') -Destination $declarationsCapturePath}
    $declarationsCapture=Get-Content -Raw -LiteralPath $declarationsCapturePath | ConvertFrom-Json
    if($declarationsCapture.export_identity_sha256 -ne $FinalizeCapturedIdentity){throw 'Finalize capture identity mismatch'}
    foreach($declarationsPin in $declarationsCapture.files){if($declarationsPin.path -notlike 'scripts/*' -and (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $PorscheProjectRoot $declarationsPin.path)).Hash.ToLowerInvariant() -ne $declarationsPin.sha256){throw 'Finalize requires unchanged captured Ghidra tools'}}
    $declarationsCaptured=$FinalizeCapturedIdentity
}
$declarationsCheckpoints=Join-Path $declarationsCheckpoints $declarationsCaptured
[ordered]@{schema=2;export_identity_sha256=$declarationsIdentity;capture_identity_sha256=$declarationsCaptured;finalize_only=[bool]$FinalizeCapturedIdentity;files=$declarationsPins;function_timeout=$FunctionTimeout;analysis='cached existing project; -noanalysis -readOnly';original_sha256='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $declarationsOutput 'provenance.json') -Encoding UTF8
$declarationsArgs=@($declarationsProject,'binary-index','-process','Porsche.exe','-noanalysis','-readOnly','-max-cpu','2','-scriptPath',$declarationsScripts,'-postScript','ExportRecoveryDeclarations179.java',$declarationsOutput,"$FunctionTimeout","$Limit",$declarationsCheckpoints,$declarationsIdentity)
if($FinalizeCapturedIdentity){$declarationsArgs+=$FinalizeCapturedIdentity}
$declarationsArgs+=@('-log',$declarationsLog)
& (Join-Path $env:GHIDRA_INSTALL_DIR 'support/analyzeHeadless.bat') @declarationsArgs
if($LASTEXITCODE -ne 0){throw "Ghidra export failed; inspect $declarationsLog"}
$declarationsProgress=Join-Path $declarationsOutput 'progress.json'
if(-not(Test-Path -LiteralPath $declarationsProgress)){throw 'Post-script completion marker missing; inspect log'}
Get-Content -LiteralPath $declarationsProgress
$declarationsState=Get-Content -Raw -LiteralPath $declarationsProgress | ConvertFrom-Json
if($declarationsState.schema -ne 2 -or $declarationsState.attempted -lt 1){throw 'Missing current exporter completion marker'}
if($Limit -eq 0 -and (-not $declarationsState.complete -or $declarationsState.total -ne 5772)){throw 'Incomplete function export; resume the same command'}
if($declarationsState.failed_total -gt 0 -or $declarationsState.high_global_declaration_errors -gt 0 -or $declarationsState.listing_declaration_errors -gt 0){throw 'Export contains explicit failures; inspect functions.jsonl and progress.json'}
exit 0
