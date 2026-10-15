"""Read-only acceptance audit for the bounded Run210 consumer-view capture."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
RUN = ROOT / "iterations/v2/001-original-recovery/runs/210-consumer-views"
OUT = ROOT / "local/experiments/v2-consumer-views-210"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    raise AssertionError(message)


def body(text: str, va: str) -> str:
    marker = f"/* VA {va} */"
    if marker not in text:
        fail(f"missing body marker {va}")
    return text.split(marker, 1)[1]


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(result)
    return result


def main() -> None:
    summary = json.loads((RUN / "summary.json").read_bytes())
    proof = json.loads((RUN / "proof-before-compile.json").read_bytes())
    batch = json.loads((OUT / "batch-exit.json").read_bytes())
    validation = json.loads((RUN / "validation.json").read_bytes())
    assert validation["summary_sha256"] == sha(RUN / "summary.json")
    for path_text, expected in summary["input_sha256"].items():
        path = Path(path_text)
        if not path.is_absolute():
            path = ROOT / path
        assert sha(path) == expected, path_text
    assert summary["original_sha256"] == proof["original_sha256"]
    assert summary["objects_compiled"] == 2
    assert summary["compiler_exit_code"] == 0 and summary["warnings"] == 0
    assert batch["compiler_exit_code"] == 0 and batch["seconds"] == 1.073
    assert batch["log_sha256"] == summary["compiler_log_sha256"]
    log = (ROOT / batch["log"]).read_bytes()
    assert not re.search(rb"\b(?:error|warning) C\d+", log)

    rows = {row["va"]: row for row in summary["results"]}
    assert set(rows) == {"004012b0", "004032d0"}
    coff = module("coff210_audit", ROOT / "scripts/research/build-v2-compile-corpus.py")
    collector = module("collector210_audit", ROOT / "scripts/research/audit-v2-native-union-204.py")
    image = (ROOT / "local/game/Porsche.exe").read_bytes()
    sections = collector.pe_sections(image)
    for va, row in rows.items():
        for path_text, expected in [(row["original_source"], row["original_source_sha256"]),
                                    (row["generated_source"], row["generated_source_sha256"]),
                                    (row["object"], row["object_sha256"])]:
            assert sha(ROOT / path_text) == expected, (va, path_text)
        for path_text, expected in row["dependency_sha256"].items():
            assert sha(ROOT / path_text) == expected, (va, path_text)
        assert coff.coff_symbols(ROOT / row["object"]) == row["symbols"]

    original_012 = (ROOT / rows["004012b0"]["original_source"]).read_text(encoding="utf-8")
    generated_012 = (ROOT / rows["004012b0"]["generated_source"]).read_text(encoding="utf-8")
    assert body(original_012, "004012b0") == body(generated_012, "004012b0")
    header_012 = (OUT / "004012b0-globals.h").read_text(encoding="utf-8")
    exact_179 = {
        "DAT_005e66a4": "extern int DAT_005e66a4;",
        "DAT_005e6688": "extern float DAT_005e6688;",
        "DAT_005e66a8": "extern int DAT_005e66a8;",
        "DAT_005e668c": "extern float DAT_005e668c;",
        "DAT_005e6690": "extern float DAT_005e6690;",
        "DAT_005e6698": "extern uint DAT_005e6698;",
        "DAT_005e6694": "extern int DAT_005e6694;",
    }
    assert all(value in header_012 for value in exact_179.values())
    assert "extern int _DAT_005e66ac;" in header_012
    assert 'static_assert(sizeof(int) == 4, "FILD signed32");' in header_012

    original_032 = (ROOT / rows["004032d0"]["original_source"]).read_text(encoding="utf-8")
    generated_032 = (ROOT / rows["004032d0"]["generated_source"]).read_text(encoding="utf-8")
    assert "(**(code **)*DAT_005e671c)(1);" in original_032
    assert "reinterpret_cast<void (__thiscall *)(void *, uint)>(original_vtable[0])(DAT_005e671c, 1);" in generated_032
    assert "(**(code **)*DAT_005e671c)(1);" not in generated_032
    header_032 = (OUT / "004032d0-globals.h").read_text(encoding="utf-8")
    assert "extern undefined4 *DAT_005e671c;" in header_032
    assert 'static_assert(sizeof(DAT_005e671c) == 4, "original pointer32");' in header_032

    assert sum(len(rows) for rows in proof["instructions"].values()) == 61
    required = {
        "004012cf": "db05ac665e00",
        "004032d0": "8b0d1c675e00",
        "004032da": "8b01",
        "004032dc": "6a01",
        "004032de": "ff10",
        "004032e0": "c7051c675e0000000000",
        "004032ea": "c3",
    }
    by_pc = {row["pc"]: row["bytes"] for rows in proof["instructions"].values() for row in rows}
    for pc, expected in required.items():
        assert by_pc.get(pc) == expected, (pc, by_pc.get(pc))
    for row_list in proof["instructions"].values():
        for instruction in row_list:
            address = int(instruction["pc"], 16)
            raw = bytes.fromhex(instruction["bytes"])
            section = next(s for s in sections if s["va"] <= address < s["va"] + s["raw_bytes"])
            offset = section["raw_offset"] + address - section["va"]
            assert image[offset:offset + len(raw)] == raw, instruction["pc"]
    assert proof["canonical_owners"] == 0 and proof["wip_owners"] == 0

    result = {
        "status": "pass",
        "objects": 2,
        "original_instructions": 61,
        "source_body_unchanged": {"004012b0": True, "004032d0": False},
        "exact_179_externs_004012b0": 7,
        "signed_int4_fild_alias": "_DAT_005e66ac",
        "caller_contract_004032d0": "ECX=self; stack uint32=1; callee cleanup=4; return ignored",
        "batch_exit": 0,
        "batch_seconds": 1.073,
        "boundary": "Candidate only; x87 intermediate rounding/overflow and actual callee fidelity remain open.",
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
