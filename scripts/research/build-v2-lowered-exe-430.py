"""Run 430: lower every catalogued Porsche.exe function and link them into one EXE.

Prototype of the "lower everything, then humanize" path. The lowered functions run
against the original image, which the runtime maps at its original VAs from
local/game/Porsche.exe at start-up; no game bytes are written to the repository.

Extra lowering rules on top of x86-cpp-backend-fpu.py (needed to execute, not syntax):
- fs-relative operands add the thread's TEB base (the frozen backend treats fs as flat);
- an indirect JMP through a jump table inside the function becomes a switch over the
  table's in-function targets, read from the PE; other indirect JMPs fall back to every
  instruction start of the function.

Usage: py -3 scripts/research/build-v2-lowered-exe-430.py [--generate-only] [--jobs N]
"""
import argparse
import collections
import hashlib
import importlib.util
import json
import os
import re
import struct
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PE_PATH = ROOT / 'local/game/Porsche.exe'
PE_SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
CATALOG = ROOT / 'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl'
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/430-lowered-whole-game'
OUT = ROOT / 'local/experiments/v2-lowered-exe-430'
# Generated C++ (the game's code, never committed) lives outside the repository.
GEN = Path(os.environ.get('PORSCHE430_GEN', r'D:\projetos\porsche-src'))
PER_TU = 64

FS_BEFORE = "        terms = [f'0x{m.disp & 0xffffffff:08x}u']"
FS_AFTER = "        terms = [f'0x{m.disp & 0xffffffff:08x}u'] + (['fs257()'] if m.segment == 32 else [])"

# Approximations this branch accepts (documented in the run README); upstream rejects them.
APPROXIMATIONS = [
    ("            raise ValueError('Unsupported fsqrt until guest FPU status/CW parity is modelled')",
     "            code = 'fpu_st(s) = sqrt(fpu_st(s));'"),
    ("                if ops[0].size not in (4, 8): raise ValueError('Unsupported fld memory width')\n"
     "                fn = 'read_f32' if ops[0].size == 4 else 'read_f64'",
     "                if ops[0].size not in (4, 8, 10): raise ValueError('Unsupported fld memory width')\n"
     "                fn = 'read_f32' if ops[0].size == 4 else 'read_f64' if ops[0].size == 8 else 'read_f80_430'"),
    ("                if ops[0].size not in (4, 8): raise ValueError('Unsupported fst/fstp memory width')\n"
     "                fn = 'write_f32' if ops[0].size == 4 else 'write_f64'",
     "                if ops[0].size not in (4, 8, 10): raise ValueError('Unsupported fst/fstp memory width')\n"
     "                fn = 'write_f32' if ops[0].size == 4 else 'write_f64' if ops[0].size == 8 else 'write_f80_430'"),
    # DF is modelled only for the one std/repne scasb/cld sequence in the binary (005a2885).
    ("        elif m in ('nop', 'cld', 'std'):",
     "        elif m == 'cld':\n"
     "            code = 's.flags&=~0x400u;'\n"
     "        elif m == 'std':\n"
     "            code = 's.flags|=0x400u;'\n"
     "        elif m in ('nop', 'prefetch', 'prefetchw', 'prefetchnta', 'prefetcht0', 'prefetcht1', 'prefetcht2'):"),
    ("            code = 'repne_scasb257(s);'",
     "            code = 'if(s.flags&0x400u)repne_scasb_down430(s);else repne_scasb257(s);'"),
    ("            raise ValueError('Unsupported instruction (no exact lowering): ' + m)",
     "            code = 'unlowered430(s);return;'"),
]

