"""Bounded, read-only audit of app_main's unresolved direct calls (Run 288)."""
import hashlib
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "iterations/v2/001-original-recovery"
OUT = BASE / "runs/288-game-startup-bindings"
PE = ROOT / "local/game/Porsche.exe"
INDEX = ROOT / "research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm"
LINK = BASE / "runs/285-normal-entry-replay/cached-001.json"
REGISTRY = BASE / "source/recovered/functions.json"
FUNCTIONS = ROOT / "research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl"
MAIN = BASE / "source/recovered/Porsche.exe/application_main.cpp"
HEADER = BASE / "source/include/porsche/application_main.hpp"
UNION = BASE / "runs/274-shared-heap-union/summary.json"
UNION_RSP = ROOT / "local/experiments/v2-native-union-274/objects.rsp"
UNION_LIB = ROOT / "local/experiments/v2-native-union-274/porsche_native_union_candidates.lib"
RAW_59EB20 = ROOT / "local/experiments/v2-declaration-compat-184/full/0059eb20.cpp"
SEMANTIC = {
    "application_main_front_end_display": "004b4da0",
    "application_main_game_setup": "004d3420",
    "application_main_network_poll": "0048dcb0",
    "application_main_network_wait": "0048e1a0",
    "application_main_log": "005a177b",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pe_bytes_at_va(data, va, length):
    pe = struct.unpack_from("<I", data, 0x3c)[0]
    assert data[pe:pe + 4] == b"PE\0\0"
    count, opt_size = struct.unpack_from("<HH", data, pe + 6)[0], struct.unpack_from("<H", data, pe + 20)[0]
    image_base = struct.unpack_from("<I", data, pe + 24 + 28)[0]
    rva = va - image_base
    sec = pe + 24 + opt_size
    for i in range(count):
        off = sec + i * 40
        virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from("<IIII", data, off + 8)
        if virtual_address <= rva < virtual_address + max(virtual_size, raw_size):
            delta = rva - virtual_address
            assert delta + length <= raw_size
            return data[raw_offset + delta:raw_offset + delta + length]
    raise AssertionError(f"VA {va:08x} outside raw PE sections")


def main():
    link = json.loads(LINK.read_text(encoding="utf-8"))
    union = json.loads(UNION.read_text(encoding="utf-8"))
    assert sha(UNION_LIB) == union["library"]["sha256"]
    assert sha(UNION_RSP) == union["objects_response"]["sha256"]
    assert all(v not in UNION_RSP.read_text(encoding="utf-8") and v.encode() not in UNION_LIB.read_bytes()
               for v in ("00487e20", "0048ff30", "0059eb20"))
    inputs = (PE, INDEX, FUNCTIONS, LINK, REGISTRY, MAIN, HEADER, UNION, UNION_RSP, UNION_LIB, RAW_59EB20)
    pins_before = {str(p.relative_to(ROOT)): sha(p) for p in inputs}
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))["functions"]
    catalog = {x["entry_va"]: x for x in map(json.loads, FUNCTIONS.read_text(encoding="utf-8").splitlines())}
    pe = PE.read_bytes()
    owners = {x["entry_va"].lower(): x for x in registry if x["module"] == "Porsche.exe"}
    asm = INDEX.read_text(encoding="utf-8")
    block = asm.split("; FUNCTION 004b6a50", 1)[1].split("; FUNCTION ", 1)[0]
    calls = {}
    for pc, target in re.findall(r"(?m)^(004b[0-9a-f]{4})\s+[^\n]*?\bCALL 0x([0-9a-f]{8})", block):
        raw = pe_bytes_at_va(pe, int(pc, 16), 5)
        assert raw[0] == 0xe8 and int(pc, 16) + 5 + struct.unpack_from("<i", raw, 1)[0] == int(target, 16), (pc, target)
        calls.setdefault(target, []).append(pc)
    rows = []
    for item in link["frontier"]:
        if not any("app_main_004b6a50" in (ref["caller"] or "") for ref in item["references"]):
            continue
        symbol = item["symbol"]
        match = re.search(r"application_main_(function_[0-9a-f]{8}|front_end_display|game_setup|network_poll|network_wait|log)", symbol)
        assert match, symbol
        name = "application_main_" + match.group(1)
        va = (match.group(1)[9:] if match.group(1).startswith("function_") else SEMANTIC[name]).lower()
        assert va in calls, (symbol, va)
        assert va not in owners, (symbol, owners[va])
        header = HEADER.read_text(encoding="utf-8")
        position = header.find(name + "(")
        assert position >= 0, name
        declaration = " ".join(header[header.rfind(";", 0, position) + 1:header.find(";", position) + 1].split())
        if "//" in declaration:
            declaration = declaration.rsplit("\n", 1)[-1].strip()
        disposition = "hold_no_accepted_original_body"
        if va == "004d3420":
            disposition = "hold_WIP_candidate_only_effect_contracts_open"
        elif va == "005a177b":
            disposition = "owned_by_parallel_locale_run287_outside_this_packet"
        elif va == "00471b60":
            disposition = "hold_thunk_target_00487e20_unowned"
        elif va == "004a54e0":
            disposition = "hold_thunk_target_0059eb20_unowned"
        elif va == "004a54b0":
            disposition = "hold_partial_callees_0048ff30_unowned_and_global_00628c70"
        rows.append({"name": name, "unresolved_actual_coff_symbol": symbol,
                     "original_target_va": va, "original_call_pc": calls[va],
                     "original_index_body_bytes": catalog[va]["body_bytes"],
                     "canonical_declaration": declaration,
                     "accepted_exact_owner": None, "disposition": disposition})
    assert len(rows) == 20, len(rows)
    assert len({r["original_target_va"] for r in rows}) == 20
    assert sha(PE) == "ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39"
    OUT.mkdir(parents=True, exist_ok=True)
    result = {"schema": 1, "kind": "bounded_game_startup_binding_preflight",
              "input_sha256": pins_before,
              "original_app_main_range": ["004b6a50", "004b6fe5"],
              "actual_link_attempt": "285 cached-001; no new link or compile",
              "unresolved_direct_services": rows,
              "ready_bridge_count": 0,
              "next_bounded_clusters": [
                  {"wrapper": "00471b60", "wrapper_body_bytes": 11, "required_body": "00487e20",
                   "required_body_bytes": 87, "entry_abi": "no stack args; wrapper loads ECX from [00628960] and tail-jumps; callee RET 0",
                   "original_direct_callees": ["004898f0", "00476170", "00423840", "00482e50"],
                   "hold": "object at 00628960, +14/+1c fields and callee effects; no accepted/274 COFF owner"},
                  {"wrapper": "004a54e0", "wrapper_body_bytes": 5, "required_body": "0059eb20",
                   "required_body_bytes": 159, "entry_abi": "no stack args; direct tail JMP; callee RET 0",
                   "original_direct_callees": ["005678f0", "0055ec30", "0059ee30", "005699f0"],
                   "hold": "global 006af3f4 guard, 006af3fc/indexed array, 005e4fec, 005b2148 IAT; raw 184 pseudocode exists only, no accepted/274 COFF owner"},
                  {"wrapper": "004a54b0", "wrapper_body_bytes": 44, "required_body": "0048ff30",
                   "required_body_bytes": 522, "entry_abi": "no stack args; wrapper calls 0048ff30 with ECX=[00628c70]; wrapper RET 0",
                   "original_direct_callees": ["004b7070", "0048ff30", "0059f050"],
                   "hold": "004b7070/0059f050 accepted; 0048ff30 unowned/uncompiled, 00628c70 shared state and 0048ff30 bulk destruction effects"}],
              "limits": ["No original target body among the 20 has accepted exact ownership.",
                         "WIP candidate, probe stubs, and call-site declarations are not game providers.",
                         "No runtime fixture or game startup behavior is claimed."]}
    (OUT / "preflight.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    assert pins_before == {str(p.relative_to(ROOT)): sha(p) for p in inputs}
    validation = {"schema": 1, "preflight_sha256": sha(OUT / "preflight.json"),
                  "input_sha256": pins_before, "input_sha256_unchanged": True,
                  "direct_calls_verified_against_actual_pe": sum(map(len, calls.values())),
                  "actual_274_archive_and_rsp_verified": True,
                  "target_count": len(rows), "accepted_exact_target_owners": 0,
                  "ready_bridge_count": 0, "compiled_or_linked": False}
    (OUT / "validation.json").write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"20 exact direct targets, {len(rows)} unresolved symbols, 0 accepted target owners")


if __name__ == "__main__":
    main()
