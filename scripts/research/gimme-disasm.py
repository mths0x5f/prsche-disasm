"""Disassembles gimme.dll functions with string and call annotations (Run 432).

usage: python gimme-disasm.py [--dll PATH] <va> [<va> ...]     one function per VA (Ghidra ranges)
       python gimme-disasm.py [--dll PATH] --range <start> <end>  raw linear range
       python gimme-disasm.py --callers <va>                      direct callers from the index

Function boundaries, strings and call edges come from the versioned Ghidra index
research/binary-index/ghidra/gimme.dll-3a43b0f6a160; bytes come from the original DLL
(default: <main checkout>/local/game/gimme.dll, SHA-256 checked).  Incremental-link thunks
(jmp rel32 below 0x10001400) are resolved to their targets.  Navigation only, not proof.
"""
import argparse
import hashlib
import json
import os
import re
import struct
import sys

import capstone

SHA256 = "3a43b0f6a1608f69adc3a5009c9fe055a24e17197e85c4045c2c43e37eb75f6b"
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INDEX = os.path.join(REPO, "research", "binary-index", "ghidra", "gimme.dll-3a43b0f6a160")


def default_dll():
    candidates = [os.path.join(REPO, "local", "game", "gimme.dll")]
    # Worktrees under <main>/.claude/worktrees/<name> share the main checkout's local/.
    parts = REPO.replace("\\", "/").split("/.claude/worktrees/")
    if len(parts) == 2:
        candidates.append(os.path.join(parts[0], "local", "game", "gimme.dll"))
    for path in candidates:
        if os.path.exists(path):
            return path
    return candidates[0]


class Image:
    def __init__(self, path):
        self.data = open(path, "rb").read()
        if hashlib.sha256(self.data).hexdigest() != SHA256:
            sys.exit("unexpected gimme.dll SHA-256: " + path)
        pe = struct.unpack_from("<I", self.data, 0x3C)[0]
        count = struct.unpack_from("<H", self.data, pe + 6)[0]
        optional = struct.unpack_from("<H", self.data, pe + 20)[0]
        self.sections = []
        for i in range(count):
            o = pe + 24 + optional + 40 * i
            vsize, rva, rsize, roff = struct.unpack_from("<IIII", self.data, o + 8)
            # Only the raw part has file bytes; the rest of vsize is zero-filled (BSS).
            self.sections.append((rva, rsize, roff))

    def offset(self, va):
        rva = va - 0x10000000
        for start, size, raw in self.sections:
            if start <= rva < start + size:
                return raw + rva - start
        return None


def load_index():
    functions, strings, callers = {}, {}, {}
    for line in open(os.path.join(INDEX, "functions.jsonl")):
        f = json.loads(line)
        functions[int(f["entry_va"], 16)] = f
    for line in open(os.path.join(INDEX, "strings.jsonl")):
        s = json.loads(line)
        strings[int(s["va"], 16)] = s["value"]
    return functions, strings


def thunk_target(image, va):
    o = image.offset(va)
    if o is not None and va < 0x10001400 and image.data[o] == 0xE9:
        return va + 5 + struct.unpack_from("<i", image.data, o + 1)[0]
    return va


def show(image, functions, strings, start, end):
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    o = image.offset(start)
    for insn in md.disasm(image.data[o:o + end - start], start):
        note = ""
        for token in re.findall(r"0x[0-9a-f]{6,8}", insn.op_str):
            value = int(token, 16)
            if value in strings:
                note += ' ; "%s"' % strings[value][:60].replace("\n", "\\n")
            elif insn.mnemonic == "call":
                target = thunk_target(image, value)
                note += " ; " + (functions[target]["name"] if target in functions else hex(target))
        print("%08x  %-8s %s%s" % (insn.address, insn.mnemonic, insn.op_str, note))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dll", default=None)
    parser.add_argument("--range", nargs=2, metavar=("START", "END"))
    parser.add_argument("--callers", metavar="VA")
    parser.add_argument("va", nargs="*")
    args = parser.parse_args()
    if args.callers:
        wanted = "%08x" % int(args.callers, 16)
        for line in open(os.path.join(INDEX, "calls.jsonl")):
            c = json.loads(line)
            if c.get("to_va") == wanted or c.get("to_function") == wanted:
                print(c["from_va"], c.get("from_function"))
        return
    image = Image(args.dll or default_dll())
    functions, strings = load_index()
    if args.range:
        show(image, functions, strings, int(args.range[0], 16), int(args.range[1], 16))
        return
    for text in args.va:
        va = int(text, 16)
        f = functions.get(va)
        if not f:
            print("no function at %08x" % va)
            continue
        print("; %s %s, %d bytes" % (f["entry_va"], f["name"], f["body_bytes"]))
        for a, b in f["ranges"]:
            show(image, functions, strings, int(a, 16), int(b, 16) + 1)
        print()


if __name__ == "__main__":
    main()
