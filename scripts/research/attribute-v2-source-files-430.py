"""Run 430 (branch feat/lowered-whole-game): attribute functions to the game's original source files.

Evidence levels, from strongest:
- path:     the function references a __FILE__-style string (e.g. "\\real\\pc\\startup.c");
- between:  the function lies in .text between two `path` functions of the same file with no
            function of another file in between (MSVC links one object's code contiguously);
- class:    RTTI names the class (vtable method, constructor writing the vtable, scalar
            deleting destructor); the file stays unknown unless `path`/`between` gives it.
Everything else stays unattributed. Writes local/experiments/v2-lowered-exe-430/attribution.json
and a summary to the run folder.

Usage: py -3 scripts/research/attribute-v2-source-files-430.py
"""
import bisect
import collections
import hashlib
import json
import re
import struct
from pathlib import Path

import capstone

ROOT = Path(__file__).resolve().parents[2]
PE_PATH = ROOT / 'local/game/Porsche.exe'
PE_SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
OUT = ROOT / 'local/experiments/v2-lowered-exe-430'
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/430-lowered-whole-game'
PATH_RE = re.compile(r'[A-Za-z0-9_:.\\/-]*\\[A-Za-z0-9_.\\/-]+\.(?:c|cpp|h|asm)$')


class Image:
    def __init__(self, data):
        pe = struct.unpack_from('<I', data, 0x3c)[0]
        self.base = struct.unpack_from('<I', data, pe + 52)[0]
        sh = pe + 24 + struct.unpack_from('<H', data, pe + 20)[0]
        self.sections = []
        for i in range(struct.unpack_from('<H', data, pe + 6)[0]):
            q = sh + 40 * i
            vs, va, rs, raw = struct.unpack_from('<IIII', data, q + 8)
            self.sections.append((data[q:q + 8].rstrip(b'\0').decode(), self.base + va, vs, rs, raw))
        self.data = data

    def off(self, va):
        for _, sva, vs, rs, raw in self.sections:
            if sva <= va < sva + rs:
                return raw + va - sva
        return None

    def dword(self, va):
        o = self.off(va)
        return struct.unpack_from('<I', self.data, o)[0] if o is not None else None

    def va_of(self, o):
        for _, sva, vs, rs, raw in self.sections:
            if raw <= o < raw + rs:
                return sva + o - raw
        return None


def normalize(path):
    # Strings are sometimes preceded by a stray byte that is part of other data ("3\real\pc").
    p = path.replace('/', '\\')
    for root in ('\\real\\', 'd:\\Nfs\\', '..\\..\\library\\'):
        k = p.lower().find(root.lower())
        if k > 0:
            p = p[k:]
    return p


def source_strings(img):
    found = {}
    for m in re.finditer(rb'[ -~]{4,160}\x00', img.data):
        s = m.group()[:-1].decode()
        if PATH_RE.search(s) and '\\' in s:
            va = img.va_of(m.start())
            if va is not None:
                found[va] = normalize(PATH_RE.search(s).group())
    return found


def rtti(img):
    names = {}
    for m in re.finditer(rb'\.\?A[VU][A-Za-z0-9_@?$]+@@\x00', img.data):
        va = img.va_of(m.start() - 8)
        if va is not None:
            names[va] = m.group()[:-1].decode()
    cols = {}
    for _, sva, vs, rs, raw in img.sections:
        for o in range(raw, raw + rs - 20, 4):
            sig, offv, cd, ptd, pch = struct.unpack_from('<IIIII', img.data, o)
            if sig == 0 and ptd in names and img.off(pch) is not None:
                # Class Hierarchy Descriptor: signature, attributes, numBaseClasses, pBaseClassArray;
                # each Base Class Descriptor starts with its TypeDescriptor.
                bases = []
                n_bases, array = img.dword(pch + 8), img.dword(pch + 12)
                if n_bases is not None and array is not None and n_bases < 64:
                    for k in range(n_bases):
                        bcd = img.dword(array + 4 * k)
                        td = img.dword(bcd) if bcd is not None else None
                        if td in names:
                            bases.append(names[td])
                cols[sva + o - raw] = (names[ptd], offv, bases)
    return cols


