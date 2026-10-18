# Shared recovery input manifests

New proof producers may share immutable input/source pin sets here. The pilot is
[Run294](../../../iterations/v2/001-original-recovery/runs/294-shared-input-manifests/README.md).
This does not merge execution results, migrate frozen reports or change game code.

`sha256/<digest>.json` is named by the SHA256 of its exact UTF-8/LF bytes. Schema1
contains `kind: recovery-pin-manifest`, `hash_mode` (`raw` or `crlf-to-lf`) and
repository-relative `files` mapping paths to SHA256. Content is never overwritten.
Changed pin sets create a new manifest or an explicit per-report delta.

A report references `source_manifest: {path, sha256}` or `input_manifest`.
Optional `source_delta`/`input_delta` adds or replaces paths; `_removed` explicitly
removes paths. A path cannot be removed and updated together. Inline `_sha256`
and a manifest reference cannot coexist in one scope. The producer owns its
report schema/version; the manifest format has an independent schema.

`scripts/research/v2_shared_manifests.py` provides `externalize` and
`ManifestReader.resolve/verify`. The reader also supports legacy inline pin maps;
callers must specify the historical hash mode for normalized legacy sources.
ProofCache reuses file reads and normalized hashes; manifest JSON is decoded once
per reader. SHA mismatch, mutation, missing manifest, invalid paths/schema and
contradictory deltas are rejected. Raw and normalized hashes are never inferred
to be interchangeable.

New shared manifests use repository-relative paths. External SDK/toolchain pins
and old absolute-path reports retain their existing format for now. Existing
legacy-only validators are not silently upgraded; new producers must use the
new reader. Ownership, COFF metadata and result schemas remain separate work.
