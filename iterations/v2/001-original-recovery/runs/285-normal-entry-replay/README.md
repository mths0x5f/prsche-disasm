# Run285: actual normal-entry link, cached objects

Two actual links start from the existing Run102 host `_WinMain@16`, through
`win_main_004b6710` and `app_main_004b6a50`. Neither uses WHOLEARCHIVE, a custom
ENTRY, NOENTRY, forced unresolved symbols or fixture providers. No compilation
or executable execution occurred.

- [cached-001](cached-001.json): existing compatible five-library game-entry graph
  from `original-game-link-098`, exit1120, **267 names /303 references**, 0.202s.
- [candidates-002](candidates-002.json): same inputs plus the actual Run274
  1125-function candidate archive, exit1120, **the same267 names /303 references**,
  0.045s. The verbose log confirms the candidate archive was searched.

No EXE was produced. There were no other linker errors. These are fresh link
executions against cached libraries, not freshly rebuilt source closure. Run283
compares available caches; four098 libraries are newest among the available variants and the graph
is the one used by historical Run173; a newer window-binding variant has not
been substituted without equivalence proof. The candidate archive does not automatically
satisfy the canonical semantic service names requested by this entry graph;
connecting any owners still requires original-call and ABI evidence. Zero change
in this frontier does not mean the candidate work is worthless or semantically
accepted. Run274's414-name WHOLEARCHIVE diagnostic measures a different graph.

`app_main_004b6a50` directly requests20 unresolved services, including logging,
game setup, front-end display and per-frame subsystem calls. Next work should
trace original targets and connect proved existing owners, beginning with
`application_main_log`, then proceed along the real startup/rendering path.
The list in each report is an observed reachable frontier, not a count of all
remaining functions or an estimate of time to a complete game.

Run284 also identifies original initialization before WinMain. Run286 narrows
its first two constructors: no direct later consumer of their output was found.
They remain a startup-equivalence question, not a demonstrated launch blocker.
Constructor order, rendering, input, resources, real gameplay and the validation
backlog still require original comparison.

Unique local attempt directories preserve response files, full logs, commands,
exit codes, timing and input hashes before assertions. Read-only
`py -3 scripts/research/audit-v2-game-entry-285.py` passes18 input pins and records
22 searched-library hashes. The replay script's English-only search extraction
left its initial library-search maps empty under the Russian linker locale;
the separate audit parses both languages without repeating either link.

Do not rerun a completed attempt name. New link inputs require a new attempt:
`py -3 scripts/research/replay-v2-game-entry-285.py --attempt <new-name>`.
The default proposal is Run283's preserved unexecuted proposal. Local receipts
are under `local/experiments/v2-normal-entry-replay-285/`.

First logger navigation (not a completed packet): original004b6b0e pushes the
string at005d6e84,004b6b13 calls005a177b, and004b6b18 clears the accumulated
16-byte argument area. The return is unused here. Existing WIP canonical source
`source/recovered/Porsche.exe/formatter_stdio.cpp` contains
`formatter_stdio_printf_005a177b(const char*,...)`; the65-byte original body
calls005a3719/005a533e/005a4371/005a53cb/005a376b and uses stdout005e5508.
The registry and274 have no005a177b body. Reusing the entire old175 object would
also introduce eight other bodies/accepted overlaps and state dependencies;
next proof must isolate the exact source fragment and its call/state contract.
No printf alias, replacement implementation or fixture was added here.
