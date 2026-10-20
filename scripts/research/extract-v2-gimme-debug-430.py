"""Run 430 (branch feat/lowered-whole-game): extract NFS5 debug evidence left inside gimme.dll.

gimme.dll ("FaceInRace", SHA 3a43b0f6...) was linked with leftover buffers holding NFS5 game object
files compiled with CodeView debug info. This script reads them without trusting anything it
cannot check against Porsche.exe:
- every source path string (D:\\dev\\NFS5\\..., D:\\dev\\library\\...);
- each embedded i386 COFF object: its sections, symbols, and its .debug$S records
  (S_OBJNAME, S_GPROC32/S_LPROC32 with parameter/local names, S_UDT names, data names);
- each function body still present, matched against Porsche.exe with relocated dwords masked.
  Only unique matches are reported as evidence.

Output: local/experiments/v2-lowered-exe-430/gimme-evidence.json (game-derived, not committed)
and a summary in the run folder.

Usage: py -3 scripts/research/extract-v2-gimme-debug-430.py
"""
import hashlib
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GIMME = ROOT / 'local/game/gimme.dll'
GIMME_SHA = '3a43b0f6a1608f69adc3a5009c9fe055a24e17197e85c4045c2c43e37eb75f6b'
PE_PATH = ROOT / 'local/game/Porsche.exe'
PE_SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
OUT = ROOT / 'local/experiments/v2-lowered-exe-430'
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/430-lowered-whole-game'

# CodeView symbol record kinds emitted by VC6 (32-bit type indices, Pascal strings).
S_OBJNAME, S_END = 0x0009, 0x0006
S_REGISTER, S_UDT, S_BPREL32 = 0x1001, 0x1003, 0x1006
S_LDATA32, S_GDATA32 = 0x1007, 0x1008
S_LPROC32, S_GPROC32 = 0x100a, 0x100b


def pascal(buf, at):
    n = buf[at] if at < len(buf) else 0
    return buf[at + 1:at + 1 + n].decode('latin1')


def parse_debug_s(buf):
    """Yields (kind, info) for the records we understand; stops at malformed data."""
    if len(buf) < 4:
        return
    at = 4  # CV signature
    stack = []
    while at + 4 <= len(buf):
        length, kind = struct.unpack_from('<HH', buf, at)
        if length < 2 or at + 2 + length > len(buf):
            return
        rec = buf[at + 4:at + 2 + length]
        if kind == S_OBJNAME and len(rec) >= 5:
            yield 'objname', dict(name=pascal(rec, 4))
        elif kind in (S_GPROC32, S_LPROC32) and len(rec) >= 35:
            parent, end, nxt, plen, dbg_start, dbg_end, typ, off, seg, flags = struct.unpack_from('<IIIIIIIIHB', rec, 0)
            proc = dict(name=pascal(rec, 35), length=plen, global_=kind == S_GPROC32, locals=[])
            stack.append(proc)
            yield 'proc', proc
        elif kind == S_BPREL32 and len(rec) >= 9 and stack:
            off, typ = struct.unpack_from('<iI', rec, 0)
            stack[-1]['locals'].append(dict(name=pascal(rec, 8), frame_offset=off))
        elif kind == S_REGISTER and len(rec) >= 7 and stack:
            typ, reg = struct.unpack_from('<IH', rec, 0)
            stack[-1]['locals'].append(dict(name=pascal(rec, 6), register=reg))
        elif kind == S_UDT and len(rec) >= 5:
            yield 'udt', dict(name=pascal(rec, 4))
        elif kind in (S_LDATA32, S_GDATA32) and len(rec) >= 11:
            yield 'data', dict(name=pascal(rec, 10), global_=kind == S_GDATA32)
        elif kind == S_END and stack:
            stack.pop()
        at += 2 + length


