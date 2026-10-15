"""Read-only audit of the finalized Run212 byte-consumer capture."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
RUN = ROOT / "iterations/v2/001-original-recovery/runs/212-byte-consumers"
OUT = ROOT / "local/experiments/v2-byte-consumers-212"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(result)
    return result


def main() -> None:
    summary = json.loads((RUN / "summary.json").read_bytes())
    proof = json.loads((RUN / "proof-before-compile.json").read_bytes())
    capture = json.loads((OUT / "batch-exit.json").read_bytes())
    validation = json.loads((RUN / "validation.json").read_bytes())
    assert validation["summary_sha256"] == sha(RUN / "summary.json")
    for path_text, expected in summary["input_sha256"].items():
        path = Path(path_text)
        if not path.is_absolute():
            path = ROOT / path
        assert sha(path) == expected, path_text
    assert summary["original_sha256"] == proof["original_sha256"]
    assert summary["objects_compiled"] == 2
    assert summary["compiler_exit_code"] == 0
    assert summary["warnings"] == 1 and summary["warning_codes"] == ["C4146"]
    assert summary["actual_compiler_batches_this_pass"] == 0
    assert capture["compiler_exit_code"] == 0 and capture["seconds"] == 1.437
    assert capture["log_sha256"] == summary["input_sha256"]["local/experiments/v2-byte-consumers-212/compile.log"]
    log = (ROOT / capture["log"]).read_bytes()
    assert not re.search(rb"\berror C\d+", log)
    assert re.findall(rb"\bwarning (C\d+)", log) == [b"C4146"]
    assert sha(OUT / "native-capture-driver.py") == "49189aa136ddd21baebeb663a66d89b9b447515126557cde6ae7e4211c6392ba"

    rows = {row["va"]: row for row in summary["results"]}
    assert set(rows) == {"00537ed0", "00598630"}
    coff = module("coff212_audit", ROOT / "scripts/research/build-v2-compile-corpus.py")
    collector = module("collector212_audit", ROOT / "scripts/research/audit-v2-native-union-204.py")
    image = (ROOT / "local/game/Porsche.exe").read_bytes()
    sections = collector.pe_sections(image)
    expected_symbols = {
        "00537ed0": {
            "defined": ["?FUN_00537ed0@@YAII@Z"],
            "undefined": ["?DAT_005de62c@@3IA", "?FUN_00572f30@@YAHI@Z", "?FUN_00572f5b@@YAHI@Z", "?FUN_00572f90@@YAII@Z", "?FUN_00573000@@YAII@Z"],
        },
        "00598630": {
            "defined": ["?FUN_00598630@@YAXH@Z"],
            "undefined": ["?DAT_006b16a4@@3IA", "?DAT_006b17d0@@3HA"],
        },
    }
    for va, row in rows.items():
        for path_text, expected in [(row["generated_source"], row["generated_source_sha256"]),
                                    (row["object"], row["object_sha256"])]:
            assert sha(ROOT / path_text) == expected, (va, path_text)
        for path_text, expected in row["dependency_sha256"].items():
            assert sha(ROOT / path_text) == expected, (va, path_text)
        symbols = row["symbols"]
        assert coff.coff_symbols(ROOT / row["object"]) == symbols
        assert symbols["defined"] == expected_symbols[va]["defined"]
        assert symbols["undefined"] == expected_symbols[va]["undefined"]

    source_537 = (OUT / "00537ed0.cpp").read_text(encoding="utf-8")
    source_986 = (OUT / "00598630.cpp").read_text(encoding="utf-8")
    original_537 = (ROOT / rows["00537ed0"]["original_source"]).read_text(encoding="utf-8")
    original_986 = (ROOT / rows["00598630"]["original_source"]).read_text(encoding="utf-8")
    before_537 = "DAT_005de62c._1_1_"
    after_537 = "(reinterpret_cast<const unsigned char *>(&DAT_005de62c)[1])"
    before_986 = "DAT_006b16a4._1_1_"
    after_986 = "(reinterpret_cast<const unsigned char *>(&DAT_006b16a4)[1])"
    assert original_537.count(before_537) == 4 and source_537.count(after_537) == 4
    assert original_986.count(before_986) == 1 and source_986.count(after_986) == 1
    assert source_537.replace(after_537, before_537).split("/* VA 00537ed0 */", 1)[1] == original_537.split("/* VA 00537ed0 */", 1)[1]
    assert source_986.replace(after_986, before_986).split("/* VA 00598630 */", 1)[1] == original_986.split("/* VA 00598630 */", 1)[1]

    h537 = (OUT / "00537ed0-globals.h").read_text(encoding="utf-8")
    h986 = (OUT / "00598630-globals.h").read_text(encoding="utf-8")
    assert "extern uint DAT_005de62c;" in h537
    assert "extern uint DAT_006b16a4;" in h986
    assert "extern int DAT_006b17d0;" in h986

    assert sum(len(row["instructions"]) for row in proof["rows"]) == 57
    proof_by_va = {row["va"]: row for row in proof["rows"]}
    assert proof_by_va["00537ed0"]["occurrences"] == 4
    assert proof_by_va["00537ed0"]["read_address"] == "005de62d"
    assert proof_by_va["00598630"]["occurrences"] == 1
    assert proof_by_va["00598630"]["read_address"] == "006b16a5"
    required = {
        "00537ed0": ("00537ed0", "a02de65d00"),
        "00598630": ("00598644", "8a15a5166b00"),
    }
    for row in proof["rows"]:
        by_pc = {item["pc"]: item["bytes"] for item in row["instructions"]}
        pc, raw = required[row["va"]]
        assert by_pc[pc] == raw
        for instruction in row["instructions"]:
            address = int(instruction["pc"], 16)
            encoded = bytes.fromhex(instruction["bytes"])
            section = next(s for s in sections if s["va"] <= address < s["va"] + s["raw_bytes"])
            offset = section["raw_offset"] + address - section["va"]
            assert image[offset:offset + len(encoded)] == encoded, instruction["pc"]
        assert row["all_other_body_bytes_preserved"] is True
        assert "no ownership" in row["boundary"] or "no ownership" in row["boundary"].lower()

    result = {
        "status": "pass",
        "objects": 2,
        "original_instructions": 57,
        "byte_replacements": 5,
        "uint4_views": ["DAT_005de62c", "DAT_006b16a4"],
        "00598630_exact_int4_view": "DAT_006b17d0",
        "batch_exit": 0,
        "batch_seconds": 1.437,
        "warning": "C4146 retained from unchanged unsigned negation; defined modulo-32 arithmetic boundary",
        "boundary": "Candidate/global-alias only; signed overflow, full-body checks, native execution, ABI and lifetimes remain open.",
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
