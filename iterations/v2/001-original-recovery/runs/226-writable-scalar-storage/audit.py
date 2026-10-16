"""Independent read-only audit of the frozen Run 226 writable scalar packet."""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
RUN = ROOT / "iterations/v2/001-original-recovery/runs/226-writable-scalar-storage"
EXP = ROOT / "local/experiments/v2-writable-scalars-226"
TARGETS = {0x005E25D0: b"\0\0\0\0", 0x005E25D4: b"\0\0\0\0"}
SYMBOLS = {"?DAT_005e25d0@@3HA", "?DAT_005e25d4@@3IA"}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def u16(b: bytes, o: int) -> int:
    return struct.unpack_from("<H", b, o)[0]


def u32(b: bytes, o: int) -> int:
    return struct.unpack_from("<I", b, o)[0]


def coff(path: Path) -> dict:
    b = path.read_bytes()
    machine, nsec, _, symptr, nsym, opt, _ = struct.unpack_from("<HHIIIHH", b, 0)
    assert machine == 0x14C and opt == 0
    sections = []
    for i in range(nsec):
        o = 20 + 40 * i
        sections.append({"name": b[o:o + 8].split(b"\0", 1)[0].decode("ascii"),
                         "raw": u32(b, o + 20), "size": u32(b, o + 16),
                         "reloc_count": u16(b, o + 32), "chars": u32(b, o + 36)})
    string_table = symptr + nsym * 18
    strings = b[string_table:]
    def name(o: int) -> str:
        raw = b[o:o + 8]
        if raw[:4] == b"\0\0\0\0":
            return strings[u32(raw, 4):].split(b"\0", 1)[0].decode("ascii")
        return raw.split(b"\0", 1)[0].decode("ascii")
    symbols = []
    i = 0
    while i < nsym:
        o = symptr + i * 18
        symbols.append({"name": name(o), "value": u32(b, o + 8),
                        "section": struct.unpack_from("<h", b, o + 12)[0]})
        i += 1 + b[o + 17]
    return {"bytes": b, "sha256": digest(path), "sections": sections, "symbols": symbols}


def pe(path: Path) -> dict:
    b = path.read_bytes()
    peoff = u32(b, 0x3C)
    nsec, opt = u16(b, peoff + 6), u16(b, peoff + 20)
    op = peoff + 24
    magic = u16(b, op)
    image_base = u32(b, op + 28)
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
    p = reloc_file
    while p + 8 <= reloc_file + reloc_size:
        page, size = u32(b, p), u32(b, p + 4)
        if size < 8:
            break
        for q in range(p + 8, p + size, 2):
            entry = u16(b, q)
            if entry >> 12 == 3:
                reloc_rvas.append(page + (entry & 0xFFF))
        p += size
    return {"bytes": b, "sha256": digest(path), "image_base": image_base,
            "sections": sections, "reloc_rvas": reloc_rvas}


def cell(image: dict, va: int) -> tuple[dict, bytes]:
    rva = va - image["image_base"]
    sec = next(s for s in image["sections"] if s["va"] <= rva < s["va"] + s["vsize"])
    off = sec["raw"] + rva - sec["va"]
    return sec, image["bytes"][off:off + 4]


def main() -> int:
    summary = json.loads((RUN / "summary.json").read_text(encoding="utf8"))
    proof = json.loads((RUN / "proof-before-compile.json").read_text(encoding="utf8"))
    validation = json.loads((RUN / "validation.json").read_text(encoding="utf8"))
    assert digest(RUN / "summary.json") == validation["summary_sha256"]
    checked = {}
    for name, expected in summary["input_sha256"].items():
        if name.startswith("C:/"):
            continue
        path = ROOT / name
        if path.exists():
            checked[name] = digest(path)
            assert checked[name] == expected, (name, checked[name], expected)
    obj = coff(EXP / "objects/original_scalars.obj")
    assert {s["name"] for s in obj["symbols"] if s["section"] > 0} >= SYMBOLS
    actual_offsets = {s["name"]: s["value"] for s in obj["symbols"] if s["name"] in SYMBOLS}
    assert actual_offsets == {"?DAT_005e25d0@@3HA": 0, "?DAT_005e25d4@@3IA": 4}
    sec = next(s for s in obj["sections"] if s["name"] == ".ogw$sc")
    assert sec["chars"] & 0x40000000 and sec["chars"] & 0x80000000 and not sec["chars"] & 0x20000000
    assert sec["reloc_count"] == 0
    assert obj["bytes"][sec["raw"]:sec["raw"] + 8] == b"\0" * 8
    original = pe(ROOT / "local/game/Porsche.exe")
    original_cells = {}
    for va, expected in TARGETS.items():
        section, got = cell(original, va)
        assert section["name"] == ".data" and section["chars"] & 0x40000000 and section["chars"] & 0x80000000
        assert not section["chars"] & 0x20000000 and got == expected
        assert not any(va - original["image_base"] <= r < va - original["image_base"] + 4 for r in original["reloc_rvas"])
        original_cells[f"{va:08x}"] = got.hex()
    fixture = pe(EXP / "scalar_fixture.exe")
    fsec = next(s for s in fixture["sections"] if s["name"] == ".ogw")
    assert fsec["chars"] & 0x40000000 and fsec["chars"] & 0x80000000 and not fsec["chars"] & 0x20000000
    assert fixture["bytes"][fsec["raw"]:fsec["raw"] + 8] == b"\0" * 8
    assert not any(fsec["va"] <= r < fsec["va"] + 8 for r in fixture["reloc_rvas"])
    disassembly = (ROOT / "research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm").read_text(encoding="utf8").splitlines()
    actual_refs = {}
    for va, entries in proof["original_memory_instructions"].items():
        assert len(entries) in (12, 3)
        for entry in entries:
            assert entry["width"] == 4 and (entry["read"] ^ entry["write"])
            assert f"{entry['pc']}  {entry['bytes']}  {entry['assembly']}" in "\n".join(disassembly)
        actual_refs[va] = {"count": len(entries), "reads": sum(e["read"] for e in entries),
                           "writes": sum(e["write"] for e in entries)}
    assert actual_refs == {"005e25d0": {"count": 12, "reads": 4, "writes": 8},
                           "005e25d4": {"count": 3, "reads": 1, "writes": 2}}
    assert proof["complete_HIGHLOW_sites"] == {"005e25d0": ["00592620", "005926ae", "005926db", "005926ff", "0059278d", "005927ad", "005927db", "0059288d", "0059289d", "0059292e", "005929b3", "005929bd"], "005e25d4": ["00592948", "00592954", "00592967"]}
    assert proof["in_cell_relocations"] == 0 and proof["relative_separation"] == 4
    assert summary["native_fixture"]["exit_code"] == 0 and validation["native_fixture_exit"] == 0
    print(json.dumps({"ok": True, "input_pins_checked": len(checked), "coff_symbols": sorted(SYMBOLS),
                      "coff_section": sec, "original_cells": original_cells, "original_refs": actual_refs,
                      "fixture_section": fsec, "fixture_sha256": fixture["sha256"],
                      "native_receipts": {"summary": summary["native_fixture"]["exit_code"], "validation": validation["native_fixture_exit"]},
                      "scope": "current views only; computed-pointer, whole-data, alias and production ownership deferred"}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