def objects(g):
    for m in re.finditer(rb'\x4c\x01', g):
        o = m.start()
        if o + 20 > len(g):
            continue
        nsec, ts, symptr, nsym, opt = struct.unpack_from('<HIIIH', g, o + 2)
        if not (1 <= nsec <= 2000 and opt == 0 and 0 < nsym < 500000 and o + symptr + 18 * nsym < len(g)):
            continue
        if g[o + 20:o + 21] not in (b'.', b'/'):
            continue
        secs = []
        for i in range(nsec):
            q = o + 20 + 40 * i
            name = g[q:q + 8].rstrip(b'\0').decode('latin1')
            size, raw, rel, ln, nrel, nln, ch = struct.unpack_from('<IIIIHHI', g, q + 16)
            secs.append(dict(name=name, size=size, raw=raw, rel=rel, nrel=nrel, ch=ch))
        symtab, strtab = o + symptr, o + symptr + 18 * nsym
        syms, k = [], 0
        while k < nsym:
            e = symtab + 18 * k
            raw_name = g[e:e + 8]
            if raw_name[:4] == b'\0\0\0\0':
                p = strtab + struct.unpack_from('<I', raw_name, 4)[0]
                name = g[p:g.find(b'\0', p)].decode('latin1')
            else:
                name = raw_name.rstrip(b'\0').decode('latin1')
            value, sec, typ, cls, naux = struct.unpack_from('<IhHBB', g, e + 8)
            aux = g[e + 18:e + 18 + 18 * naux]
            syms.append(dict(name=name, value=value, sec=sec, type=typ, cls=cls, aux=aux, index=k))
            k += 1 + naux
        yield o, secs, syms


SPECIAL = {'0': 'ctor', '1': 'dtor', '_E': 'vector_deleting_dtor', '_G': 'scalar_deleting_dtor'}