HEADER_EXTRA = r'''
#include <math.h>
extern "C" unsigned long __readfsdword(unsigned long);
#pragma intrinsic(__readfsdword)
static inline U fs257(){return static_cast<U>(__readfsdword(0x18));}
static inline U read257(U a,U n){
    return n==1?*reinterpret_cast<const B*>(a):n==2?*reinterpret_cast<const unsigned short*>(a):*reinterpret_cast<const U*>(a);
}
static inline void write257(U a,U n,U v){
    if(n==1)*reinterpret_cast<B*>(a)=static_cast<B>(v);
    else if(n==2)*reinterpret_cast<unsigned short*>(a)=static_cast<unsigned short>(v);
    else *reinterpret_cast<U*>(a)=v;
}
static inline double read_f80_430(U a){
    U64 man=static_cast<U64>(read257(a,4u))|(static_cast<U64>(read257(a+4u,4u))<<32);
    U se=read257(a+8u,2u);int e=static_cast<int>(se&0x7fffu);double sign=(se&0x8000u)?-1.0:1.0;
    if(e==0&&man==0)return sign*0.0;
    if(e==0x7fff)return (man<<1)?NAN:sign*INFINITY;
    return sign*ldexp(static_cast<double>(man),e-16383-63);
}
static inline void write_f80_430(U a,double v){
    U se=signbit(v)?0x8000u:0u;U64 man=0;
    if(isnan(v)){se|=0x7fffu;man=0xc000000000000000ull;}
    else if(isinf(v)){se|=0x7fffu;man=0x8000000000000000ull;}
    else if(v!=0.0){int e;double m=frexp(fabs(v),&e);man=static_cast<U64>(ldexp(m,64));se|=static_cast<U>(e-1+16383);}
    write257(a,4u,static_cast<U>(man));write257(a+4u,4u,static_cast<U>(man>>32));write257(a+8u,2u,se);
}
void unlowered430(Machine257&);  // 3DNow!/FPU environment images: fatal if reached
void repne_scasb_down430(Machine257&);  // repne scasb with DF set
// Target is evaluated by the generated caller before ESP changes.
static inline bool call257(Machine257&s,U target,U returnPC){
    s.r[4]-=4u;write257(s.r[4],4u,returnPC);dispatch257(s,target);
    if(s.stop!=Stop257::Returned||s.pc!=returnPC){if(s.stop==Stop257::Returned)s.stop=Stop257::BadReturn;return false;}
    s.stop=Stop257::Running;return true;
}
'''


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def backend():
    be = load('backend_fpu_430', ROOT / 'scripts/research/x86-cpp-backend-fpu.py')
    src = be.DERIVED_SOURCE
    for before, after in [(FS_BEFORE, FS_AFTER), *APPROXIMATIONS]:
        assert src.count(before) == 1, 'patch context drift: ' + before
        src = src.replace(before, after)
    ns = dict(be._namespace)
    exec(compile(src, 'backend-430::derived', 'exec'), ns)
    header = be.HEADER
    for decl in ('U read257(U address, U bytes);\n', 'void write257(U address, U bytes, U value);\n'):
        assert header.count(decl) == 1
        header = header.replace(decl, '')
    header = header.replace('void dispatch257(Machine257&, U target);\n',
                            'void dispatch257(Machine257&, U target);\n' + HEADER_EXTRA)
    # Speed (same results): force-inline every helper, and divide in 32 bits when EDX only
    # sign-/zero-extends EAX (the cdq/xor edx,edx + div pattern) instead of calling the
    # CRT's 64-bit division.
    header = header.replace('static inline ', 'static __forceinline ')
    fast_paths = [
        ('static __forceinline void idiv257_1(Machine257& s, U b) {\n',
         'static __forceinline void idiv257_1(Machine257& s, U b) {\n'
         '    if (b != 0u && s.r[2] == ((s.r[0] & 0x80000000u) ? 0xffffffffu : 0u) &&\n'
         '        !(s.r[0] == 0x80000000u && b == 0xffffffffu)) {\n'
         '        int a = (int)s.r[0], d = (int)b; s.r[0] = (U)(a / d); s.r[2] = (U)(a % d); return;\n'
         '    }\n'),
        ('static __forceinline void div257_1(Machine257& s, U b) {\n',
         'static __forceinline void div257_1(Machine257& s, U b) {\n'
         '    if (b != 0u && s.r[2] == 0u) { U a = s.r[0]; s.r[0] = a / b; s.r[2] = a % b; return; }\n'),
    ]
    for before, after in fast_paths:
        assert header.count(before) == 1, before
        header = header.replace(before, after)
    # The runtime never budgets execution; keep pc for diagnostics.
    step_old = ('static __forceinline bool step257(Machine257&s,U pc){\n'
                '    if(s.stop!=Stop257::Running)return false;s.pc=pc;\n'
                '    if(!s.budget){s.stop=Stop257::BudgetExhausted;return false;}--s.budget;return true;\n}')
    assert header.count(step_old) == 1
    header = header.replace(step_old, 'static __forceinline bool step257(Machine257&s,U pc){\n'
                            '    if(s.stop!=Stop257::Running)return false;s.pc=pc;return true;\n}')
    return ns["translate"], header + HEADER_NF


