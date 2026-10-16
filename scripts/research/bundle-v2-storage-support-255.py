"""Bundle validated data-only packets for the frozen native collector; no native tools."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
relative=lambda p:Path(p).resolve().relative_to(ROOT).as_posix() if Path(p).resolve().is_relative_to(ROOT) else str(Path(p).resolve())
resolve=lambda p:(Path(p) if Path(p).is_absolute() else ROOT/p).resolve()


def main(args):
    run=resolve(args.run);assert not (run/'summary.json').exists(),'completed bundle immutable'
    pins={};rows=[];sources=[];compiler_hashes=set();ids=set()
    def pin(path,h=None):
        path=resolve(path);actual=digest(path);assert h is None or h==actual,('input drift',path)
        key=relative(path);assert key not in pins or pins[key]==actual;pins[key]=actual;return path
    pin(__file__)
    parser=pin('scripts/research/build-v2-compile-corpus.py')
    spec=importlib.util.spec_from_file_location('coff255',parser);coff=importlib.util.module_from_spec(spec);spec.loader.exec_module(coff)
    for name in args.support_summary:
        path=pin(name);s=json.loads(path.read_bytes());validation=pin(path.parent/'validation.json');v=json.loads(validation.read_bytes())
        assert v['summary_sha256']==digest(path) and (v.get('passed') or v.get('status')=='PASS')
        assert s['kind']=='original-writable-data' and s['original_sha256']==SHA
        manifest={resolve(p):h for p,h in s['input_sha256'].items()}
        for p,h in manifest.items():pin(p,h)
        captured=s['compiled'];assert captured['exit_code']==0
        compiler=resolve(captured['command'][0]);assert compiler.name.lower()=='cl.exe' and compiler in manifest
        compiler_hashes.add(manifest[compiler])
        receipts=[]
        for p in manifest:
            if p.name.endswith('.execution.json'):
                value=json.loads(p.read_bytes())
                if value.get('command')==captured['command'] and value.get('exit_code')==0:receipts.append(relative(p))
        if not receipts:
            # Source packets embed this entire observed receipt as `compiled`.
            # Pin the durable file as well, requiring exact parsed equality.
            receipt=pin(resolve(captured['log']).parent/'compile.execution.json')
            assert json.loads(receipt.read_bytes())==captured,'Durable compiler receipt differs from captured source report'
            receipts.append(relative(receipt))
        assert len(receipts)==1,'Exactly one actual successful compiler receipt required'
        for row in s['support_objects']:
            assert row['id'] not in ids and row['compiler_exit_code']==0 and row['compiled'] is True
            ids.add(row['id']);obj=pin(row['object'],row['object_sha256'])
            assert coff.coff_symbols(obj)==row['symbols'] and not row['symbols']['undefined']
            assert all(n.startswith('?DAT_') and '@@3' in n for n in row['symbols']['defined'])
            rows.append(row)
        sources.append(dict(summary=relative(path),summary_sha256=digest(path),validation=relative(validation),compiler_receipt=receipts[0],
                            compiler_sha256=manifest[compiler],actual_source_compiler_batches=s['actual_compiler_batches']))
    assert len(compiler_hashes)==1 and rows
    for p,h in pins.items():assert digest(resolve(p))==h,('final drift',p)
    run.mkdir(parents=True,exist_ok=True)
    result=dict(schema=1,kind='original-writable-data',original_sha256=SHA,compiler_sha256=next(iter(compiler_hashes)),support_objects=rows,
        functions_added=0,source_packets=sources,input_sha256=pins,actual_compiler_batches_in_source_packets=sum(s['actual_source_compiler_batches']for s in sources),
        actual_compiler_commands_this_pass=0,actual_link_commands_this_pass=0,actual_native_commands_this_pass=0,
        limits=['Metadata adapter only; compiler identity derived from each recorded input and exact successful receipt.',
                'Original source packets, individual compiler receipts and COFF bytes preserved; no invented composite compiler exit or batch.',
                'All original data-layout/alias/lifetime/gameplay limitations remain in the source packets.'])
    (run/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
    (run/'validation.json').write_text(json.dumps(dict(passed=True,summary_sha256=digest(run/'summary.json'),source_packets=len(sources),support_objects=len(rows),guarded_inputs=len(pins),compiler_identity_receipts=len(sources),native_commands=0),indent=2)+'\n',encoding='utf8',newline='\n')
    (run/'README.md').write_text('''# Run255 — compatible original data support bundle

Frozen250/254 packets record the actual compiler command/hash in their closures rather than the collector's top-level compiler_sha256 field. This adapter checks each pinned successful receipt, input closure and actual COFF, then exposes the same two data-only objects in the existing241 interface. Source packets remain unchanged.
No compiler, linker or native execution occurs here. Two source compiler batches remain two recorded batches; no composite observed exit is fabricated. The first249 metadata preflight failed before any native archive/link command and is retained locally.

```powershell
py -3 scripts/research/bundle-v2-storage-support-255.py --support-summary iterations/v2/001-original-recovery/runs/250-writable-scalar-batch/summary.json --support-summary iterations/v2/001-original-recovery/runs/254-writable-scalar-batch/summary.json --run iterations/v2/001-original-recovery/runs/255-storage-support-bundle
```
''',encoding='utf8',newline='\n')
    print(json.dumps(dict(support_objects=len(rows),source_packets=len(sources),pins=len(pins),native_commands=0)))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--support-summary',action='append',required=True);p.add_argument('--run',required=True);main(p.parse_args())
