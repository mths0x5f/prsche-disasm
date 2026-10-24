param([int]$Runs = 20, [int]$Seconds = 22, [string]$Tag = 'g432', [string]$Dll)
# Same procedure as stress430native.ps1, plus: installs $Dll as gimme.dll for the runs and checks
# per run that SaveData\pic16.fsh was rewritten (ConvertFile ran). Restores gimme.dll.bak state.
$o = "D:\projetos\prsche-disasm\local\experiments\v2-lowered-exe-430"; $wd = "D:\projetos\prsche-disasm\local\run-430"
$env:PORSCHE430_NATIVE="1"; Remove-Item Env:PORSCHE430_TRACE, Env:PORSCHE430_TRACE_FILTER -ErrorAction SilentlyContinue
Copy-Item $Dll "$wd\gimme.dll" -Force
$pic = "$wd\SaveData\pic16.fsh"
$fails = 0; $converted = 0
for ($k = 1; $k -le $Runs; $k++) {
  $err = "$o\$Tag-$k.err"
  $before = (Get-Item $pic -ErrorAction SilentlyContinue).LastWriteTime
  $p = Start-Process -FilePath "$o\PorscheLowered.exe" -ArgumentList "Porsche.exe" -WorkingDirectory $wd -PassThru -RedirectStandardError $err -RedirectStandardOutput "$o\$Tag-$k.out"
  $t = 0; while (-not $p.HasExited -and $t -lt $Seconds) { Start-Sleep 1; $t++ }
  $alive = -not $p.HasExited
  Get-Process | Where-Object { $_.Name -match 'porsche' } | Stop-Process -Force -ErrorAction SilentlyContinue; Start-Sleep 2
  $after = (Get-Item $pic -ErrorAction SilentlyContinue).LastWriteTime
  $wrote = $after -ne $before; if ($wrote) { $converted++ }
  $stop = Select-String -Path $err -Pattern "fault while|no lowered|unlowered|exception" | Select-Object -First 1
  if (-not $alive -or $stop) { $fails++; "run $k FAIL alive=$alive t=$t pic16=$wrote $($stop.Line)" } else { "run $k ok pic16=$wrote" }
  Copy-Item $pic "$o\$Tag-$k-pic16.fsh" -ErrorAction SilentlyContinue
}
Remove-Item "$wd\gimme.dll" -Force
"total $Runs fails $fails converted $converted"
