"""Run 430: picks the next functions to humanize and writes their disassembly in chunks.

Candidates: catalog functions not yet humanized, one contiguous range, no thunk, no indirect
call or jump (vtables, imports, switch tables), smallest first. Each chunk file lists, per
function, its name from the catalog, size, direct callees (with their RET size, so the callee's
convention is known) and the disassembly with string literals the code references.

Usage: py -3 scripts/research/humanize-candidates-430.py --count 2000 --chunk 200 --out DIR
"""
import argparse
import importlib.util
import json
from pathlib import Path

import capstone

ROOT = Path(__file__).resolve().parents[2]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--count', type=int, default=2000)
    ap.add_argument('--chunk', type=int, default=200)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    spec = importlib.util.spec_from_file_location('b', ROOT / 'scripts/research/build-v2-lowered-exe-430.py')
    b = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(b)
    data = b.PE_PATH.read_bytes()
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    funcs = {}
    for line in b.CATALOG.read_text(encoding='utf-8').splitlines():
        f = json.loads(line)
        funcs[f['entry_va']] = f

    def code(f):
        lo, hi = (int(x, 16) for x in f['ranges'][0])
        return lo, list(md.disasm(data[lo - 0x400000:hi - 0x400000 + 1], lo))

    def ret_pop(va):
        f = funcs.get(f'{va:08x}')
        if not f or len(f['ranges']) != 1:
            return '?'
        for i in code(f)[1]:
            if i.mnemonic == 'ret':
                return i.op_str or '0'
        return '?'

    def string_at(va):
        o = va - 0x400000
        if not (0 < o < len(data)):
            return None
        end = data.find(b'\0', o, o + 80)
        s = data[o:end] if end > o else b''
        if len(s) >= 3 and all(32 <= c < 127 for c in s):
            return s.decode()
        return None

    picked = []
    for va, f in funcs.items():
        if va in b.HUMANIZED or f.get('thunk') or len(f['ranges']) != 1:
            continue
        lo, ins = code(f)
        if not ins:
            continue
        bad = False
        for i in ins:
            if i.mnemonic in ('call', 'jmp') and not i.op_str.startswith('0x'):
                bad = True
            if i.mnemonic.startswith('j') and i.op_str.startswith('0x'):
                t = int(i.op_str, 16)
                lo_, hi_ = (int(x, 16) for x in f['ranges'][0])
                if not lo_ <= t <= hi_ and i.mnemonic != 'jmp':
                    bad = True
        if bad:
            continue
        picked.append((sum(i.size for i in ins), va, f, ins))
    picked.sort(key=lambda t: (t[0], t[1]))
    picked = picked[:args.count]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for c in range(0, len(picked), args.chunk):
        lines = []
        for n, va, f, ins in picked[c:c + args.chunk]:
            callees = sorted({int(i.op_str, 16) for i in ins if i.mnemonic == 'call'})
            lines.append(f'== {va} {f.get("name")} size {n} recovery={f.get("recovery_status")}')
            for t in callees:
                lines.append(f'   callee {t:08x} {funcs.get(f"{t:08x}", {}).get("name")} ret {ret_pop(t)}')
            for i in ins:
                note = ''
                for tok in i.op_str.replace('[', ' ').replace(']', ' ').replace(',', ' ').split():
                    if tok.startswith('0x') and len(tok) >= 7:
                        s = string_at(int(tok, 16))
                        if s:
                            note = f'    ; "{s}"'
                lines.append(f'   {i.address:08x} {i.mnemonic} {i.op_str}{note}')
        (out / f'chunk{c // args.chunk:02d}.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'{len(picked)} functions in {(len(picked) + args.chunk - 1) // args.chunk} chunks; sizes {picked[0][0]}..{picked[-1][0]}')


if __name__ == '__main__':
    main()