def demangle(sym):
    """Readable Class::Method for MSVC symbols ('?Load@WFarGroundBundle@@...' -> 'WFarGroundBundle::Load').

    Only the qualified name is decoded; parameter types are left out. Returns None for symbols
    that are not plain MSVC function names (compiler helpers, labels, garbage).
    """
    if not sym.startswith('?'):
        return None
    if sym.startswith('??'):
        code = sym[2:4] if sym[2] == '_' else sym[2]
        if code not in SPECIAL:
            return None
        rest = sym[2 + len(code):]
        scope = rest.split('@@', 1)[0].split('@')
        cls = '::'.join(reversed(scope))
        return f'{cls}::{SPECIAL[code]}' if cls else None
    body = sym[1:].split('@@', 1)[0]
    parts = body.split('@')
    if not all(re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', p) for p in parts):
        return None
    return '::'.join(reversed(parts))


def vtables(g, o, secs, syms):
    """Embedded vtables: ??_7Class@@6B@ data whose relocations point at the slot functions."""
    byidx = {s['index']: s['name'] for s in syms}
    out = []
    for v in syms:
        if not v['name'].startswith('??_7') or v['sec'] <= 0:
            continue
        sec = secs[v['sec'] - 1]
        slots = {}
        for r in range(sec['nrel']):
            va, si, typ = struct.unpack_from('<IIH', g, o + sec['rel'] + 10 * r)
            if v['value'] <= va < v['value'] + sec['size'] and typ == 6:  # IMAGE_REL_I386_DIR32
                name = byidx.get(si, '')
                if demangle(name):
                    slots[(va - v['value']) // 4] = dict(symbol=name, name=demangle(name))
        cls = '::'.join(reversed(v['name'][4:].split('@@', 1)[0].split('@')))
        out.append(dict(cls=cls, symbol=v['name'], slots=slots))
    return out


def text_of(exe):
    pe = struct.unpack_from('<I', exe, 0x3c)[0]
    base = struct.unpack_from('<I', exe, pe + 52)[0]
    sh = pe + 24 + struct.unpack_from('<H', exe, pe + 20)[0]
    vs, va, rs, raw = struct.unpack_from('<IIII', exe, sh + 8)
    return base + va, exe[raw:raw + rs]


def main():
    g = GIMME.read_bytes()
    assert hashlib.sha256(g).hexdigest() == GIMME_SHA
    exe = PE_PATH.read_bytes()
    assert hashlib.sha256(exe).hexdigest() == PE_SHA
    text_va, text = text_of(exe)
    paths = sorted({m.group().decode('latin1') for m in re.finditer(
        rb'[A-Za-z]:\\dev\\[ -~]{3,160}?\.(?:cpp|c|h|hpp|inl)', g, re.I)})
    objs, matches = [], []
    for o, secs, syms in objects(g):
        info = dict(offset=f'{o:x}', sections=len(secs), symbols=len(syms), objname=None, files=[],
                    procs=[], udts=[], data=[], functions=[], vtables=vtables(g, o, secs, syms))
        for s in syms:
            if s['cls'] == 103:  # C_FILE: name in aux records
                info['files'].append(s['aux'].rstrip(b'\0').decode('latin1'))
        for sec in secs:
            if sec['name'] != '.debug$S' or not sec['raw']:
                continue
            for kind, rec in parse_debug_s(g[o + sec['raw']:o + sec['raw'] + sec['size']]):
                if kind == 'objname':
                    info['objname'] = rec['name']
                elif kind == 'proc':
                    info['procs'].append(rec)
                elif kind == 'udt':
                    info['udts'].append(rec['name'])
                elif kind == 'data':
                    info['data'].append(rec['name'])
        for s in syms:
            if not (s['sec'] > 0 and (s['type'] >> 4) == 2 and s['cls'] == 2):
                continue
            sec = secs[s['sec'] - 1]
            if not (sec['ch'] & 0x20) or not sec['raw']:
                continue
            later = sorted(t['value'] for t in syms if t['sec'] == s['sec'] and t['value'] > s['value'])
            size = (later[0] if later else sec['size']) - s['value']
            body = g[o + sec['raw'] + s['value']:o + sec['raw'] + s['value'] + size]
            relocs = set()
            for r in range(sec['nrel']):
                va, si, typ = struct.unpack_from('<IIH', g, o + sec['rel'] + 10 * r)
                if s['value'] <= va < s['value'] + size:
                    relocs.add(va - s['value'])
            fn = dict(symbol=s['name'], bytes=size, match=None)
            if size >= 16:
                pat, k = b'', 0
                while k < size:
                    if k in relocs:
                        pat, k = pat + b'....', k + 4
                    else:
                        pat, k = pat + re.escape(body[k:k + 1]), k + 1
                hits = [h.start() for h in re.finditer(pat, text, re.S)]
                fn['hits'] = len(hits)
                if len(hits) == 1 and demangle(s['name']):
                    fn['match'] = f'{text_va + hits[0]:08x}'
                    matches.append(dict(va=fn['match'], symbol=s['name'], name=demangle(s['name']), bytes=size,
                                        object=info['objname'],
                                        files=info['files']))
            info['functions'].append(fn)
        objs.append(info)
    evidence = dict(schema=1, gimme_sha256=GIMME_SHA, original_sha256=PE_SHA, paths=paths, objects=objs,
                    matches=matches)
    (OUT / 'gimme-evidence.json').write_text(json.dumps(evidence, indent=1), encoding='utf-8')
    summary = dict(schema=1, gimme_sha256=GIMME_SHA, paths=len(paths),
                   cpp_paths=sum(p.lower().endswith(('.c', '.cpp')) for p in paths), objects=len(objs),
                   objnames=[x['objname'] for x in objs], procs=sum(len(x['procs']) for x in objs),
                   procs_with_locals=sum(1 for x in objs for p in x['procs'] if p['locals']),
                   udts=sum(len(x['udts']) for x in objs), function_bodies=sum(len(x['functions']) for x in objs),
                   unique_matches=[dict(va=m['va'], name=m['name']) for m in matches],
                   vtables={v['cls']: {k: s['name'] for k, s in sorted(v['slots'].items())}
                            for x in objs for v in x['vtables']})
    (RUN / 'gimme-evidence-summary.json').write_text(json.dumps(summary, indent=1) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in summary.items()}, indent=1))


if __name__ == '__main__':
    main()
