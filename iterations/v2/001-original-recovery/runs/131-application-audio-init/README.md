# Run 131: application audio initialization

This packet recovers startup-domain behavior for `Porsche.exe`
`004a66b0..004a683d` (398 bytes) and the short post-setup helper
`004ab470..004ab4ae` (63 bytes). The direct caller
`004a6840` tests the first function's `AL` result; another caller is
`004a6a00`. Evidence is pinned to original SHA-256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.

The C++ retains the signed query/device-result branches, mode and gate tests,
the byte/word writes into the 124-byte local descriptor, table stride and
contents, the buffer/flag state, timer wait calculation, and post-setup call
arguments. `004ab470` is recovered as a small helper; its two device-control
calls remain external. Device-creation failure returns false without clearing
the computed configured flag, matching the original branch target. The
verifier also pins the raw 128-byte source range
`005b4ac0..005b4b3f`; table fields are left unnamed because their semantic
names are not established by this consumer.

The unknown audio/device effects stay typed boundaries: pre-initialization
`00565950`, descriptor query `00565680`, descriptor apply `005656d0`, device
creation `00565720`, timer wait `0053c380`, and control call `00565c70`.
Fixture boundaries supply the 124-byte descriptor and controlled signed
returns. The original query copies all 31 dwords into its output before the
caller reads it. No real audio device is opened. The original has no negative
mode guard: `-9` is covered by the pinned source-data window; `-10` reads
before it. Caller `004e48b4` supplies an opaque virtual-method result without
a proven range contract, so lower signed modes remain an explicit
partial-function input domain. Do not infer a guard from that boundary.

The eight original-x86 differential cases cover matching and nonmatching
capability bytes, gate bypass, mode `>= 3`, query failure, device failure,
configured-flag retention, timer/post-setup conditions, and negative timer
rates `-2` and `-1`. The timer conversion preserves the original
`CDQ; SUB EAX,EDX; SAR EAX,1` behavior. The verifier compares ordered calls,
descriptor bytes, state cells, stack cleanup and callee-saved registers.

```powershell
cmake -S iterations/v2/001-original-recovery/runs/131-application-audio-init `
  -B local/builds/v2/application-audio-init-131 -A Win32
cmake --build local/builds/v2/application-audio-init-131 --config Release
py -3 scripts/research/verify-v2-application-audio-init.py `
  --probe local/builds/v2/application-audio-init-131/bin/Release/application_audio_init_probe.exe `
  --report-dir iterations/v2/001-original-recovery/runs/131-application-audio-init
```
