"""Run 430 (branch feat/lowered-whole-game): transfer evidence from the NFS4 (High Stakes) PS1 prototype.

The prototype disc (user's "Need For Speed 4 v9.0.iso") ships NFS4.EXE with the linker map NFS4.MAP and
the Psy-Q symbol file NFS4.SYM. NFS4 PS1 (EA Canada) is the code base Porsche Unleashed PC (EA Canada)
evolved from. MIPS and x86 never match byte for byte, so names move to Porsche.exe only through indirect,
checkable evidence, each kept at its own level:

- nfs4-strings: a string literal used by exactly one NFS4 function and by exactly one Porsche.exe function
  pairs the two; a pair is accepted when every unique shared string agrees on it.
- nfs4-data:    an initialised NFS4 global whose exact bytes (>= 16, not trivial) occur exactly once in
  Porsche.exe's data names that address.
- nfs4-heranca: an RTTI class whose name matches an NFS4 source file by the abbreviation rule
  (AIHigh_Human -> AIH_HUM.CPP: same token count, each file token a prefix of the class token). This is
  an inference about the file name only; the directory stays unknown.

The disc contents are read from the ISO at run time and never written to the repository; the output
goes to local/experiments/v2-lowered-exe-430/nfs4-evidence.json, with a summary in the run folder.

Usage: py -3 scripts/research/nfs4-lineage-430.py [--iso PATH]
"""
import argparse
import collections
import hashlib
import json
import re
import struct
from pathlib import Path

import capstone

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ISO = Path(r'D:\projetos\Need For Speed 4 v9.0\Need For Speed 4 v9.0.iso')
PE_PATH = ROOT / 'local/game/Porsche.exe'
PE_SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
OUT = ROOT / 'local/experiments/v2-lowered-exe-430'
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/430-lowered-whole-game'