class Image:
    def __init__(self, data):
        pe = struct.unpack_from('<I', data, 0x3c)[0]
        self.base = struct.unpack_from('<I', data, pe + 52)[0]
        self.size = struct.unpack_from('<I', data, pe + 80)[0]
        self.entry = self.base + struct.unpack_from('<I', data, pe + 40)[0]
        sh = pe + 24 + struct.unpack_from('<H', data, pe + 20)[0]
        self.sections = []
        for i in range(struct.unpack_from('<H', data, pe + 6)[0]):
            q = sh + 40 * i
            vs, va, rs, raw = struct.unpack_from('<IIII', data, q + 8)
            self.sections.append((data[q:q + 8].rstrip(b'\0').decode(), self.base + va, vs, rs, raw,
                                  struct.unpack_from('<I', data, q + 36)[0]))
        self.data = data

    def read(self, va, n):
        for _, sva, vs, rs, raw, _ in self.sections:
            if sva <= va and va + n <= sva + min(vs, rs):
                return self.data[raw + va - sva:raw + va - sva + n]
        return None


JMP_TABLE = re.compile(r'dword ptr \[(?:e[a-z]{2})\*4 \+ (0x[0-9a-f]+)\]')


STATS = {"dead_flag_writes": 0}
BRANCH_IMM = re.compile(r'0x[0-9a-f]+')

# Dead-flag elimination. A flag write is dead when, going forward in the same range, a full
# flag writer comes before anything that may read EFLAGS or leave the straight line. Only
# instructions known not to touch EFLAGS are crossed; everything else keeps flags live.
FLAG_FULL = {'add', 'sub', 'cmp', 'test', 'and', 'or', 'xor', 'neg'}
FLAG_PARTIAL = {'inc', 'dec'}
FLAG_NEUTRAL = {'mov', 'movzx', 'movsx', 'lea', 'push', 'pop', 'nop', 'not', 'cdq', 'xchg',
                'fld', 'fst', 'fstp', 'fild', 'fistp', 'fadd', 'faddp', 'fsub', 'fsubp', 'fsubr',
                'fsubrp', 'fmul', 'fmulp', 'fdiv', 'fdivp', 'fdivr', 'fdivrp', 'fchs', 'fabs', 'fxch',
                'fldz', 'fld1', 'fnstsw', 'fldcw', 'fnstcw', 'fcom', 'fcomp', 'fcompp', 'fucom',
                'fucomp', 'fucompp', 'fst', 'fsin', 'fcos', 'fsqrt', 'wait',
                'movss', 'movaps', 'movups', 'movd', 'movq'}
NO_FLAGS = [('add257(s,', 'add257nf('), ('subtract257(s,', 'subtract257nf('), ('logical257(s,', 'logical257nf('),
            ('inc257(s,', 'inc257nf('), ('dec257(s,', 'dec257nf(')]
HEADER_NF = r'''
// Value-only forms used where the flags an instruction writes are provably dead.
static __forceinline U add257nf(U a,U b,U bits){return (a+b)&mask257(bits);}
static __forceinline U subtract257nf(U a,U b,U c,U bits){return (a-b-c)&mask257(bits);}
static __forceinline U logical257nf(U v,U bits){return v&mask257(bits);}
static __forceinline U inc257nf(U a,U bits){return (a+1u)&mask257(bits);}
static __forceinline U dec257nf(U a,U bits){return (a-1u)&mask257(bits);}
'''


def full_writer(w):
    # Only a lowering that really goes through a full-flag helper counts as a killer.
    return w['mnemonic'] in FLAG_FULL and any(h in w['cpp'] for h in ('add257(s,', 'subtract257(s,', 'logical257(s,'))


