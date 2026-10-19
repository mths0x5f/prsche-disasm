"""Batch export all 5,694 non-thunk functions of Porsche.exe to C++ source files.

Uses scripts/research/x86-cpp-backend-fpu.py to translate machine code directly
into clean, standalone C++ implementations organized by address space.
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

ROOT = Path(__file__).resolve().parents[2]
PE_PATH = ROOT / 'local/game/Porsche.exe'
PE_SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
CATALOG_PATH = ROOT / 'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl'
BACKEND_PATH = ROOT / 'scripts/research/x86-cpp-backend-fpu.py'
DEFAULT_OUT_DIR = ROOT / 'local/exported_cpp'


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
    parser.add_argument('--output-dir', type=Path, default=DEFAULT_OUT_DIR, help='Target directory for exported C++ files')
    parser.add_argument('--limit', type=int, default=0, help='Limit number of functions to export (0 = all)')
    parser.add_argument('--prefix', type=str, default='', help='Filter functions starting with specific hex prefix (e.g. 004b)')
    args = parser.parse_args()

    assert PE_PATH.exists(), f"Missing PE at {PE_PATH}"
    pe_bytes = PE_PATH.read_bytes()
    assert hashlib.sha256(pe_bytes).hexdigest() == PE_SHA, "PE SHA mismatch"
    get_bytes = pe_map(pe_bytes)

    spec = importlib.util.spec_from_file_location('backend', BACKEND_PATH)
    backend = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(backend)

    lines = CATALOG_PATH.read_text(encoding='utf-8').splitlines()
    entries = [json.loads(line) for line in lines if line.strip()]

    evaluable = []
    for e in entries:
        if e.get('is_thunk'):
            continue
        if len(e.get('ranges', [])) != 1:
            continue
        va = e['entry_va']
        if args.prefix and not va.startswith(args.prefix):
            continue
        evaluable.append(e)

    if args.limit > 0:
        evaluable = evaluable[:args.limit]

    out_dir = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Exporting {len(evaluable)} C++ functions to {out_dir}...")
    t0 = time.time()
    exported_count = 0
    total_bytes = 0

    manifest = []

    for idx, e in enumerate(evaluable):
        va = e['entry_va']
        body_len = e['body_bytes']
        start = int(va, 16)
        raw = get_bytes(start, body_len)

        # Organize by subfolder based on first 4 hex digits (e.g. 004b, 0053)
        folder = out_dir / va[:4]
        folder.mkdir(exist_ok=True)
        file_path = folder / f"{va}.cpp"

        cpp_code, witness = backend.translate(raw, start)
        file_path.write_text(cpp_code, encoding='utf-8')

        exported_count += 1
        total_bytes += len(cpp_code.encode('utf-8'))
        manifest.append({
            'va': va,
            'name': e.get('name', f'FUN_{va}'),
            'body_bytes': body_len,
            'cpp_bytes': len(cpp_code),
            'rel_path': f"{va[:4]}/{va}.cpp"
        })

        if (idx + 1) % 500 == 0 or (idx + 1) == len(evaluable):
            elapsed = time.time() - t0
            print(f"Progress: {idx + 1}/{len(evaluable)} exported ({total_bytes / (1024*1024):.2f} MB written) [{elapsed:.1f}s]...", flush=True)

    elapsed = time.time() - t0
    manifest_path = out_dir / 'manifest.json'
    manifest_path.write_text(json.dumps({
        'total_exported': exported_count,
        'total_cpp_bytes': total_bytes,
        'elapsed_seconds': round(elapsed, 2),
        'functions': manifest
    }, indent=2), encoding='utf-8')

    print(f"\nSUCCESS: Exported {exported_count} functions ({total_bytes / (1024*1024):.2f} MB) in {elapsed:.2f}s.")
    print(f"Manifest written to: {manifest_path}")


if __name__ == '__main__':
    main()
