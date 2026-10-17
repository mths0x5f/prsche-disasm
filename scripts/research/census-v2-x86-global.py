"""Global syntax census across all 5,772 functions of Porsche.exe.

Evaluates the complete binary catalog against scripts/research/x86-cpp-backend-fpu.py.
Measures total real-world coverage, generated C++ volume, and categorizes remaining
unsupported opcodes across the entire original game binary.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import struct
import sys
import time
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
PE_SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
CATALOG_REL = 'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl'
BACKEND_REL = 'scripts/research/x86-cpp-backend-fpu.py'
OUTPUT_DIR = ROOT / 'local/experiments/v2-x86-global-census'


def digest(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def pe_map(data):
    pe = struct.unpack_from('<I', data, 0x3c)[0]
    n = struct.unpack_from('<H', data, pe + 6)[0]
    oh = struct.unpack_from('<H', data, pe + 20)[0]
    base = struct.unpack_from('<I', data, pe + 24 + 28)[0]
    sh = pe + 24 + oh
    ss = []
    for i in range(n):
        q = sh + 40 * i
        name = data[q:q + 8].split(b'\0', 1)[0].decode('ascii')
        vs, va, raw, ptr = struct.unpack_from('<IIII', data, q + 8)
        ss.append((name, va, vs, raw, ptr))

    def get(va, size):
        r = va - base
        for name, sv, vsize, rsize, ptr in ss:
            if sv <= r and r + size <= sv + vsize and r + size <= sv + rsize:
                return data[ptr + r - sv:ptr + r - sv + size]
        raise ValueError(f'no raw body {va:08x}+{size}')

    return get


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true', help='Output JSON summary')
    parser.add_argument('--limit', type=int, default=0, help='Limit number of functions to evaluate (0 = all)')
    args = parser.parse_args()

    pe_path = ROOT / 'local/game/Porsche.exe'
    catalog_path = ROOT / CATALOG_REL
    backend_path = ROOT / BACKEND_REL

    if not pe_path.exists():
        raise FileNotFoundError(f'Missing game executable: {pe_path}')
    if digest(pe_path) != PE_SHA:
        raise ValueError(f'Game PE SHA mismatch: {pe_path}')

    spec = importlib.util.spec_from_file_location('backend_fpu', backend_path)
    backend = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(backend)

    pe_bytes = pe_map(pe_path.read_bytes())

    all_functions = []
    for line in catalog_path.read_text(encoding='utf-8-sig').splitlines():
        line = line.strip()
        if line:
            all_functions.append(json.loads(line))

    total_catalog = len(all_functions)
    thunks = [f for f in all_functions if f.get('thunk')]
    multi_range = [f for f in all_functions if not f.get('thunk') and len(f.get('ranges', [])) > 1]
    evaluable = [f for f in all_functions if not f.get('thunk') and len(f.get('ranges', [])) == 1]

    if args.limit > 0:
        evaluable = evaluable[:args.limit]

    supported = []
    rejected = []
    rejection_reasons = Counter()
    total_x86_bytes = 0
    total_cpp_bytes = 0

    t0 = time.time()
    for idx, fn in enumerate(evaluable):
        va = fn['entry_va']
        start, end = (int(z, 16) for z in fn['ranges'][0])
        body_len = end - start + 1
        total_x86_bytes += body_len

        try:
            raw = pe_bytes(start, body_len)
            cpp_code, witness = backend.translate(raw, start)
            cpp_len = len(cpp_code)
            total_cpp_bytes += cpp_len
            supported.append({
                'va': va,
                'name': fn.get('name', f'FUN_{va}'),
                'x86_bytes': body_len,
                'cpp_bytes': cpp_len,
                'instructions': len(witness['instructions']) if isinstance(witness, dict) and 'instructions' in witness else 0
            })
        except Exception as e:
            err_msg = str(e)
            family = err_msg.split(': ')[-1].split(' ')[0]
            if family.startswith("'") and family.endswith("'"):
                family = family.strip("'")
            rejection_reasons[family] += 1
            rejected.append({
                'va': va,
                'name': fn.get('name', f'FUN_{va}'),
                'x86_bytes': body_len,
                'error': err_msg,
                'reason_family': family
            })

        if not args.json and (idx + 1) % 500 == 0:
            elapsed = time.time() - t0
            print(f'Progress: {idx + 1}/{len(evaluable)} functions evaluated ({len(supported)} ok, {len(rejected)} err) [{elapsed:.1f}s]...', flush=True)

    dur = time.time() - t0
    coverage_pct = (len(supported) / len(evaluable) * 100.0) if evaluable else 0.0

    summary = {
        'total_catalog_functions': total_catalog,
        'thunk_functions': len(thunks),
        'multi_range_functions': len(multi_range),
        'evaluated_functions': len(evaluable),
        'syntax_supported': len(supported),
        'syntax_rejected': len(rejected),
        'coverage_percentage': round(coverage_pct, 2),
        'duration_seconds': round(dur, 2),
        'total_x86_bytes_evaluated': total_x86_bytes,
        'total_cpp_bytes_generated': total_cpp_bytes,
        'top_rejection_reasons': rejection_reasons.most_common(20)
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print('\n' + '=' * 60)
        print('       GLOBAL CENSUS REPORT: Porsche.exe (All Functions)')
        print('=' * 60)
        print(f"Total catalog functions:       {total_catalog}")
        print(f"  - Thunk / JMP wrappers:      {len(thunks)}")
        print(f"  - Multi-range bodies:        {len(multi_range)}")
        print(f"  - Evaluated normal bodies:   {len(evaluable)}")
        print('-' * 60)
        print(f"Syntax Supported (Lowered):    {len(supported)} / {len(evaluable)} ({coverage_pct:.2f}%)")
        print(f"Syntax Rejected:               {len(rejected)} / {len(evaluable)} ({100.0 - coverage_pct:.2f}%)")
        print(f"Evaluation time:               {dur:.2f}s ({len(evaluable)/dur:.1f} funcs/sec)")
        print(f"X86 machine code evaluated:    {total_x86_bytes:,} bytes")
        print(f"C++ source code generated:     {total_cpp_bytes:,} bytes")
        print('-' * 60)
        print("Top Remaining Rejection Families:")
        for reason, count in rejection_reasons.most_common(12):
            pct = count / len(evaluable) * 100.0
            print(f"  {reason:<22} : {count:>5} functions ({pct:>4.1f}%)")
        print('=' * 60)
        print(f"Detailed summary saved to: local/experiments/v2-x86-global-census/summary.json\n")


if __name__ == '__main__':
    main()
