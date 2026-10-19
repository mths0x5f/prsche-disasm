# Next resource-file recovery boundaries

Original `Porsche.exe` SHA-256:
`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Index queries:00561b80,00561ca0 and their callers/callees in
`research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d` and
`research/v2/binaries/Porsche.exe-ddd748fdbe6d`. Run321 still has four object
references to `file_exists_00561b80` and one to pointer-return `file_open_00561ca0`.
These are not aliases of the accepted file-size leaf00561ba0.

- **Exists00561b80**,20B: reads canonical group005df770, forwards path/group to
  unrecovered00533f00, cleans eight bytes and returns EAX. Caller ABI is cdecl.
  The group has an accepted owner in `resource_dispatch_globals.cpp`.00533f00
  allocates/waits/completes a request through00568260/00567f70/00567df0; it stays
  an explicit boundary. A new exact wrapper may reuse the group, not substitute
  file-size lookup. The existing Run109 report already distinguishes these roles.
- **Open00561ca0**,63B: cdecl path/flags with pointer/raw EAX return. It forms a
  stack context with path+0, flags+8 and value1 at+12, obtains a device name via
  unresolved00568e90, then calls the accepted resource dispatcher00568d50 with
  distinct callback00561ce0. The accepted size leaf uses00561be0 and omits flags;
  it cannot supply this open behavior through a typed alias.
- **Interior callback00561ce0** is labeled LAB rather than indexed as a function.
  It extends toward00561df3 and uses open00533b90, size00533de0, allocation00531ca0,
  read00533bf0, close00533da0 and mutable transform callback006ad750. Its range,
  callback ABI, allocation/failure/read/close/transform consumers need tracing
  before an implementation can claim successful resource-open semantics.

Ownership checks covered the registry, recovered source and run bodies/interior
entries.00561ba0 has an owner;00561b80/00561ca0/00561ce0 have no accepted body.
The Run313 resource opener's pointer-return contract matches EAX, but its real
callee/state composition remains unverified.

Next bounded step: recover and fixture-test the exact20-byte exists wrapper
against PE EAX/ESP/nonvolatile/path/group behavior, keeping00533f00 unresolved.
Then extend the index for00561ce0 and trace open callback/device ABI/state before
recovering that path. No new game behavior or providers were introduced here.
