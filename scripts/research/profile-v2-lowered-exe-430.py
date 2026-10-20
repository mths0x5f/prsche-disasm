"""Run 430: symbolize a PORSCHE430_PROFILE dump with the linker map of PorscheLowered.exe.

Usage: py -3 scripts/research/profile-v2-lowered-exe-430.py <profile.txt> [top]
"""
import bisect
import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAP = ROOT / 'local/experiments/v2-lowered-exe-430/PorscheLowered.map'
SYMBOL = re.compile(r'^\s*\d{4}:[0-9a-f]{8}\s+(\S+)\s+([0-9a-f]{8})\s+f?\s*(?:i\s+)?(\S+)', re.I)


def main():
    profile = Path(sys.argv[1])
    top = int(sys.argv[2]) if len(sys.argv) > 2 else 25
    syms = []
    for line in MAP.read_text(encoding='utf-8', errors='replace').splitlines():
        m = SYMBOL.match(line)
        if m:
            syms.append((int(m.group(2), 16), m.group(1), m.group(3)))
    syms.sort()
    starts = [a for a, _, _ in syms]
    funcs, objs, modules = collections.Counter(), collections.Counter(), collections.Counter()
    reverse = collections.Counter()
    total = 0
    for line in profile.read_text(encoding='utf-8').splitlines():
        kind, *rest = line.split()
        if kind == 'total':
            total = int(rest[0])
        elif kind == 'host':
            addr, n = int(rest[0], 16), int(rest[1])
            k = bisect.bisect_right(starts, addr) - 1
            name, obj = (syms[k][1], syms[k][2]) if k >= 0 else ('?', '?')
            m = re.match(r'\?translated_([0-9a-f]{8})@', name)
            funcs['lowered ' + m.group(1) if m else name] += n
            objs['lowered' if obj.startswith('lowered_') else obj] += n
        elif kind == 'reverse':
            reverse[rest[0]] += int(rest[1])
        elif kind == 'native':
            modules[rest[0]] += 1
            objs['native'] += 1
    print(f'samples {total}')
    print('-- by origin')
    for name, n in objs.most_common(12):
        print(f'{100 * n / total:5.1f}% {name}')
    print('-- native modules')
    for name, n in modules.most_common(8):
        print(f'{100 * n / total:5.1f}% {name}')
    print('-- reverse entries (native -> lowered) in the window')
    for va, n in reverse.most_common(10):
        print(f'{n:8d} {va}')
    print('-- functions')
    for name, n in funcs.most_common(top):
        print(f'{100 * n / total:5.1f}% {name}')


if __name__ == '__main__':
    main()