def kill_dead_flags(code, witness):
    killed = 0
    for k, w in enumerate(witness):
        m = w['mnemonic']
        if m not in FLAG_FULL and m not in FLAG_PARTIAL:
            continue
        if not any(old in w['cpp'] for old, _ in NO_FLAGS):
            continue
        dead = False
        for nxt in witness[k + 1:k + 24]:
            n = nxt['mnemonic']
            if full_writer(nxt):
                dead = True
                break
            if n not in FLAG_NEUTRAL:
                break
        if not dead:
            continue
        new = w['cpp']
        for old, nf in NO_FLAGS:
            new = new.replace(old, nf)
        marker = f" // {w['va']} {w['bytes']} "
        at = code.index(marker)
        block = '{ ' + w['cpp'] + ' }'
        at = code.index(block, at)
        code = code[:at] + '{ ' + new + ' }' + code[at + len(block):]
        killed += 1
    return code, killed


def lower(translate, img, va, size, entries=()):
    """Lower one contiguous range. `entries` are mid-range addresses other ranges enter."""
    raw = img.read(va, size)
    code, witness = translate(raw, va)
    code, killed = kill_dead_flags(code, witness)
    STATS["dead_flag_writes"] += killed
    starts = [int(w['va'], 16) for w in witness]
    lo, hi = va, va + len(raw)
    need = set(t for t in entries if t in starts and t != va)
    for w in witness:
        if (w['mnemonic'] != 'jmp' or 'dispatch257(s,target);return;' not in w['cpp']
                or w['operands'].startswith('0x')):
            continue
        targets = []
        m = JMP_TABLE.fullmatch(w['operands'])
        if m:
            table = int(m.group(1), 16)
            while True:
                cell = img.read(table + 4 * len(targets), 4)
                t = struct.unpack('<I', cell)[0] if cell else 0
                if not lo <= t < hi or t not in starts:
                    break
                targets.append(t)
        if not targets:
            targets = starts
        targets = sorted(set(targets))
        need.update(targets)
        cases = ''.join(f'case 0x{t:08x}u:goto L_{t:08x};' for t in targets)
        old = '{ ' + w['cpp'] + ' }'
        new = '{ ' + w['cpp'].replace('dispatch257(s,target);return;',
                                      f'switch(target){{{cases}default:dispatch257(s,target);return;}}') + ' }'
        marker = f" // {w['va']} {w['bytes']} "
        at = code.index(marker)
        at = code.index(old, at)
        code = code[:at] + new + code[at + len(old):]
    for t in sorted(need):
        label = f'L_{t:08x}:'
        if label not in code:
            marker = f' // {t:08x} '
            code = code.replace('\n' + marker, f'\n{label}\n{marker}', 1)
    # Falling off the end of a range continues at the next address (tail dispatch).
    tail = ' s.stop = Stop257::Returned; return;\n}'
    if code.rstrip().endswith(tail.strip()):
        at = code.rindex(' s.stop = Stop257::Returned; return;')
        code = code[:at] + f' dispatch257(s,0x{hi:08x}u); return;' + code[at + len(' s.stop = Stop257::Returned; return;'):]
    mids = sorted(t for t in set(entries) if t in starts and t != va)
    if mids:
        head = f'void translated_{va:08x}(Machine257&s){{'
        cases = ''.join(f'case 0x{t:08x}u:goto L_{t:08x};' for t in mids)
        code = code.replace(head, head + f'\n switch(s.pc){{{cases}default:break;}}', 1)
    branch_targets = set()
    for w in witness:
        if w['mnemonic'].startswith('j') or w['mnemonic'] == 'call':
            for x in BRANCH_IMM.findall(w['operands']):
                if 'ptr' not in w['operands']:
                    branch_targets.add(int(x, 16))
    return code, len(witness), mids, starts, branch_targets