def demangle(name):
    # ".?AVAIState_Chase@@" -> "AIState_Chase"; ".?AVControl@FERT@@" -> "FERT::Control".
    body = name[4:-2]
    if '?$' in body:
        return re.sub(r'[^A-Za-z0-9_]', '_', body)[:60]
    return '::'.join(reversed(body.split('@')))


SIMPLE_TYPES = {'C': 4, 'D': 4, 'E': 4, 'F': 4, 'G': 4, 'H': 4, 'I': 4, 'J': 4, 'K': 4, 'M': 4, 'N': 8, 'O': 8}


def stack_arg_bytes(sym):
    """Bytes a __thiscall/__stdcall MSVC function pops, from its decorated name, or None.

    Handles the parameter forms seen in this game's names: builtin scalars, pointers and
    references (P/Q/A + cv + pointee), back-references (0-9) and _N (bool). By-value class or
    struct parameters (size unknown) give None.
    """
    m = re.match(r'\?[A-Za-z_][A-Za-z0-9_]*@(?:[A-Za-z_][A-Za-z0-9_]*@)+@([QUAIEMS])([AB]?)E(.*)$', sym)
    if not m:
        return None
    s = m.group(3)
    seen, total, at, first = [], 0, 0, True

    def skip_name(k):
        end = s.find('@@', k)
        return -1 if end < 0 else end + 2

    def one(k):
        """Returns (size or None, next index)."""
        c = s[k]
        if c.isdigit():
            idx = int(c)
            return (seen[idx] if idx < len(seen) else None), k + 1
        if c in SIMPLE_TYPES:
            return SIMPLE_TYPES[c], k + 1
        if s.startswith('_N', k) or s.startswith('_J', k) or s.startswith('_K', k):
            return (4 if s[k + 1] == 'N' else 8), k + 2
        if c in 'PQA' and k + 1 < len(s):
            j = k + 2  # cv qualifier
            if s[j] in 'VUT':
                j = skip_name(j + 1)
                return (4 if j > 0 else None), j
            size, j = one(j)
            return 4, j
        if c in 'VUT':
            return None, skip_name(k + 1)
        if c == 'X':
            return 0, k + 1
        return None, k + 1

    # Return type first ('?A' marks a by-value class return: hidden pointer argument).
    if s.startswith('?A'):
        size, at = one(2)
        total += 4
    else:
        size, at = one(0)
    if at < 0:
        return None
    while at < len(s) and s[at] not in '@Z':
        if s[at] == 'X' and first:
            at += 1
            break
        size, nxt = one(at)
        if size is None or nxt < 0:
            return None
        if nxt - at > 1:
            seen.append(size)
        total += size
        at, first = nxt, False
    return total


def ret_bytes(img, md, va, size):
    o = img.off(va)
    rets = set()
    for ins in md.disasm(img.data[o:o + size], va):
        if ins.mnemonic == 'ret':
            rets.add(int(ins.op_str, 16) if ins.op_str else 0)
    return rets


