"""Run 430 (branch feat/lowered-whole-game): function symbols of 007 Everything or Nothing PS2.

The user's Alpha 53 prototype (2003-12-11) ships ACTION.ELF with a full ELF symbol table. It links
EA's "real" library prebuilt, so its global functions carry EA's own names (STREAM_*, FILESYS_*,
TIMER_*...), in link order. The ISO is read at run time; only the symbol list is written, to
local/experiments/v2-lowered-exe-430/eon-symbols.json (not committed).

Usage: py -3 scripts/research/eon-ps2-symbols-430.py [--iso PATH]
"""
import argparse
import hashlib
import importlib.util
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ISO = Path(r'C:\Users\mths0\Downloads\PS2 - 007 Everything or Nothing For Preview Only Alpha 53 12-12-2003.iso')
OUT = ROOT / 'local/experiments/v2-lowered-exe-430'
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/430-lowered-whole-game'


def demangle_gcc(name):
    """GCC 2.x names: 'FILEDEV_init__Fii' -> 'FILEDEV_init'; 'Update__9AIState_tFi' -> 'AIState_t::Update'."""
    if '__' not in name or name.startswith('__'):
        return name
    base, rest = name.split('__', 1)
    m = re.match(r'(?:C)?(\d+)([A-Za-z_][A-Za-z0-9_]*)', rest)
    if m and int(m.group(1)) <= len(m.group(2)) and not rest.startswith('F'):
        return f'{m.group(2)[:int(m.group(1))]}::{base}'
    return base


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--iso', type=Path, default=DEFAULT_ISO)
    args = ap.parse_args()
    spec = importlib.util.spec_from_file_location('nfs4', ROOT / 'scripts/research/nfs4-lineage-430.py')
    nfs4 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(nfs4)
    files, read = nfs4.iso_files(args.iso)
    d = read('/ACTION.ELF')
    shoff = struct.unpack_from('<I', d, 0x20)[0]
    es, n, si = struct.unpack_from('<HHH', d, 0x2e)
    secs = [struct.unpack_from('<IIIIIIIIII', d, shoff + i * es) for i in range(n)]
    name = lambda s: d[secs[si][4] + s[0]:d.find(b'\0', secs[si][4] + s[0])].decode()
    named = {name(s): s for s in secs}
    sym, strtab = named['.symtab'], named['.strtab']
    out = []
    for k in range(sym[5] // 16):
        a, value, size, info, other, shndx = struct.unpack_from('<IIIBBH', d, sym[4] + 16 * k)
        if info & 0xf != 2 or not value:
            continue
        raw = d[strtab[4] + a:d.find(b'\0', strtab[4] + a)].decode('latin1')
        out.append(dict(addr=value, size=size, raw=raw, name=demangle_gcc(raw), bind='global' if info >> 4 == 1 else 'local'))
    out.sort(key=lambda e: e['addr'])
    result = dict(schema=1, iso=str(args.iso), action_elf_sha256=hashlib.sha256(d).hexdigest(), functions=out)
    (OUT / 'eon-symbols.json').write_text(json.dumps(result, indent=1), encoding='utf-8')
    print(len(out), 'functions; sha', result['action_elf_sha256'][:16])


if __name__ == '__main__':
    main()
