"""UNVALIDATED WIP280; no native replacement packet has been exercised.
Strict COFF boundaries for data, link directives and modern Win32 providers."""
import hashlib
from pathlib import Path
import re
import struct


def validate(kind, row, symbols, obj, root, pins):
    raw = Path(obj).read_bytes()
    machine, count = struct.unpack_from('<HH',raw)
    assert machine == 0x14c, 'Native support must be i386 COFF'
    optional = struct.unpack_from('<H',raw,16)[0]
    code = []
    for n in range(count):
        p = 20+optional+n*40
        size = struct.unpack_from('<I',raw,p+16)[0]
        flags = struct.unpack_from('<I',raw,p+36)[0]
        if size and flags & (0x20|0x20000000):
            code.append(n+1)
    if kind != 'native-platform-provider':
        assert not code, 'Data/binding support cannot contain executable sections'
        assert all(re.fullmatch(r'\?[^@]+(?:@[^@]+)*@@3.*',n) for n in symbols['defined']), 'Function in data support'
        return {'kind':kind,'code_sections':[]}
    assert code and not symbols['common'] and not symbols['weak'], 'Platform provider requires ordinary code definitions'
    contracts = row['platform_contracts']
    assert contracts and len({c['symbol'] for c in contracts}) == len(contracts)
    for c in contracts:
        is_stdcall=bool(re.fullmatch(r'\?platform_[a-z_]+@porsche@@YG.*',c['symbol']))
        is_error_adapter=c['symbol']=='?file_set_last_error@porsche@@YAXI@Z'
        assert is_stdcall or is_error_adapter, 'Only declared SDK adapters allowed'
        if is_error_adapter:
            assert c['sdk_import']=='__imp__SetLastError@4' and c['original_iat_va']=='005b21a4'
        assert c['module'] == 'KERNEL32.dll'
        assert re.fullmatch(r'__imp__[A-Za-z][A-Za-z0-9]+@\d+',c['sdk_import'])
        assert re.fullmatch(r'[0-9a-f]{8}',c['original_iat_va'])
    assert set(symbols['defined']) == {c['symbol'] for c in contracts}, 'Unexpected platform definitions'
    assert set(symbols['undefined']) == {c['sdk_import'] for c in contracts}, 'Unexpected platform dependencies'
    canonical = (root/row['platform_source']).resolve()
    assert canonical.is_relative_to(root/'iterations/v2/001-original-recovery/source/platform')
    assert canonical in pins, 'Platform source absent from closure'
    source = canonical.read_bytes()
    assembled = []
    for part in row['platform_source_parts']:
        if 'literal' in part:
            assert part == {'literal':part['literal']} and part['literal'] in ('namespace porsche {\n','}\n')
            assembled.append(part['literal'].encode())
        else:
            assert part['length'] > 0 and part['offset'] >= 0
            piece = source[part['offset']:part['offset']+part['length']]
            assert len(piece) == part['length'] and hashlib.sha256(piece).hexdigest() == part['sha256']
            assembled.append(piece)
    assert (root/row['generated_source']).read_bytes() == b''.join(assembled), 'Platform source changed instead of reused'
    return {'kind':kind,'code_sections':code,'platform_contracts':contracts}