def main():
    data = PE_PATH.read_bytes()
    assert hashlib.sha256(data).hexdigest() == PE_SHA
    img = Image(data)
    funcs = []
    for line in (ROOT / 'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text().splitlines():
        e = json.loads(line)
        funcs.append((int(e['ranges'][0][0], 16), int(e['ranges'][-1][1], 16) + 1, e['entry_va']))
    funcs.sort()
    starts = [a for a, _, _ in funcs]
    strings = source_strings(img)
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)

    def refs(lo, hi):
        o = img.off(lo)
        body = img.data[o:o + hi - lo]
        out = set()
        for k in range(len(body) - 3):
            v = struct.unpack_from('<I', body, k)[0]
            if v in strings:
                out.add(strings[v])
        return out

    by_func = {}
    for lo, hi, va in funcs:
        # A header path only shows inlined code, not the file the function lives in.
        r = {p for p in refs(lo, hi) if not p.lower().endswith('.h')}
        if len(r) == 1:
            by_func[va] = dict(file=r.pop(), evidence='path')
        elif len(r) > 1:
            by_func[va] = dict(file=sorted(r)[0], evidence='path-ambiguous', candidates=sorted(r))

    # between: walk .text order; fill gaps between two anchors of the same file.
    order = [va for _, _, va in funcs]
    last_file, last_idx = None, None
    for i, va in enumerate(order):
        a = by_func.get(va)
        if not a or a['evidence'] != 'path':
            continue
        if last_file == a['file'] and last_idx is not None:
            gap = order[last_idx + 1:i]
            if all(g not in by_func for g in gap):
                for g in gap:
                    by_func[g] = dict(file=a['file'], evidence='between')
        last_file, last_idx = a['file'], i

    # class: vtable methods, constructors (store the vtable), destructors.
    cols = rtti(img)
    classes = collections.defaultdict(lambda: dict(vtables=[], methods={}, primary={}, bases=[], ctors=set()))
    vt_of = {}
    for _, sva, vs, rs, raw in img.sections:
        if _ not in ('.rdata', '.data'):
            continue
        for o in range(raw, raw + rs - 8, 4):
            v = struct.unpack_from('<I', img.data, o)[0]
            if v in cols:
                vt = sva + o - raw + 4
                cls = demangle(cols[v][0])
                k = 0
                while True:
                    f = img.dword(vt + 4 * k)
                    if f is None or not any(lo <= f < hi for _, lo, vsz, _, _ in img.sections[:2]
                                            for hi in [lo + vsz]):
                        break
                    if k and (vt + 4 * k) in vt_of:
                        break
                    classes[cls]['methods'].setdefault(f, []).append(k)
                    if cols[v][1] == 0:
                        classes[cls]['primary'][k] = f
                    k += 1
                classes[cls]['vtables'].append(vt)
                classes[cls]['bases'] = [demangle(b) for b in cols[v][2]]
                vt_of[vt] = cls
    names = {}
    for lo, hi, va in funcs:
        o = img.off(lo)
        for ins in md.disasm(img.data[o:o + hi - lo], lo):
            if ins.mnemonic == 'mov' and ins.op_str.startswith('dword ptr [') and ins.op_str.split(', ')[-1].startswith('0x'):
                imm = int(ins.op_str.split(', ')[-1], 16)
                if imm in vt_of:
                    classes[vt_of[imm]]['ctors'].add(va)
    for cls, info in classes.items():
        for f, slots in info['methods'].items():
            va = f'{f:08x}'
            names.setdefault(va, []).append(f'{cls}::virtual_{slots[0]:02d}')
        for va in info['ctors']:
            names.setdefault(va, []).append(f'{cls}::ctor_or_dtor')
    # gimme.dll evidence (extract-v2-gimme-debug-430.py): real names from byte matches and from
    # embedded vtables (slot k of class C), and real .cpp paths.
    gimme_path = OUT / 'gimme-evidence.json'
    gimme = json.loads(gimme_path.read_text(encoding='utf-8')) if gimme_path.exists() else {}
    real = collections.defaultdict(set)
    real_evidence = {}
    for m in gimme.get('matches', []):
        real[m['va']].add(m['name'])
        real_evidence[m['va']] = 'gimme-bytes'
        cpp = [f for f in m.get('files', []) if f.lower().endswith(('.c', '.cpp'))]
        if cpp:
            entry = by_func.setdefault(m['va'], dict(file=None, evidence='gimme-bytes'))
            if entry['file'] is None:
                entry['file'], entry['evidence'] = normalize(cpp[0]), 'gimme-bytes'
    # Vtable slots: slot k of class C names the function in slot k of C's vtable in Porsche.exe.
    # An inherited entry (Base::Method in C's vtable) keeps its slot in Base's own vtable, so it
    # names Base's slot k. Each name is checked: the bytes the decorated name says a __thiscall
    # method pops must equal every `ret N` of the Porsche.exe function.
    sizes = {va: hi - lo for lo, hi, va in funcs}
    vtable_checks = collections.Counter()
    for obj in gimme.get('objects', []):
        for vt in obj.get('vtables', []):
            for k_text, slot in vt['slots'].items():
                k, name, sym = int(k_text), slot['name'], slot['symbol']
                owner, method = name.rsplit('::', 1)
                if method.endswith('_dtor') or method == 'ctor':
                    owner = vt['cls']  # destructors are per class, never inherited by name
                    family = [owner] if owner in classes else []
                else:
                    # Every Porsche.exe class that is `owner` or derives from it has its own
                    # implementation of `method` in slot k of its primary vtable.
                    family = [c for c, info in classes.items() if c == owner or owner in info['bases']]
                if not family:
                    vtable_checks['class absent from Porsche.exe'] += 1
                    continue
                users = collections.defaultdict(list)
                for c in family:
                    f = classes[c]['primary'].get(k)
                    if f is not None:
                        users[f].append(c)
                expected = stack_arg_bytes(sym)
                for f, cs in users.items():
                    va = f'{f:08x}'
                    rets = ret_bytes(img, md, f, sizes.get(va, 0)) if va in sizes else set()
                    if expected is None or rets != {expected}:
                        vtable_checks['ret check failed or unknown'] += 1
                        continue
                    top = min(cs, key=lambda c: (len(classes[c]['bases']), c))
                    vtable_checks['named'] += 1
                    real[va].add(f'{top}::{method}')
                    real_evidence.setdefault(va, 'gimme-vtable')

    # class-file: EA's C++ code names files after the class or namespace (RCustomLayers.cpp
    # holds RCustomLayers::*, FEIntro.cpp holds FEIntro). A class whose outermost name equals a
    # known source file's base name is placed in that file.
    stems = collections.defaultdict(set)
    for p in set(strings.values()) | {normalize(p) for p in gimme.get('paths', [])}:
        if not p.lower().endswith(('.h', '.hpp', '.inl')):
            stems[re.split(r'[\\/]', p)[-1].rsplit('.', 1)[0].lower()].add(p)
    for va, ns in real.items():
        entry = by_func.setdefault(va, dict(file=None, evidence=real_evidence[va]))
        entry['real_names'] = sorted(ns)
        entry['name_evidence'] = real_evidence[va]
        outer = {n.split('::')[0].lower() for n in ns}
        hits = {p for o in outer for p in stems.get(o, ())}
        if entry['file'] is None and len(outer) == 1 and len(hits) == 1:
            entry['file'], entry['evidence'] = hits.pop(), 'class-file'
    for va, ns in names.items():
        entry = by_func.setdefault(va, dict(file=None, evidence='class'))
        entry['names'] = sorted(set(ns))
        if entry['file'] is None:
            # Identical-code folding puts one body (e.g. `xor eax,eax; ret`) in many classes'
            # vtables; only a body whose names all share one outer class/namespace counts.
            outer = {n.split('::')[0].lower() for n in entry['names']}
            hits = {p for o in outer for p in stems.get(o, ())}
            if len(outer) == 1 and len(hits) == 1:
                entry['file'], entry['evidence'] = hits.pop(), 'class-file'

    counts = collections.Counter(v['evidence'] for v in by_func.values())
    files = collections.Counter(v['file'] for v in by_func.values() if v.get('file'))
    result = dict(schema=1, original_sha256=PE_SHA, gimme_vtable_checks=dict(vtable_checks),
                  real_names=len(real), functions=len(funcs), source_paths=len(set(strings.values())),
                  evidence=dict(counts), named_by_rtti=len(names), classes=len(classes),
                  files={k: n for k, n in sorted(files.items())})
    (OUT / 'attribution.json').write_text(json.dumps(dict(result, by_function=by_func), indent=1), encoding='utf-8')
    (RUN / 'attribution-summary.json').write_text(json.dumps(result, indent=1) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'files'}, indent=1))
    for f, n in files.most_common():
        print(f'{n:4d} {f}')


if __name__ == '__main__':
    main()