def pointer_entries(img, entries):
    """Code addresses stored in data (HIGHLOW relocations) that the catalog does not start.

    Returns synthetic functions for targets outside every catalogued range (each runs to
    the next catalogued range, minus padding) and the set of all pointer targets, which
    become mid-body entries when they land inside a range.
    """
    data, base = img.data, img.base
    pe = struct.unpack_from('<I', data, 0x3c)[0]
    rva, size = struct.unpack_from('<II', data, pe + 24 + 96 + 8 * 5)
    code = [(sva, sva + vs) for name, sva, vs, rs, raw, ch in img.sections if ch & 0x20000000]
    targets = set()
    at = 0
    while at < size:
        page, block = struct.unpack('<II', img.read(base + rva + at, 8))
        if block < 8:
            break
        for k in range((block - 8) // 2):
            item = struct.unpack('<H', img.read(base + rva + at + 8 + 2 * k, 2))[0]
            if item >> 12 == 3:
                cell = img.read(base + page + (item & 0xfff), 4)
                v = struct.unpack('<I', cell)[0] if cell else 0
                if any(lo <= v < hi for lo, hi in code):
                    targets.add(v)
        at += block
    return gap_pieces(img, entries, targets), targets


def code_ranges(img):
    return [(sva, sva + vs) for name, sva, vs, rs, raw, ch in img.sections if ch & 0x20000000]


def gap_pieces(img, entries, targets):
    """Synthetic functions for code targets that no range of `entries` covers."""
    code = code_ranges(img)
    ranges = sorted((int(a, 16), int(b, 16) + 1) for e in entries for a, b in e['ranges'])
    starts = [a for a, _ in ranges]
    synthetic = []
    import bisect
    outside = []
    for t in sorted(targets):
        if not any(lo <= t < hi for lo, hi in code):
            continue
        k = bisect.bisect_right(starts, t) - 1
        if not (k >= 0 and ranges[k][0] <= t < ranges[k][1]):
            outside.append((t, k))
    # One piece per target, ending at the next target in the same gap (or the gap's end);
    # a piece that falls off its end continues into the next one by tail dispatch, and a
    # piece that is really data fails on its own.
    for j, (t, k) in enumerate(outside):
        end = starts[k + 1] if k + 1 < len(starts) else next(hi for lo, hi in code if lo <= t < hi)
        if j + 1 < len(outside) and outside[j + 1][1] == k:
            end = min(end, outside[j + 1][0])
        body = img.read(t, end - t) or b''
        n = len(body)
        while n and body[n - 1] in (0xcc, 0x90):
            n -= 1
        if n:
            synthetic.append(dict(entry_va=f'{t:08x}', name=f'PTR_{t:08x}', ranges=[[f'{t:08x}', f'{t + n - 1:08x}']],
                                  body_bytes=n, synthetic=True))
    return synthetic


def generate(translate, header, img, entries, pointers=()):
    gen = GEN
    gen.mkdir(parents=True, exist_ok=True)
    written = set()

    def put(path, text):
        # Rewrite only changed files so the build recompiles only what changed.
        written.add(str(path))
        if not path.exists() or path.read_text(encoding='utf-8') != text:
            path.write_text(text, encoding='utf-8')

    put(gen / 'machine257.h', header)
    table_rows, rejected = [], []
    tu, tu_index, insns, functions, ranges = [], 0, 0, 0, 0
    t0 = time.time()

    def flush():
        nonlocal tu, tu_index
        if tu:
            put(gen / f'lowered_{tu_index:03d}.cpp', '#include "machine257.h"\n' + '\n'.join(tu))
            tu, tu_index = [], tu_index + 1

    # Pass 1: lower every range alone and collect direct branch/call targets that come from
    # outside the range they land in (cross-range jumps, shared CRT tails such as strcpy ->
    # strcat). Pass 2 re-lowers only the ranges that such targets enter mid-body.
    first, external = {}, set(pointers)
    entries = list(entries)
    pending = list(entries)
    added = 0
    while pending:
        for e in pending:
            spans = [(int(a, 16), int(b, 16) + 1 - int(a, 16)) for a, b in e['ranges']]
            try:
                first[e['entry_va']] = [(a, n, lower(translate, img, a, n)) for a, n in spans]
            except Exception as x:  # noqa: BLE001 - recorded as an explicit boundary
                rejected.append(dict(va=e['entry_va'], reason=str(x)[:120]))
                continue
            for a, n, res in first[e['entry_va']]:
                external.update(t for t in res[4] if not a <= t < a + n)
                if f'dispatch257(s,0x{a + n:08x}u); return;' in res[0][-200:]:
                    external.add(a + n)  # fallthrough into the next range
        # Direct targets in gaps (code no catalogued range covers) become new pieces.
        pending = [p for p in gap_pieces(img, entries, external) if p['entry_va'] not in first]
        pending = [p for p in pending if p['entry_va'] not in {r['va'] for r in rejected}]
        entries += pending
        added += len(pending)
    layout = source_layout(entries)
    files = collections.defaultdict(list)
    for e in entries:
        if e['entry_va'] not in first:
            continue
        out = []
        for a, n, res in first[e['entry_va']]:
            mids = {t for t in external if a < t < a + n} & set(res[3])
            out.append(lower(translate, img, a, n, mids) if mids else res)
        spans = [(a, n) for a, n, _ in first[e['entry_va']]]
        rel, ident = layout[e['entry_va']]
        functions += 1
        for k, ((a, _), (code, n, mids, _, _)) in enumerate(zip(spans, out)):
            ranges += 1
            insns += n
            name = ident if k == 0 else f'{ident}_part_{a:08x}'
            code = code.replace('#include "machine257.h"\n', '')
            code = code.replace(f'void translated_{a:08x}(Machine257&s){{', f'void {name}(Machine257&s){{', 1)
            files[rel].append((a, name, code))
            table_rows.append((a, name))
            table_rows.extend((t, name) for t in mids)
    src = gen / 'src'
    for rel, items in sorted(files.items()):
        path = src / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        origin = SOURCE_NOTES.get(rel, '')
        body = '\n'.join(code for _, _, code in sorted(items))
        put(path, f'// {origin}\n#include "machine257.h"\n' + body if origin else '#include "machine257.h"\n' + body)
        tu_index += 1
    fns = sorted({f for _, f in table_rows})
    table = ['#include "machine257.h"', *(f'void {f}(Machine257&);' for f in fns),
             'struct LoweredEntry430{U va;void(*fn)(Machine257&);};',
             f'extern const unsigned lowered_count430={len(table_rows)}u;',
             'extern const LoweredEntry430 lowered_table430[]={',
             *(f'{{0x{v:08x}u,{f}}},' for v, f in sorted(table_rows)), '};', '']
    put(gen / 'lowered_table.cpp', '\n'.join(table))
    for old in list(gen.glob('lowered_[0-9]*.cpp')) + [p for p in src.rglob('*.cpp') if str(p) not in written]:
        old.unlink()
    for d in sorted((p for p in src.rglob('*') if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
        if not any(d.iterdir()):
            d.rmdir()
    return dict(dead_flag_writes=STATS["dead_flag_writes"], gap_pieces_added=added, lowered=functions, ranges=ranges,
                table_entries=len(table_rows), rejected=rejected, instructions=insns, source_files=tu_index,
                generate_seconds=round(time.time() - t0, 1))


SOURCE_NOTES = {}
CANON_CASE = {}


def canonical_rel(original):
    """Original path -> relative .cpp path, one tree for both build roots.

    Porsche.exe was built under d:\\Nfs\\ and the gimme.dll objects under D:\\dev\\; both hold the
    same tree (Nfs5\\..., Support\\..., library\\...). Drive and root are dropped, and each
    directory keeps the spelling it was first seen with (Windows paths are case-insensitive).
    """
    parts = [p for p in re.split(r'[\\/]', original) if p and not p.endswith(':') and p != '..']
    if parts and parts[0].lower() in ('dev', 'nfs') and len(parts) > 2:
        parts = parts[1:]
    out = []
    for k, p in enumerate(parts[:-1]):
        key = '/'.join(x.lower() for x in parts[:k + 1])
        out.append(CANON_CASE.setdefault(key, p))
    return '/'.join(out + [parts[-1].rsplit('.', 1)[0] + '.cpp'])


def source_layout(entries):
    """entry_va -> (relative .cpp path, function identifier), following the game's own source tree.

    Uses attribution.json from attribute-v2-source-files-430.py. Functions whose original file
    is known go to that path (drive and leading separators dropped, extension .cpp). Functions
    with only an RTTI class go to _sem_arquivo/classes/<outer name>.cpp; the rest go to
    _sem_arquivo/codigo/ in contiguous .text chunks. Identifiers come from RTTI names when
    present, otherwise FUN_<va> (catalog) or PTR_<va> (pointer-only pieces).
    """
    path = OUT / 'attribution.json'
    by_func = json.loads(path.read_text(encoding='utf-8'))['by_function'] if path.exists() else {}
    layout, used, rest = {}, {}, []
    for e in sorted(entries, key=lambda e: int(e['entry_va'], 16)):
        va = e['entry_va']
        info = by_func.get(va, {})
        real = info.get('real_names') or []
        names = real or info.get('names') or []
        shared = len({n.split('::')[0] for n in names}) > 1  # folded body used by several classes
        if real and not shared:
            ident = re.sub(r'[^A-Za-z0-9]+', '_', real[0].replace('::', '__')) + '_' + va
        elif shared:
            ident = f'shared_{va}'
        elif names:
            ident = re.sub(r'[^A-Za-z0-9]+', '_', names[0].replace('::', '__')) + '_' + va
        else:
            ident = f'PTR_{va}' if e.get('synthetic') else f'FUN_{va}'
        if info.get('file'):
            original = info['file']
            rel = canonical_rel(original)
            SOURCE_NOTES[rel] = f'original source: {original} (evidence: see attribution.json)'
        elif shared:
            rel = '_sem_arquivo/classes/_compartilhadas.cpp'
            SOURCE_NOTES[rel] = ('original file unknown; bodies folded by the linker and shared by several '
                                 'classes (all names in attribution.json)')
        elif names:
            outer = re.sub(r'[^A-Za-z0-9]+', '_', names[0].split('::')[0])
            rel = f'_sem_arquivo/classes/{outer}.cpp'
            SOURCE_NOTES[rel] = 'original file unknown; grouped by RTTI class/namespace'
        else:
            rel = None
            rest.append(va)
        layout[va] = (rel, ident)
    for k in range(0, len(rest), 64):
        chunk = rest[k:k + 64]
        rel = f'_sem_arquivo/codigo/{chunk[0]}_{chunk[-1]}.cpp'
        SOURCE_NOTES[rel] = 'original file unknown; contiguous .text range'
        for va in chunk:
            layout[va] = (rel, layout[va][1])
    # Object files are named after the source base name; keep base names unique.
    count, final = collections.Counter(), {}
    for rel in sorted({r for r, _ in layout.values()}):
        base = rel.rsplit('/', 1)[-1].lower()
        count[base] += 1
        final[rel] = rel if count[base] == 1 else rel[:-4] + f'_{count[base]}.cpp'
        SOURCE_NOTES[final[rel]] = SOURCE_NOTES.get(rel, '')
    return {va: (final[rel], ident) for va, (rel, ident) in layout.items()}


def toolchain():
    roots = [Path(r'C:\Program Files\Microsoft Visual Studio'), Path(r'C:\Program Files (x86)\Microsoft Visual Studio')]
    cl = sorted(c for r in roots if r.exists() for c in r.glob('*/*/VC/Tools/MSVC/*/bin/Hostx64/x86/cl.exe'))[-1]
    kits = Path(r'C:\Program Files (x86)\Windows Kits\10')
    sdk_inc = sorted(p for p in (kits / 'Include').iterdir() if (p / 'um').exists())[-1]
    vc = cl.parents[3]
    env = dict(os.environ)
    env['INCLUDE'] = ';'.join(str(p) for p in [vc / 'include', sdk_inc / 'ucrt', sdk_inc / 'shared', sdk_inc / 'um'])
    env['LIB'] = ';'.join(str(p) for p in [vc / 'lib/x86', kits / 'Lib' / sdk_inc.name / 'ucrt/x86',
                                            kits / 'Lib' / sdk_inc.name / 'um/x86'])
    return cl, cl.parent / 'link.exe', env


def build(jobs):
    cl, link, env = toolchain()
    gen, obj = GEN, OUT / 'obj'
    obj.mkdir(parents=True, exist_ok=True)
    sources = sorted((gen / 'src').rglob('*.cpp')) + [gen / 'lowered_table.cpp', RUN / 'runtime_430.cpp']
    keep = {p.stem for p in sources} | {'reserve_430'}
    header = gen / 'machine257.h'

    def stale(src):
        o = obj / (src.stem + '.obj')
        return not o.exists() or o.stat().st_mtime < max(src.stat().st_mtime, header.stat().st_mtime)

    sources = [s for s in sources if stale(s)]
    t0 = time.time()
    r = subprocess.CompletedProcess([], 0, '', '')
    if sources:
        # Hundreds of sources: pass them through a response file.
        rsp = OUT / 'compile.rsp'
        rsp.write_text('\n'.join(f'"{p}"' for p in sources), encoding='utf-8')
        cmd = [str(cl), '/nologo', '/c', '/std:c++17', '/O2', '/GS-', '/EHs-c-', '/bigobj', '/W0', f'/MP{jobs}',
               f'/I{gen}', f'/Fo{obj}\\', f'@{rsp}']
        r = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=OUT)
    (OUT / 'compile.log').write_text(r.stdout + r.stderr, encoding='utf-8')
    compile_s = round(time.time() - t0, 1)
    for o in obj.glob('*.obj'):
        if o.stem not in keep:
            o.unlink()
    if r.returncode:
        errors = [ln for ln in r.stdout.splitlines() if ' error ' in ln]
        return dict(compile_seconds=compile_s, compile_errors=len(errors), first_errors=errors[:10])
    r = subprocess.run([str(cl.parent / 'ml.exe'), '/nologo', '/c', '/safeseh', f'/Fo{obj / "reserve_430.obj"}',
                        str(RUN / 'reserve_430.asm')], capture_output=True, text=True, env=env, cwd=OUT)
    if r.returncode:
        return dict(compile_seconds=compile_s, compile_errors=1, first_errors=r.stdout.splitlines()[-5:])
    exe = OUT / 'PorscheLowered.exe'
    link_rsp = OUT / 'link.rsp'
    link_rsp.write_text('\n'.join(f'"{p}"' for p in sorted(obj.glob('*.obj'))), encoding='utf-8')
    # Based at the original's 0x00400000: reserve_430.obj holds the original image's pages.
    cmd = [str(link), '/nologo', '/MACHINE:X86', '/SUBSYSTEM:CONSOLE,5.01', '/MANIFEST:NO', '/BASE:0x400000', '/DYNAMICBASE:NO',
           '/FIXED', '/NXCOMPAT', '/LARGEADDRESSAWARE', '/STACK:0x200000,0x200000', f'/OUT:{exe}', f'/MAP:{OUT / "PorscheLowered.map"}', f'@{link_rsp}',
           'kernel32.lib', 'user32.lib']
    r = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=OUT)
    (OUT / 'link.log').write_text(r.stdout + r.stderr, encoding='utf-8')
    return dict(compiled_sources=len(sources), compile_seconds=compile_s, compile_errors=0, link_exit=r.returncode,
                link_errors=[ln for ln in r.stdout.splitlines() if 'error' in ln][:10],
                exe_bytes=exe.stat().st_size if exe.exists() else 0)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--generate-only', action='store_true')
    ap.add_argument('--build-only', action='store_true')
    ap.add_argument('--jobs', type=int, default=os.cpu_count() or 4)
    args = ap.parse_args()
    data = PE_PATH.read_bytes()
    assert hashlib.sha256(data).hexdigest() == PE_SHA
    img = Image(data)
    entries = [json.loads(ln) for ln in CATALOG.read_text(encoding='utf-8').splitlines() if ln.strip()]
    result = dict(schema=1, run='430-lowered-whole-game', original_sha256=PE_SHA, catalogued=len(entries))
    synthetic, pointers = pointer_entries(img, entries)
    result.update(pointer_targets=len(pointers), synthetic_functions=len(synthetic))
    if not args.build_only:
        translate, header = backend()
        result.update(generate(translate, header, img, entries + synthetic, pointers))
    if not args.generate_only:
        result.update(build(args.jobs))
    print(json.dumps({k: v for k, v in result.items() if k != 'rejected'}, indent=1))
    (OUT / 'result.json').write_text(json.dumps(result, indent=1) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
