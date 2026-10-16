"""Read-only acceptance audit for the frozen Run 221 evidence.

This deliberately reads existing artifacts only.  It does not invoke a compiler,
linker, native executable, Ghidra, or allocate production storage.
"""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
RUN = ROOT / "iterations/v2/001-original-recovery/runs/221-readonly-scalar-storage"
EXP = ROOT / "local/experiments/v2-readonly-scalars-221"
TARGETS = {0x005B242C: bytes.fromhex("0000c842"), 0x005B24A8: bytes.fromhex("0000803f")}
EXPECTED_SYMBOLS = {"?_DAT_005b242c@@3MA", "?_DAT_005b24a8@@3MA"}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def u16(b: bytes, o: int) -> int:
    return struct.unpack_from("<H", b, o)[0]


def u32(b: bytes, o: int) -> int:
    return struct.unpack_from("<I", b, o)[0]


def coff_object(path: Path) -> dict:
    b = path.read_bytes()
    nsec, symptr, nsym, opt = u16(b, 2), u32(b, 8), u32(b, 12), u16(b, 16)
    sections = []
    for i in range(nsec):
        o = 20 + opt + 40 * i
        name = b[o:o + 8].split(b"\0", 1)[0].decode("ascii")
        sections.append({"name": name, "raw": u32(b, o + 20), "size": u32(b, o + 16),
                         "reloc_ptr": u32(b, o + 24), "reloc_count": u16(b, o + 32),
                         "characteristics": u32(b, o + 36)})
    strtab = symptr + nsym * 18
    strings = b[strtab:] if strtab + 4 <= len(b) else b""
    def sym_name(o: int) -> str:
        raw = b[o:o + 8]
        if raw[:4] == b"\0\0\0\0":
            off = u32(raw, 4)
            return strings[off:].split(b"\0", 1)[0].decode("ascii")
        return raw.split(b"\0", 1)[0].decode("ascii")
    symbols = []
    i = 0
    while i < nsym:
        o = symptr + i * 18
        symbols.append({"name": sym_name(o), "section": struct.unpack_from("<h", b, o + 12)[0],
                        "value": u32(b, o + 8)})
        i += 1 + b[o + 17]
    return {"sha256": sha(path), "sections": sections, "symbols": symbols}


def pe(path: Path) -> dict:
    b = path.read_bytes()
    peoff = u32(b, 0x3C)
    nsec, opt = u16(b, peoff + 6), u16(b, peoff + 20)
    op = peoff + 24
    magic = u16(b, op)
    dd = op + (112 if magic == 0x20B else 96)
    sections = []
    for i in range(nsec):
        o = op + opt + 40 * i
        sections.append({"name": b[o:o + 8].split(b"\0", 1)[0].decode("ascii"),
                         "va": u32(b, o + 12), "vsize": u32(b, o + 8),
                         "raw": u32(b, o + 20), "raw_size": u32(b, o + 16),
                         "chars": u32(b, o + 36)})
    reloc_rva, reloc_size = u32(b, dd + 8 * 5), u32(b, dd + 8 * 5 + 4)
    reloc_file = next(s["raw"] for s in sections if s["name"] == ".reloc")
    reloc_rvas = []
    pos = reloc_file
    end = reloc_file + reloc_size
    while pos + 8 <= end:
        page, block = u32(b, pos), u32(b, pos + 4)
        if block < 8 or pos + block > len(b):
            break
        for q in range(pos + 8, pos + block, 2):
            entry = u16(b, q)
            if entry >> 12:
                reloc_rvas.append(page + (entry & 0xFFF))
        pos += block
    return {"sha256": sha(path), "bytes": b, "sections": sections, "reloc_rvas": reloc_rvas}


def section_bytes(image: dict, va: int) -> tuple[dict, bytes]:
    rva = va - 0x400000
    sec = next(s for s in image["sections"] if s["va"] <= rva < s["va"] + s["vsize"])
    off = sec["raw"] + rva - sec["va"]
    return sec, image["bytes"][off:off + 4]


def main() -> int:
    summary = json.loads((RUN / "summary.json").read_text(encoding="utf-8"))
    proof = json.loads((RUN / "proof-before-compile.json").read_text(encoding="utf-8"))
    validation = json.loads((RUN / "validation.json").read_text(encoding="utf-8"))
    assert sha(RUN / "summary.json") == validation["summary_sha256"]
    # Recheck all repository-relative input pins used by the evidence.
    checked = {}
    for name, expected in summary["input_sha256"].items():
        if ":/" in name or name.startswith("C:/"):
            continue
        path = ROOT / name
        if path.exists():
            checked[name] = sha(path)
            assert checked[name] == expected, (name, checked[name], expected)
    obj = coff_object(EXP / "objects/original_scalars.obj")
    assert {s["name"] for s in obj["symbols"] if s["section"] > 0} >= EXPECTED_SYMBOLS
    orig = next(s for s in obj["sections"] if s["name"] == ".orig$fc")
    assert orig["characteristics"] & 0x80000000 == 0 and orig["characteristics"] & 0x40000000
    assert orig["reloc_count"] == 0
    obj_bytes = (EXP / "objects/original_scalars.obj").read_bytes()[orig["raw"]:orig["raw"] + 8]
    assert obj_bytes == b"\x00\x00\xc8\x42\x00\x00\x80\x3f"
    image = pe(ROOT / "local/game/Porsche.exe")
    original_cells = {}
    for va, expected in TARGETS.items():
        sec, got = section_bytes(image, va)
        assert sec["name"] == ".rdata" and sec["chars"] & 0x80000000 == 0 and sec["chars"] & 0x40000000
        assert got == expected
        assert not any(va - 0x400000 <= r < va - 0x400000 + 4 for r in image["reloc_rvas"])
        original_cells[f"{va:08x}"] = got.hex()
    fixture = pe(EXP / "scalar_fixture.exe")
    fsec = next(s for s in fixture["sections"] if s["name"] == ".orig")
    assert fsec["chars"] & 0x80000000 == 0 and fsec["chars"] & 0x40000000
    foff = fsec["raw"]
    assert fixture["bytes"][foff:foff + 8] == b"\x00\x00\xc8\x42\x00\x00\x80\x3f"
    assert not any(fsec["va"] <= r < fsec["va"] + 8 for r in fixture["reloc_rvas"])
    indexed = proof["indexed_reads"]
    indexed_counts = {k: len(v) for k, v in indexed.items()}
    unindexed = json.loads((EXP / "unindexed-relocation-candidates.json").read_text(encoding="utf-8"))
    rows = unindexed["rows"]
    unindexed_24a8 = sum(1 for row in rows if any("5b24a8" in c.get("assembly", "").lower() for c in row["candidates"]))
    assert indexed_counts == {"005b242c": 55, "005b24a8": 683}
    assert unindexed_24a8 == 26 and len(rows) == 26
    result = {"ok": True, "summary_sha256": sha(RUN / "summary.json"),
              "input_pins_checked": len(checked), "coff_symbols": sorted(EXPECTED_SYMBOLS),
              "original_cells": original_cells, "fixture_section": fsec,
              "fixture_exe_sha256": fixture["sha256"],
              "highlow_reference_counts": {"005b242c": 55, "005b24a8": 709,
                                             "005b24a8_unindexed_overlap_candidates": 26},
              "native_receipt": {"recorded_exit_code": summary["native_fixture"]["exit_code"],
                                  "validation_exit_code": validation["native_fixture_exit"]},
              "scope": "audit only; no allocation or whole-program ownership claim"}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
