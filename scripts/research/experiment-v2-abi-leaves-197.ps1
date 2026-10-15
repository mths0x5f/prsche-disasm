param([ValidateRange(1,99)][int]$Attempt=1)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot '../tool-env.ps1')
$leafRoot=Join-Path $PorscheProjectRoot 'local/experiments/v2-abi-analysis-197'
$leafSource=Join-Path $PorscheProjectRoot 'local/experiments/binary-index-ghidra'
$leafProject=Join-Path $leafRoot ('project-{0:D3}' -f $Attempt)
$leafOutput=Join-Path $PorscheProjectRoot ('iterations/v2/001-original-recovery/runs/197-call-free-abi/export/attempt-{0:D3}' -f $Attempt)
$leafContracts=Join-Path $PorscheProjectRoot 'iterations/v2/001-original-recovery/runs/197-call-free-abi/contracts-before-analysis.json'
if(-not(Test-Path -LiteralPath $leafContracts)){throw 'Run197 contract/proposal must exist before project copy/mutation'}
if((Test-Path -LiteralPath $leafProject)-or(Test-Path -LiteralPath $leafOutput)){throw 'Use a fresh197 attempt'}
function Get-LeafManifest {
 $leafFiles=@(Get-Item -LiteralPath (Join-Path $leafSource 'binary-index.gpr'))
 $leafFiles+=@(Get-ChildItem -LiteralPath (Join-Path $leafSource 'binary-index.rep') -File -Recurse|Sort-Object FullName)
 @($leafFiles|ForEach-Object{[ordered]@{path=$_.FullName.Substring($leafSource.Length+1).Replace('\','/');bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()}})
}
function Write-LeafJson($leafPath,$leafValue){$leafJson=($leafValue|ConvertTo-Json -Depth 10).Replace("`r`n","`n")+"`n";[IO.File]::WriteAllText($leafPath,$leafJson,(New-Object Text.UTF8Encoding($false)))}
$leafBefore=Get-LeafManifest
New-Item -ItemType Directory -Path $leafProject,$leafOutput -Force|Out-Null
Copy-Item -LiteralPath (Join-Path $leafSource 'binary-index.gpr') -Destination $leafProject
Copy-Item -LiteralPath (Join-Path $leafSource 'binary-index.rep') -Destination $leafProject -Recurse
$leafPins=@('scripts/research/experiment-v2-abi-leaves-197.ps1','scripts/research/ghidra/ExperimentAbiLeaves197.java','iterations/v2/001-original-recovery/runs/197-call-free-abi/contracts-before-analysis.json','local/tools/ghidra_12.1.3_PUBLIC/Ghidra/Features/Decompiler/lib/Decompiler.jar','local/tools/ghidra_12.1.3_PUBLIC/Ghidra/Features/Decompiler/os/win_x86_64/decompile.exe')|ForEach-Object{[ordered]@{path=$_;sha256=(Get-FileHash -LiteralPath (Join-Path $PorscheProjectRoot $_) -Algorithm SHA256).Hash.ToLowerInvariant()}}
$leafArgs=@($leafProject,'binary-index','-process','Porsche.exe','-noanalysis','-readOnly','-max-cpu','2','-scriptPath',(Join-Path $PSScriptRoot 'ghidra'),'-postScript','ExperimentAbiLeaves197.java',$leafOutput,$leafRoot,'-log',(Join-Path $leafRoot ('headless-{0:D3}.log' -f $Attempt)))
$ErrorActionPreference='Continue'
& (Join-Path $env:GHIDRA_INSTALL_DIR 'support/analyzeHeadless.bat') @leafArgs *> (Join-Path $leafRoot ('console-{0:D3}.log' -f $Attempt))
$leafExit=$LASTEXITCODE
$ErrorActionPreference='Stop'
$leafAfter=Get-LeafManifest
$leafUnchanged=(($leafBefore|ConvertTo-Json -Depth 5 -Compress)-ceq($leafAfter|ConvertTo-Json -Depth 5 -Compress))
Write-LeafJson (Join-Path $leafOutput 'provenance.json') ([ordered]@{schema=1;original_project_unchanged=$leafUnchanged;original_project_before=$leafBefore;original_project_after=$leafAfter;files=$leafPins;command=$leafArgs;headless_exit_code=$leafExit;copy_only_mutation=$true;autoanalysis=$false})
if(-not $leafUnchanged){throw 'Original project mutation detected'}
if($leafExit-ne 0-or-not(Test-Path -LiteralPath (Join-Path $leafOutput 'result.json'))){throw "Pilot incomplete: $leafRoot"}
Write-Output 'ABI197_CAPTURE_COMPLETE original_project_unchanged=True functions=2 stages=2'
