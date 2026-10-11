# Run142 - audio transition and shutdown

Porsche.exe SHA256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Four full bodies:004a6a00 (375B),004ab470 (63B),004ab4b0 (47B),
00565890 (135B). Index queries followed functions/calls/references to the
original disassembly. The verifier pins all four indexed byte ranges and the
five-argument caller at004e48a2..004e48b8, plus the original audio-heap string.

004a6a00 compares prior mode/configuration/flag before changing anything;
mode3 forces the first argument's low byte to1, while its second argument is
unused. Cleanup releases the canonical final audio record and current buffer;
restart seeds eight records, then follows the original initializer result.
The virtual-method-derived mode is copied unchanged, including negative bits:
this confirms that Run131 cannot justify a clamp or a nonnegative domain.

00565890 invokes control, three optional callbacks, quiet, the fourth optional
callback, backend stop and two releases in original order. It reloads each
callback and each release pointer after preceding effects. Its final return
is the actual backend-close return; inactive state returns-10.004ab4b0 reloads
its auxiliary pointer after control and releases it;004ab470 preserves both
control argument sets and clears the two post-init bytes.

Canonical Run128 records/application cells, Run133 audio bytes and shared
application arena are reused. The two post-init bytes alias the existing
frame-services storage, with native pointer identity checked; they do not get
separate owners. Two new cells are proven PE zero-fill, not invented initialized
runtime state. The private probe owns only its fixture
version of Run133 storage and never links a replacement into production.
Known callers ignore incidental EAX of the three void bodies; no arbitrary
register-result contract is claimed for them.

26 native/original-x86 cases compare the entire3977-DWORD application arena,
all eight audio records,396 audio/predecessor bytes, nine scalar/byte cells,
ordered effect arguments and00565890's return. Callback mutations verify
reloads of later callbacks/handles. Three composed cases execute real004a6840
and the recovered shutdown bodies on both sides. Native callback addresses
are normalized only in their four confirmed pointer cells after identity is
established; no arbitrary state is normalized. External initializer, allocator,
control, device and backend effects remain explicit controlled boundaries.
There is no live audio, CRT or full-game startup acceptance.

```powershell
. ./scripts/tool-env.ps1
cmake -S iterations/v2/001-original-recovery/runs/142-audio-lifecycle -B local/builds/v2/audio-lifecycle-142 -A Win32
cmake --build local/builds/v2/audio-lifecycle-142 --config Release
py -3 scripts/research/verify-v2-application-audio-lifecycle.py --probe local/builds/v2/audio-lifecycle-142/bin/Release/application_audio_lifecycle_probe.exe --report-dir iterations/v2/001-original-recovery/runs/142-audio-lifecycle
```

Next: recover005659f0 and backend close/release, then the virtual method
producing mode in004e48b4. Run131 remains isolated until its data-read domain
and initializer closure are recovered. Source and verifier closure SHA pins
are in verification.json.
