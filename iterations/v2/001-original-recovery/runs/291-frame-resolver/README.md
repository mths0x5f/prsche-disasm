# Run291: recover the resolver's original pointer result

Original `Porsche.exe` `004898f0..00489908` is25 bytes, RET8. It copies the
DWORD at `this+0x14` into an8-byte output, clears byte4, leaves byte5 unchanged,
writes the low16 bits of the second stack argument into word6, and returns the
output pointer in EAX. `00487e20` immediately dereferences that returned pointer.

Run187 already compiled a raw candidate for this VA, but its declaration returns
void and its emitted EAX is unsuitable for this consumer. The new implementation
uses Run290's existing thiscall declaration. It is a typed replacement of an
existing candidate VA, **not another distinct recovered address**. The old
source/object hashes and mangle are recorded in `summary.json`; future raw
unions must replace the old row explicitly. The game293 graph includes only the
new typed source and never links raw187/274.

One `/MP6` batch compiled the game TU and a private fixture. The reference COFF
contains the exact25 original PE bytes with zero relocations.512 native pairs
cover full-DWORD source patterns, high stack-tag bits, eight output offsets
including input/output overlap, all128 surrounding bytes, byte5, returned
pointer, RET8 stack cleanup, nonvolatile registers and DF. Existing five direct
Unicorn cases are retained; the new native oracle adds broader alias coverage.
Compilation, link and native execution all passed on the first attempt.

Only `004898f0.cpp` is a game source. It introduces no global/provider and has
zero undefined symbols. `fixture.cpp` and its reference body are private tests.
Faults, arbitrary caller-stack aliases and full-game behavior remain unproved.
See `summary.json`, `validation.json`, and the combined independent293 audit.
