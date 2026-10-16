"""Preserve failed Run259 link, then repair only its private fixture TU."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'local/experiments/v2-canonical-reuse-259'
OBJ=OUT/'objects'
DEPS=OUT/'dependencies'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save_receipt(path,value):path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')

def main():
    original=json.loads((OUT/'compile.execution.json').read_bytes())
    failed=json.loads((OUT/'fixture-link.execution.json').read_bytes())
    assert original['exit_code']==0 and failed['exit_code']!=0
    assert not (OUT/'fixture-repair-compile.execution.json').exists()
    protected=[OBJ/(name+'.obj') for name in ('0059f050','005a66a7','binding_0059f050','binding_005a66a7')]
    before={str(p):sha(p) for p in protected}
    fixture=OUT/'native-fixture.cpp'
    old=fixture.read_text(encoding='utf8')
    assert old.count('void __cdecl FUN_0059f050(unsigned int);')==1
    shutil.copyfile(fixture,OUT/'first-native-fixture.cpp')
    shutil.copyfile(OBJ/'native-fixture.obj',OUT/'first-native-fixture.obj')
    for name in ('fixture-link.execution.json','fixture-link.log'):
        shutil.copyfile(OUT/name,OUT/('first-'+name))
    fixture.write_text(old.replace('void __cdecl FUN_0059f050(unsigned int);','void __cdecl FUN_0059f050(int);'),encoding='utf8',newline='\n')
    assert sha(ROOT/'scripts/research/experiment-v2-canonical-reuse-259.py')
    command=original['command']
    compiler=command[0]
    include_at=command.index('/I')
    includes=command[include_at:-6]
    assert command[-6:]==[str(OBJ)+os.sep,str(OUT/'0059f050.cpp'),str(OUT/'005a66a7.cpp'),str(OUT/'binding_0059f050.cpp'),str(OUT/'binding_005a66a7.cpp'),str(fixture)] or command[-6:]==['/Fo'+str(OBJ)+os.sep,str(OUT/'0059f050.cpp'),str(OUT/'005a66a7.cpp'),str(OUT/'binding_0059f050.cpp'),str(OUT/'binding_005a66a7.cpp'),str(fixture)]
    command=[compiler,'/nologo','/c','/std:c++17','/Od','/Oi','/Gy','/GR-','/EHsc','/TP','/W4','/utf-8','/diagnostics:column','/MP6','/Zl','/GS-','/sourceDependencies',str(DEPS),*includes,'/Fo'+str(OBJ)+os.sep,str(fixture)]
    start=time.perf_counter()
    p=subprocess.run(command,cwd=OUT,env={**os.environ,'VSLANG':'1033','CL':'','_CL_':'','INCLUDE':''},capture_output=True,timeout=120)
    log=OUT/'fixture-repair-compile.log'
    log.write_bytes((p.stdout+p.stderr).replace(b'\r\n',b'\n'))
    receipt=dict(command=command,exit_code=p.returncode,seconds=round(time.perf_counter()-start,6),log='local/experiments/v2-canonical-reuse-259/fixture-repair-compile.log',log_sha256=sha(log),protected_object_sha256_before=before,protected_object_sha256_after={str(q):sha(q) for q in protected})
    save_receipt(OUT/'fixture-repair-compile.execution.json',receipt)
    assert p.returncode==0,log.read_text(errors='replace')
    assert receipt['protected_object_sha256_before']==receipt['protected_object_sha256_after']
    print(json.dumps(dict(exit_code=p.returncode,seconds=receipt['seconds'],protected_objects=4)))
if __name__=='__main__':main()
