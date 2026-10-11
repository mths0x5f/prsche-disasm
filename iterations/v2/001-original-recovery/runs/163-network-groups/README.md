# Run163 - network groups

Original source: Porsche.exe SHA256
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index query starts with unresolved0048bda0 from complete00492770; all direct
callees and their callers identify six complete bodies:0048bda0(311 bytes),
0048c220(135),0048c300(85),00490b70(50),0048a390(61),0048baa0(134).

The C++ preserves captured signed member index, modulo32 x86 byte shifts,
acknowledgement/mask order, duplicate membership removal, message pool+88,
sentinel lifetime and callback-dependent pointer reloads. State packets use
big-endian24-bit identity and little-endian32-bit member count. Actual recovered
0048c870 and0048b660 execute in the private oracle. Unknown locks, fill/copy
and virtual slot0 are scripted boundaries, never production stubs.

The unsized005e8e50 text dependency deliberately has no production owner.
Original initial byte is zero in the virtual tail of .data; that fact does not
prove an extent or resolve conflicting older one/32-byte aliases. Fixture text
lengths0/1/20/210 exercise the actual bounded serializer.005e8bfc table remains
unproved storage and is untouched.

Native vtable identity investigation is recorded below; frozen151/155 are
unchanged. Native relocation is a separate pending integration.

Validation:
```
. ./scripts/tool-env.ps1
cmake -S iterations/v2/001-original-recovery/runs/163-network-groups -B local/builds/v2/network-groups-163 -A Win32
cmake --build local/builds/v2/network-groups-163 --config Release -- /m
py -3 scripts/research/verify-v2-network-groups.py --report-dir iterations/v2/001-original-recovery/runs/163-network-groups
```

Vtable evidence: original words005b4968->0048ad70,005b4970->005a1056,
005b4978->0048b340 and preceding RTTI pointers005c5190/005c51d8/005c5228
all have PE HIGHLOW relocations. Constructor/destructor assignments have
relocations too. Slot0 callers0048a3b8/0048bb1c/0048c946/0048c96e pass
thiscall(sender,destination,packet,size), three stack arguments.0048ad70
ignores destination and queues a copied packet;0048b340 first dereferences
destination, invokes0048a3d0 and conditionally stores it in list+18.
005a1056 calls CRT fatal005a2e22 with code25. No substitute virtual effect
or synthetic fatal-return ABI is supplied.

The targets are absent from functions.jsonl/manual-functions.jsonl:
0048ad70..0048ae2b(188 bytes,RET12),0048b340..0048b3b9(122,RET12),
005a1056..005a105e(9,RET0). The report records exact target/body SHA and
coverage gaps. Next: supplement index, recover these complete targets and
0048a920/0048a8d0/0048a3d0/0055d4a0, trace RTTI consumers, then integrate
canonical native table owners. Table extent and RTTI layout remain unclaimed.

Validation passed173 cases with native MSVC19.44 Win32 and original Unicorn.
