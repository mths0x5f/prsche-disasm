# Run261 — canonical reuse in the actual native union

The existing Run249 inputs plus Run259's two canonical C++ bodies and two
directive-only bindings form **1122 distinct function VAs + 15 support objects**:
1137 archive members, 1,290,344 bytes. Archive SHA-256:
`94b6cbdf83cf5a98ff44fae1e79998745649ddf252d9e5d2d24752d8a355a88f`.

The actual diagnostic link leaves **417 names / 579 diagnostics**, versus
418 / 602 in Run249. It resolves raw 0059f050 and 005a66a7 names and exposes
the real canonical dependency `porsche::free_00531f90(void*)`. No EXE/DLL exists.
The linked frontier is 87 missing function bodies, 33 canonical owners outside
the union, 283 data names and 14 remaining contracts. Counts describe this
diagnostic candidate union, not the full game's remaining work.

1133 cached symbol snapshots reused; only four new COFFs inspected.
7461 input pins pass before and after; zero compiler commands, one archive and
one link, collector 8.811 seconds. [validation.json](validation.json) records
the exact summary identity and closure checks. Run173's verified production
set remains 476 full + 6 partial functions.

The first collector preflight stopped before native commands because Run259
declared only its project include root. Its metadata was corrected against the
successful compiler receipt's five ordered roots; the same COFFs were reused.
The failed log remains `local/reports/v2-union-261-preflight-failed.log`.

Reproduce the recorded command using [command.json](command.json), choosing a
fresh output/run path rather than overwriting the completed run:

```powershell
$command = Get-Content iterations/v2/001-original-recovery/runs/261-canonical-reuse-union/command.json -Raw | ConvertFrom-Json
$command[[Array]::IndexOf($command,'--output')+1] = 'local/experiments/v2-native-union-261-replay'
$command[[Array]::IndexOf($command,'--run')+1] = 'local/reports/v2-native-union-261-replay'
$program = $command[0]
$arguments = $command[1..($command.Count-1)]
& $program @arguments
```

Actual outputs are under `local/experiments/v2-native-union-261/`; the original
game directory was read only. Function/provider composition, ABI corrections,
the validation backlog and full-game execution remain open.
