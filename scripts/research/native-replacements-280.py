"""UNVALIDATED WIP280; no native replacement packet has been exercised.
Explicit, identity-pinned replacements; frozen parent packets stay unchanged."""
import re


def apply(rows, packets, validated):
    original = {r['va']:r for r in rows}
    assert len(original)==len(rows),'Duplicate input VA before replacement'
    replacement={};proof=[]
    for packet in packets:
        assert packet['kind']=='original-caller-contract-repair'
        selected=packet['results']
        assert selected and len(selected)==packet['objects_compiled']
        for row in selected:
            va=row['va']
            assert re.fullmatch(r'[0-9a-f]{8}',va) and va in original,'Unknown replacement VA'
            assert va not in replacement,'Duplicate/chained replacement VA'
            assert validated(row),'Uncompiled replacement'
            old=original[va];expected=row['replaces']
            for key in ('object','object_sha256','generated_source','generated_source_sha256'):
                assert expected[key]==old[key],('Old native identity mismatch',va,key)
            assert row['object']!=old['object'] and row['generated_source']!=old['generated_source']
            assert row['object_sha256']!=old['object_sha256'],'Replacement reuses old code'
            replacement[va]=row
            proof.append(dict(va=va,old=expected,new={k:row[k] for k in expected}))
    return [replacement.get(r['va'],r) for r in rows],proof
