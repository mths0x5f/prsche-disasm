# Run294: share input pins, preserve separate build results

The two captured293 builds have the same380 source pins. Their new schema2
reference reports point to one immutable content-addressed manifest, while each
retains its own original report and execution-receipt identity. The failed
build001 is not relabelled as a successful compilation. Neither build is rerun.

The repeated pin payload is118624 bytes inline versus59847 bytes for one shared
manifest plus two references: **49.55% less for this component**. This is not a
49.55% reduction of the whole repository: frozen legacy reports remain in Git,
and the pilot adds reference files. Future reports avoid those duplicate pin maps.

The common reader handles both legacy inline and new reference formats. It
supports explicit additions/replacements/removals, repository-relative paths,
separate raw/CRLF-normalized modes, immutable manifest bytes and mutation guards.
One reader loads the manifest once and reads/hashes the380 sources once for both
reports, reusing existing ProofCache. Nine unit tests pass, including corrupt or
missing manifests, mode confusion, path traversal, ambiguous metadata, actual
changed-source delta verification and input mutation after caching.

The first unit-test invocation was blocked by Windows temporary-directory
permissions in the sandbox. The separately approved invocation passed. WIP
metadata was finalized after helper/test coverage changes; its original bytes
were retained locally. The two captured build documents and the shared manifest
were checked unchanged during that metadata finalization.

`summary.json`/`validation.json` record the producer checks. Independent
`audit.json` checks exact old/new pin equality, distinct actual receipts, SHA
closure and byte accounting without compilation or native execution.

```powershell
py -3 scripts/research/test_v2_shared_manifests.py
py -3 scripts/research/audit-v2-shared-manifests-294.py
```

Scope: source/input closures only. Existing frozen reports and legacy validators
are preserved; new producers must call the shared reader. This does not yet
centralize toolchain/COFF/ownership schemas or provide game-behavior acceptance.
The game checkpoint remains293:151 compiled TUs,269 unresolved names, no EXE.