# ---- ISO 9660 (2048-byte sectors) ----------------------------------------------------------
def iso_files(path):
    f = open(path, 'rb')

    def sector(n, count=1):
        f.seek(n * 2048)
        return f.read(2048 * count)

    out = {}

    def walk(rec, prefix):
        lba, size = struct.unpack_from('<I', rec, 2)[0], struct.unpack_from('<I', rec, 10)[0]
        data = sector(lba, (size + 2047) // 2048)[:size]
        at = 0
        while at < len(data):
            n = data[at]
            if n == 0:
                at = (at // 2048 + 1) * 2048
                continue
            r = data[at:at + n]
            name = r[33:33 + r[32]]
            if name not in (b'\0', b'\1'):
                full = prefix + '/' + name.decode('latin1').split(';')[0]
                clba, csize = struct.unpack_from('<I', r, 2)[0], struct.unpack_from('<I', r, 10)[0]
                if r[25] & 2:
                    walk(r, full)
                else:
                    out[full.upper()] = (clba, csize)
            at += n

    walk(sector(16)[156:190], '')
    return out, lambda name: sector(out[name][0], (out[name][1] + 2047) // 2048)[:out[name][1]]


# ---- Psy-Q SYM ---------------------------------------------------------------------------------
def pascal(b, at):
    return b[at + 1:at + 1 + b[at]].decode('latin1'), at + 1 + b[at]


def parse_sym(b):
    """Function starts (0x8C) with their source file, plus plain symbols (types 1/2)."""
    assert b[:3] == b'MND'
    at, funcs, symbols = 8, [], {}
    while at + 5 <= len(b):
        value, kind = struct.unpack_from('<IB', b, at)
        at += 5
        if kind < 0x80:  # symbol records (globals, locals, labels): value + Pascal name
            name, at = pascal(b, at)
            symbols[name] = value
        elif kind in (0x80, 0x8a):
            pass
        elif kind == 0x82:
            at += 1
        elif kind == 0x84:
            at += 2
        elif kind == 0x86:
            at += 4
        elif kind == 0x88:
            at += 4
            _, at = pascal(b, at)
        elif kind == 0x8c:
            at += 2 + 4 + 2 + 4 + 4 + 4
            fname, at = pascal(b, at)
            name, at = pascal(b, at)
            funcs.append(dict(addr=value, file=fname, name=name))
        elif kind in (0x8e, 0x90, 0x92):
            at += 4
        elif kind == 0x94:
            at += 2 + 2 + 4
            _, at = pascal(b, at)
        elif kind == 0x96:
            at += 2 + 2 + 4
            dims = struct.unpack_from('<H', b, at)[0]
            at += 2 + 4 * dims
            _, at = pascal(b, at)
            _, at = pascal(b, at)
        elif kind == 0x98:
            at += 4
        elif kind == 0x9a:
            pass
        else:
            raise ValueError(f'unknown SYM record 0x{kind:02x} at {at - 5:#x}')
    return funcs, symbols


def demangle_gcc(name):
    """'AIInit_ClearAICar__FP8Car_tObj' -> 'AIInit_ClearAICar'; 'Update__9AIState_tFi' -> 'AIState_t::Update'."""
    if '__' not in name or name.startswith('__'):
        return name
    base, rest = name.split('__', 1)
    m = re.match(r'(?:C)?(\d+)([A-Za-z_][A-Za-z0-9_]*)', rest)
    if m and int(m.group(1)) <= len(m.group(2)) and not rest.startswith('F'):
        cls = m.group(2)[:int(m.group(1))]
        return f'{cls}::{base}'
    return base


# ---- PS-X EXE + MIPS string references --------------------------------------------------------
def psx_image(exe):
    assert exe[:8] == b'PS-X EXE'
    t_addr, t_size = struct.unpack_from('<II', exe, 0x18)
    return t_addr, exe[0x800:0x800 + t_size]


def c_string(mem, base, addr, minimum=4):
    o = addr - base
    if not 0 <= o < len(mem):
        return None
    end = mem.find(b'\0', o, o + 256)
    if end < 0 or end - o < minimum:
        return None
    s = mem[o:end]
    if all(32 <= c < 127 or c in (9, 10, 13) for c in s):
        return s.decode('latin1')
    return None


def mips_strings(mem, base, start, end):
    """String literals a MIPS function builds with lui/addiu (or ori) and lui/load-store offsets."""
    md = capstone.Cs(capstone.CS_ARCH_MIPS, capstone.CS_MODE_MIPS32 + capstone.CS_MODE_LITTLE_ENDIAN)
    md.detail = True
    hi = {}
    found = set()
    o = start - base
    for ins in md.disasm(mem[o:o + (end - start)], start):
        ops = ins.operands
        if ins.mnemonic == 'lui' and len(ops) == 2:
            hi[ops[0].reg] = (ops[1].imm & 0xffff) << 16
        elif ins.mnemonic in ('addiu', 'ori') and len(ops) == 3 and ops[1].reg in hi:
            v = hi[ops[1].reg] + (ops[2].imm if ins.mnemonic == 'addiu' else ops[2].imm & 0xffff)
            v &= 0xffffffff
            s = c_string(mem, base, v)
            if s:
                found.add(s)
        elif len(ops) == 2 and ops[1].type == capstone.mips.MIPS_OP_MEM and ops[1].mem.base in hi:
            v = (hi[ops[1].mem.base] + ops[1].mem.disp) & 0xffffffff
            s = c_string(mem, base, v)
            if s:
                found.add(s)
    return found


# ---- Porsche.exe ------------------------------------------------------------------------------
class PE:
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

    def string(self, va, minimum=4):
        o = self.off(va)
        if o is None:
            return None
        end = self.data.find(b'\0', o, o + 256)
        if end < 0 or end - o < minimum:
            return None
        s = self.data[o:end]
        return s.decode('latin1') if all(32 <= c < 127 or c in (9, 10, 13) for c in s) else None


def porsche_strings(pe, funcs):
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = True
    out = {}
    for va, lo, hi in funcs:
        o = pe.off(lo)
        found = set()
        for ins in md.disasm(pe.data[o:o + hi - lo], lo):
            for op in ins.operands:
                v = op.imm if op.type == capstone.x86.X86_OP_IMM else (
                    op.mem.disp if op.type == capstone.x86.X86_OP_MEM and not op.mem.base else None)
                if v is not None and v > 0x400000:
                    s = pe.string(v & 0xffffffff)
                    if s:
                        found.add(s)
        out[va] = found
    return out


def tokens(name):
    return [t for t in re.split(r'[_\W]+', re.sub(r'([a-z])([A-Z])', r'\1_\2', name)) if t]


def camel(word):
    return [t.lower() for t in re.findall(r'[A-Z]+(?=[A-Z][a-z]|$)|[A-Z]?[a-z0-9]+|[A-Z]+', word)]


def covers(stem, words, minimum=3):
    """True when `stem` spells the first words of `words`, each in full or abbreviated (>= 3 letters),
    always cutting at word boundaries: FEDIALOG covers FE|Dialog|Button, FETOURN covers FE|Tourny|...,
    FECARS does not cover FE|Car|Setting (the 's' would be a one-letter abbreviation)."""
    if not stem:
        return True
    if not words:
        return False
    w = words[0]
    if stem.startswith(w) and covers(stem[len(w):], words[1:], minimum):
        return True
    return any(stem == w[:n] for n in range(len(w) - 1, minimum - 1, -1))


def abbreviates(stem, cls):
    """AIH_HUM abbreviates AIHigh_Human (per '_' part); FEDIALOG abbreviates FEDialogButton."""
    a, b = stem.lower().split('_'), cls.split('_')
    if len(a) > 1:  # the file name already marks its word breaks: one-letter abbreviations allowed
        return len(a) == len(b) and all(covers(x, camel(y), 1) for x, y in zip(a, b))
    return covers(a[0], camel(cls.replace('_', '')))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--iso', type=Path, default=DEFAULT_ISO)
    args = ap.parse_args()
    files, read = iso_files(args.iso)
    sym = read('/NFS4.SYM')
    exe = read('/NFS4.EXE')
    nfs4_map = read('/NFS4.MAP').decode('latin1')
    iso_sha = dict(sym=hashlib.sha256(sym).hexdigest(), exe=hashlib.sha256(exe).hexdigest(),
                   map=hashlib.sha256(nfs4_map.encode('latin1')).hexdigest())
    sym_funcs, _ = parse_sym(sym)
    base, mem = psx_image(exe)
    end_of_image = base + len(mem)
    # Function bodies: SYM function starts, ends at the next start (within the main image).
    starts = sorted({(f['addr'], f['name'], f['file']) for f in sym_funcs if base <= f['addr'] < end_of_image})
    nfs4 = []
    for k, (addr, name, src) in enumerate(starts):
        nxt = starts[k + 1][0] if k + 1 < len(starts) else min(addr + 0x4000, end_of_image)
        nfs4.append(dict(addr=addr, end=nxt, name=name, readable=demangle_gcc(name), file=src))
    for f in nfs4:
        f['strings'] = sorted(mips_strings(mem, base, f['addr'], f['end']))

    data = PE_PATH.read_bytes()
    assert hashlib.sha256(data).hexdigest() == PE_SHA
    pe = PE(data)
    catalog = [json.loads(l) for l in (ROOT / 'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl')
               .read_text().splitlines()]
    pfuncs = [(e['entry_va'], int(e['ranges'][0][0], 16), int(e['ranges'][-1][1], 16) + 1) for e in catalog]
    pstr = porsche_strings(pe, pfuncs)

    # Layer 1: unique shared strings.
    n_users, p_users = collections.defaultdict(set), collections.defaultdict(set)
    for f in nfs4:
        for s in f['strings']:
            n_users[s].add(f['name'])
    for va, ss in pstr.items():
        for s in ss:
            p_users[s].add(va)
    by_name = {f['name']: f for f in nfs4}
    votes = collections.defaultdict(lambda: collections.defaultdict(list))
    for s in set(n_users) & set(p_users):
        if len(n_users[s]) == 1 and len(p_users[s]) == 1 and len(s.strip()) >= 6:
            votes[next(iter(p_users[s]))][next(iter(n_users[s]))].append(s)
    def distinctive(s):
        return len(s) >= 12 or bool(re.search(r'[%.\\/ ]', s))

    string_pairs = {}
    for va, cands in votes.items():
        if len(cands) == 1:
            name, strings = next(iter(cands.items()))
            if len(strings) < 2 and not any(distinctive(s) for s in strings):
                continue
            string_pairs[va] = dict(nfs4=name, readable=by_name[name]['readable'], nfs4_file=by_name[name]['file'],
                                    strings=strings)
    # A name claimed by several Porsche functions is not unique evidence.
    claims = collections.Counter(p['nfs4'] for p in string_pairs.values())
    string_pairs = {va: p for va, p in string_pairs.items() if claims[p['nfs4']] == 1}

    # Layer 2: identical initialised globals (MAP gives addresses; size = gap to the next symbol).
    msyms = sorted({(int(a, 16), n) for a, n in re.findall(r'^ ([0-9A-F]{8}) (\S+)$', nfs4_map, re.M)})
    pdata = b''.join(data[raw:raw + rs] for name, sva, vs, rs, raw in pe.sections if name in ('.rdata', '.data'))
    data_pairs = []
    for k, (addr, name) in enumerate(msyms):
        if not base <= addr < end_of_image or k + 1 >= len(msyms):
            continue
        size = min(msyms[k + 1][0] - addr, 4096)
        blob = mem[addr - base:addr - base + size]
        if size < 16 or len(set(blob)) < 4 or c_string(mem, base, addr):
            continue
        hits = [m.start() for m in re.finditer(re.escape(blob), pdata)]
        if len(hits) == 1:
            off = hits[0]
            for sname, sva, vs, rs, raw in pe.sections:
                if sname in ('.rdata', '.data'):
                    if off < rs:
                        data_pairs.append(dict(nfs4=name, va=f'{sva + off:08x}', bytes=size, section=sname))
                        break
                    off -= rs

    # Layer 2b: PS1 code stores tuning values in 16.16 fixed point, Porsche in IEEE floats. An NFS4
    # global of >= 4 dwords, converted value by value to float32, that occurs exactly once (aligned)
    # in Porsche.exe's data names that address. Tables of zeros/ones or repeated values are skipped.
    floats = {}
    for name, sva, vs, rs, raw in pe.sections:
        if name in ('.rdata', '.data'):
            floats[name] = (sva, data[raw:raw + rs])
    for k, (addr, name) in enumerate(msyms):
        if not base <= addr < end_of_image or k + 1 >= len(msyms) or addr % 4:
            continue
        size = min(msyms[k + 1][0] - addr, 4096) // 4 * 4
        if size < 16:
            continue
        ints = struct.unpack_from(f'<{size // 4}i', mem, addr - base)
        if len(set(ints)) < 3 or all(abs(v) < 0x100 for v in ints):
            continue
        blob = struct.pack(f'<{len(ints)}f', *(v / 65536.0 for v in ints))
        hits = []
        for sname, (sva, sdata) in floats.items():
            for m in re.finditer(re.escape(blob), sdata):
                if m.start() % 4 == 0:
                    hits.append((sname, sva + m.start()))
        if len(hits) == 1:
            data_pairs.append(dict(nfs4=name, va=f'{hits[0][1]:08x}', bytes=size, section=hits[0][0],
                                   encoding='16.16 fixed -> float32'))

    # Layer 3: RTTI class -> NFS4 file by abbreviation.
    cpp_files = sorted({f['file'] for f in sym_funcs if f['file'].lower().endswith(('.cpp', '.c'))})
    rtti = sorted({x.decode()[4:-2] for x in re.findall(rb'\.\?A[VU][A-Za-z0-9_]+@@', data)})
    heranca = {}
    for cls in rtti:
        outer = cls.split('@')[-1] if '@' in cls else cls
        hits = [p for p in cpp_files if abbreviates(p.rsplit('\\', 1)[1].rsplit('.', 1)[0], outer)]
        # A file that spells every part of the class (AIH_HUM for AIHigh_Human) beats one that only
        # spells its first word (AIHIGH).
        full = [p for p in hits if p.rsplit('\\', 1)[1].count('_') == outer.count('_') > 0]
        hits = full or hits
        if len(hits) == 1:
            heranca[outer] = hits[0]

    evidence = dict(schema=1, original_sha256=PE_SHA, iso=str(args.iso), nfs4_sha256=iso_sha,
                    nfs4_functions=len(nfs4), nfs4_files=cpp_files, string_pairs=string_pairs,
                    data_pairs=data_pairs, class_files=heranca,
                    nfs4_function_list=[dict(addr=f'{f["addr"]:08x}', name=f['name'], readable=f['readable'],
                                             file=f['file']) for f in nfs4])
    (OUT / 'nfs4-evidence.json').write_text(json.dumps(evidence, indent=1), encoding='utf-8')
    summary = dict(schema=1, nfs4_sha256=iso_sha, nfs4_functions=len(nfs4), nfs4_source_files=len(cpp_files),
                   nfs4_functions_with_strings=sum(1 for f in nfs4 if f['strings']),
                   string_pairs=len(string_pairs), data_pairs=len(data_pairs), class_files=len(heranca),
                   string_pair_sample={va: p['readable'] for va, p in sorted(string_pairs.items())[:40]},
                   data_pair_sample={p['va']: p['nfs4'] for p in data_pairs[:40]},
                   class_files_all=heranca)
    (RUN / 'nfs4-evidence-summary.json').write_text(json.dumps(summary, indent=1) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=1))


if __name__ == '__main__':
    main()
