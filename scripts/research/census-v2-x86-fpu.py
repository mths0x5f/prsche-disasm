"""Bounded syntax census for the full ISA extension (x87 FPU, shifts, unary, mul/div, rep).

Evaluates the 85-body frozen frontier from Run 252 against scripts/research/x86-cpp-backend-fpu.py.
Asserts 100% coverage (85/85 bodies supported) with 0 regressions against Run 277.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
PE_SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
SOURCE252_REL = 'iterations/v2/001-original-recovery/runs/252-x86-cpp-coverage/summary.json'
CENSUS277_REL = 'iterations/v2/001-original-recovery/runs/277-x86-extended-integer/census.json'
CATALOG_REL = 'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl'
BACKEND_REL = 'scripts/research/x86-cpp-backend-fpu.py'


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
    args = parser.parse_args()

    pe_path = ROOT / 'local/game/Porsche.exe'
    source252_path = ROOT / SOURCE252_REL
    census277_path = ROOT / CENSUS277_REL
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
    s252 = json.loads(source252_path.read_text(encoding='utf-8'))
    c277 = json.loads(census277_path.read_text(encoding='utf-8'))

    cat = {}
    for line in catalog_path.read_text(encoding='utf-8-sig').splitlines():
        line = line.strip()
        if line:
            rec = json.loads(line)
            cat[rec['entry_va']] = rec

    old277_supported = {r['va'] for r in c277['rows'] if r.get('classification') == 'syntax_supported'}

    results = []
    supported = []
    rejected = []

    for q in s252['rows']:
        va = q['va']
        c = cat[va]
        ranges = c['ranges']
        start, end = (int(z, 16) for z in ranges[0])
        raw = pe_bytes(start, end - start + 1)
        expected_sha = q['body_sha256']
        actual_sha = hashlib.sha256(raw).hexdigest()
        assert actual_sha == expected_sha, f'Body {va} SHA mismatch'

        try:
            code, witness = backend.translate(raw, start)
            supported.append(va)
            results.append({
                'va': va,
                'classification': 'syntax_supported',
                'body_sha256': actual_sha,
                'code_bytes': len(code),
                'instruction_count': len(witness['instructions']) if isinstance(witness, dict) and 'instructions' in witness else 0
            })
        except Exception as e:
            rejected.append((va, str(e)))
            results.append({
                'va': va,
                'classification': 'syntax_rejected',
                'body_sha256': actual_sha,
                'error': str(e)
            })

    regressions = [va for va in old277_supported if va not in supported]

    summary = {
        'total_bodies': len(s252['rows']),
        'syntax_supported': len(supported),
        'syntax_rejected': len(rejected),
        'baseline_277_supported': len(old277_supported),
        'regressions': len(regressions),
        'coverage_ratio': len(supported) / len(s252['rows']) if s252['rows'] else 0.0,
        'rows': results
    }

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"Total frontier bodies: {summary['total_bodies']}")
        print(f"Baseline 277 supported: {summary['baseline_277_supported']} / {summary['total_bodies']}")
        print(f"FPU + Full ISA supported: {summary['syntax_supported']} / {summary['total_bodies']} ({summary['coverage_ratio'] * 100:.1f}%)")
        print(f"Regressions against Run 277: {summary['regressions']}")
        if rejected:
            print(f"\nRemaining rejections ({len(rejected)}):")
            for va, err in rejected[:10]:
                print(f"  {va}: {err}")
        else:
            print("\n100% of census bodies successfully lowered to C++!")

    if len(rejected) > 0 or len(regressions) > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
