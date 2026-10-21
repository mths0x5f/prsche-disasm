"""Read-only PE/index evidence for006ad750; never supplies production storage."""
from __future__ import annotations

import argparse
import bisect
import hashlib
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'iterations/v2/001-original-recovery/runs/336-transform-cell-evidence'
CELL = 0x6ad750
SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rel(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def parse(image):
    pe = struct.unpack_from('<I', image, 0x3c)[0]
    assert image[pe:pe+4] == b'PE\0\0'
    opt = pe + 24
    assert struct.unpack_from('<H', image, opt)[0] == 0x10b
    base = struct.unpack_from('<I', image, opt + 28)[0]
    sections = []
    start = opt + struct.unpack_from('<H', image, pe + 20)[0]
    for i in range(struct.unpack_from('<H', image, pe + 6)[0]):
        offset = start + i * 40
        vsize, rva, raw_size, raw_offset = struct.unpack_from('<IIII', image, offset + 8)
        flags = struct.unpack_from('<I', image, offset + 36)[0]
        sections.append(dict(name=image[offset:offset+8].split(b'\0')[0].decode('latin1'),
                             rva=rva, virtual_size=vsize, raw_size=raw_size, raw_offset=raw_offset,
                             characteristics=f'{flags:08x}'))
    def read(va, n):
        for section in sections:
            delta = va - base - section['rva']
            if 0 <= delta and delta + n <= max(section['virtual_size'], section['raw_size']):
                available = max(0, min(n, section['raw_size'] - delta))
                return image[section['raw_offset']+delta:section['raw_offset']+delta+available] + bytes(n-available)
        raise ValueError(hex(va))
    def raw_to_va(offset):
        for section in sections:
            if section['raw_offset'] <= offset < section['raw_offset'] + section['raw_size']:
                return base + section['rva'] + offset - section['raw_offset'], section['name']
        return None, 'headers-or-unmapped-file-bytes'
    relocation_rva, relocation_size = struct.unpack_from('<II', image, opt + 96 + 5 * 8)
    relocations = []
    raw_reloc = read(base + relocation_rva, relocation_size) if relocation_rva else b''
    cursor = 0
    while cursor + 8 <= len(raw_reloc):
        page, size = struct.unpack_from('<II', raw_reloc, cursor)
        if not size:
            break
        assert size >= 8 and size % 2 == 0 and cursor + size <= len(raw_reloc)
        for offset in range(cursor+8, cursor+size, 2):
            entry = struct.unpack_from('<H', raw_reloc, offset)[0]
            if entry >> 12 == 3:
                site = base + page + (entry & 4095)
                relocations.append((site, struct.unpack('<I', read(site, 4))[0]))
        cursor += size
    return dict(base=base, sections=sections, relocations=relocations, read=read, raw_to_va=raw_to_va,
                entry=base+struct.unpack_from('<I', image, opt+16)[0],
                image_size=struct.unpack_from('<I', image, opt+56)[0],
                export_directory=struct.unpack_from('<II', image, opt+96),
                tls_directory=struct.unpack_from('<II', image, opt+96+9*8))


def occurrences(image, value, view):
    needle = struct.pack('<I', value)
    sites = {site for site, _ in view['relocations']}
    result = []
    cursor = 0
    while True:
        offset = image.find(needle, cursor)
        if offset < 0:
            return result
        va, section = view['raw_to_va'](offset)
        result.append(dict(file_offset=f'{offset:08x}', mapped_va=f'{va:08x}' if va is not None else None,
                           section=section, highlow_site=va in sites))
        cursor = offset + 1


def collect():
    inputs = {}
    def pin(path):
        path = Path(path)
        inputs[rel(path)] = digest(path)
        return path
    index_root = ROOT / 'research/binary-index/ghidra'
    binary_rows = [json.loads(line) for line in pin(ROOT / 'research/binary-index/static/binaries.jsonl').read_text().splitlines()]
    main = None
    modules = []
    scanned = {}
    for row in binary_rows:
        path = pin(ROOT / 'local/game' / row['path'])
        assert digest(path) == row['sha256'], row['path']
        if row['sha256'] not in scanned:
            image = path.read_bytes()
            view = parse(image)
            refs = [dict(site=f'{site:08x}', target=f'{target:08x}') for site, target in view['relocations'] if target == CELL]
            literals = occurrences(image, CELL, view)
            rva_literals = occurrences(image, CELL - 0x400000, view)
            containing = [section for section in view['sections'] if section['rva'] <= CELL-view['base'] < section['rva']+max(section['virtual_size'], section['raw_size'])]
            module = dict(paths=[], sha256=row['sha256'], preferred_image_base=f'{view["base"]:08x}',
                          highlow_entries=len(view['relocations']), exact_cell_highlow_targets=refs,
                          exact_cell_va_literal_occurrences=literals,
                          porsche_cell_rva_literal_occurrences=rva_literals,
                          numeric_va_maps_in_this_image=bool(containing),
                          containing_section_names=[x['name'] for x in containing],
                          export_count=len(row.get('exports', [])))
            scanned[row['sha256']] = module
            modules.append(module)
        scanned[row['sha256']]['paths'].append(row['path'])
        if row['file'] == 'Porsche.exe':
            assert row['sha256'] == SHA
            main = (path.read_bytes(), parse(path.read_bytes()))
    assert main is not None
    image, view = main
    section = next(s for s in view['sections'] if s['rva'] <= CELL-view['base'] < s['rva']+s['virtual_size'])
    cell_delta = CELL-view['base']-section['rva']
    assert cell_delta >= section['raw_size']
    assert view['read'](CELL, 4) == bytes(4)
    reloc_window = [dict(site=f'{site:08x}', target=f'{target:08x}') for site, target in view['relocations']
                    if CELL-0x50 <= target < CELL+0x30]
    target_sites = sorted(int(x['site'], 16) for x in reloc_window)
    found = {}
    listing = pin(ROOT / 'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm')
    for line in listing.open(encoding='utf8'):
        match = re.match(r'^([0-9a-fA-F]{8})\s+([0-9a-fA-F]+)\s+(.*)$', line)
        if not match:
            continue
        start = int(match[1], 16)
        count = len(match[2]) // 2
        i = bisect.bisect_left(target_sites, start)
        while i < len(target_sites) and target_sites[i] < start + count:
            site = target_sites[i]
            found[f'{site:08x}'] = dict(instruction_va=f'{start:08x}', bytes_hex=match[2].lower(), instruction=match[3])
            i += 1
    for entry in reloc_window:
        entry['indexed_instruction'] = found.get(entry['site'])
    references = []
    adjacent = []
    for path in sorted(index_root.glob('*/references.jsonl')):
        matches = []
        with path.open(encoding='utf8') as lines:
            for line in lines:
                if '006ad750' in line:
                    row = json.loads(line)
                    if row.get('to_va') == '006ad750':
                        matches.append(row)
        if matches:
            pin(path)
            references.append(dict(index=rel(path), references=matches,
                                   warning='Numeric address matches in a separate EXE are not inter-module writer relationships.'))
    ref_path = pin(index_root / 'Porsche.exe-ddd748fdbe6d/references.jsonl')
    for line in ref_path.open(encoding='utf8'):
        row = json.loads(line)
        value = row.get('to_va', '')
        if re.fullmatch('[0-9a-fA-F]{8}', value) and CELL-0x10 <= int(value, 16) < CELL+0x10:
            adjacent.append(row)
    symbols_path = pin(index_root / 'Porsche.exe-ddd748fdbe6d/symbols.jsonl')
    symbols = [row for line in symbols_path.read_text().splitlines() if (row := json.loads(line)).get('va')
               and re.fullmatch('[0-9a-fA-F]{8}', row['va']) and CELL-0x10 <= int(row['va'], 16) < CELL+0x10]
    coverage = json.loads(pin(ROOT / 'research/binary-index/coverage.json').read_text())
    # Keep the already-proven calling sequence separate from this storage scan.
    packet = pin(ROOT / 'iterations/v2/001-original-recovery/runs/327-resource-open-callback-evidence/evidence.json')
    existing = json.loads(packet.read_text())
    source_contract = existing['transform_cell']
    pin(Path(__file__))
    assert all(digest(ROOT / path) == expected for path, expected in inputs.items()), 'input drift'
    return dict(schema=1, original_sha256=SHA, cell_va='006ad750', cell_rva='002ad750',
                cell_bytes=4, pe_entry_va=f'{view["entry"]:08x}', pe_image_size=view['image_size'],
                section=section, cell_offset_in_section=f'{cell_delta:08x}', raw_file_backed=False,
                zero_fill_tail_start_va=f'{view["base"]+section["rva"]+section["raw_size"]:08x}',
                zero_fill_tail_end_exclusive_va=f'{view["base"]+section["rva"]+section["virtual_size"]:08x}',
                initial_bytes='00000000', relocation_at_cell=any(site == CELL for site, _ in view['relocations']),
                porsche_export_directory=list(view['export_directory']), porsche_tls_directory=list(view['tls_directory']),
                pe_scan_paths=len(binary_rows), pe_scan_unique_hashes=len(modules), modules=modules,
                exact_numeric_references_across_index=references,
                nearby_highlow_targets=reloc_window, nearby_symbols=symbols, nearby_indexed_references=adjacent,
                known_consumer=dict(instruction_va='00561d49', operand_va='00561d4a',
                    instruction='MOV EAX,[006ad750]',
                    transform_abi='void* __cdecl(void* buffer, const char* saved_path, uint32 saved_flags)',
                    call_va='00561d5c', caller_cleanup_bytes=12,
                    original_contract_packet=rel(packet), original_storage_observation=source_contract),
                coverage=dict(pe_paths=len(binary_rows), source_coverage_counts=coverage['counts'],
                    gaps=['indexed references do not cover all computed aliases, bulk writes or generated code',
                          'HIGHLOW scan covers stored absolute operands, not base-plus-offset calculations',
                          'raw constant matches are candidates, not proof of instruction/data semantics',
                          'separate executable numeric matches do not prove a shared runtime image']),
                accepted_storage_owner=None, complete_layout_proved=False, writer_coverage_complete=False,
                proposed_production_provider=None, production_storage_authorized=False,
                next_trace=dict(target_rva='002ad750',
                    method='From main-image mapping before initialization, watch all writes to loaded_image_base+002ad750 through startup and resource-open flows; record writer instruction/module/thread/old-new DWORD and containing write extent.',
                    consumer_breakpoints=['loaded_image_base+00161d49', 'loaded_image_base+00161d5c'],
                    acceptance_limit='No observed write in sampled runs is bounded runtime evidence, not a proof of immutable zero or complete ownership.'),
                input_sha256=inputs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', action='store_true')
    args = parser.parse_args()
    evidence = collect()
    path = RUN / 'evidence.json'
    if args.capture:
        RUN.mkdir(parents=True, exist_ok=True)
        assert not path.exists(), 'Completed evidence is immutable'
        path.write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf8', newline='\n')
    else:
        assert json.loads(path.read_text()) == evidence, 'Completed evidence changed'
    main_module = next(x for x in evidence['modules'] if 'Porsche.exe' in x['paths'])
    print(json.dumps(dict(passed=True, pe_paths=evidence['pe_scan_paths'],
                         unique_pe=evidence['pe_scan_unique_hashes'],
                         porsche_exact_highlow=main_module['exact_cell_highlow_targets'],
                         porsche_literal_occurrences=main_module['exact_cell_va_literal_occurrences'],
                         nearby_highlow=len(evidence['nearby_highlow_targets']), storage_provider=False)))


if __name__ == '__main__':
    main()
