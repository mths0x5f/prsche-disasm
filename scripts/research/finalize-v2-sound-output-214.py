"""Correct native RET metadata from saved214 disassembly; no tool execution."""
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/214-sound-output-consumer'
OUT=ROOT/'local/experiments/v2-sound-output-consumer-214'
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    path=RUN/'summary.json';raw=path.read_bytes();summary=json.loads(raw)
    assert 'metadata_finalization'not in summary,'preserve completed metadata finalization'
    for name,expected in summary['input_sha256'].items():
        p=Path(name);p=p if p.is_absolute()else ROOT/p
        assert digest(p)==expected,('input drift',name)
    saved=OUT/'captured-summary.json';driver=OUT/'captured-driver.py'
    assert not saved.exists()and not driver.exists()
    saved.write_bytes(raw)
    original_driver=ROOT/'scripts/research/experiment-v2-sound-output-214.py'
    driver.write_bytes(original_driver.read_bytes())
    row=summary['results'][0];asm=(ROOT/row['disassembly']).read_text(encoding='utf8')
    body=asm.split('\n?signed_bits214',1)[0]
    returns=re.findall(r'\bret(?:\s+([0-9A-Fa-f]+)h?)?\s*\n',body,re.I)
    assert returns==['']
    proof=json.loads((RUN/'proof-before-compile.json').read_text())
    original=[p for p in proof['original_instructions']if p['instruction'].startswith('RET')]
    assert len(original)==3 and all(p['bytes']=='c3'for p in original)
    old_value=row['native_ret_bytes'];row['native_ret_bytes']=[0]
    row['native_ret_site_count']=len(returns);row['original_ret_path_count']=len(original)
    for p in (saved,driver,Path(__file__)):
        summary['input_sha256'][p.resolve().relative_to(ROOT).as_posix()]=digest(p)
    summary['metadata_finalization']=dict(captured_summary=saved.relative_to(ROOT).as_posix(),captured_summary_sha256=digest(saved),
        captured_driver=driver.relative_to(ROOT).as_posix(),captured_driver_sha256=digest(driver),
        corrected_field='native_ret_bytes',previous_value=old_value,current_value=[0],original_RET0_paths=3,native_RET0_epilogues=1,
        compiler_link_native_Ghidra_commands=0,compiled_source_and_object_unchanged=True)
    for name,expected in summary['input_sha256'].items():
        p=Path(name);p=p if p.is_absolute()else ROOT/p
        assert digest(p)==expected,('input mutation',name)
    path.write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(summary['metadata_finalization']))


if __name__=='__main__':main()
