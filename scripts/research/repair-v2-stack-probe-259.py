"""Repair only Run259 fixture EBP probe after archived native access violation."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'local/experiments/v2-canonical-reuse-259'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    receipt=json.loads((OUT/'fixture-repair-compile.execution.json').read_bytes())
    crash=json.loads((OUT/'fixture-native.execution.json').read_bytes())
    assert receipt['exit_code']==0 and crash['exit_code']==3221225477
    assert not (OUT/'first-fixture-repair-compile.execution.json').exists()
    protected=[OUT/'objects'/(n+'.obj') for n in ('0059f050','005a66a7','binding_0059f050','binding_005a66a7')]
    before={str(p):sha(p) for p in protected}
    for name in ('fixture-repair-compile.execution.json','fixture-repair-compile.log','fixture-native.execution.json','fixture-native.log'):
        shutil.copyfile(OUT/name,OUT/('first-'+name))
    fixture=OUT/'native-fixture.cpp'
    shutil.copyfile(fixture,OUT/'second-native-fixture.cpp')
    shutil.copyfile(OUT/'objects/native-fixture.obj',OUT/'second-native-fixture.obj')
    spec=importlib.util.spec_from_file_location('driver259',ROOT/'scripts/research/experiment-v2-canonical-reuse-259.py')
    driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)
    fixture.write_text(driver.FIXTURE,encoding='utf8',newline='\n')
    command=receipt['command']
    assert command[-1]==str(fixture) and '/GS-' in command
    start=time.perf_counter()
    p=subprocess.run(command,cwd=OUT,env={**os.environ,'VSLANG':'1033','CL':'','_CL_':'','INCLUDE':''},capture_output=True,timeout=120)
    log=OUT/'fixture-repair-compile.log';log.write_bytes((p.stdout+p.stderr).replace(b'\r\n',b'\n'))
    new=dict(command=command,exit_code=p.returncode,seconds=round(time.perf_counter()-start,6),log='local/experiments/v2-canonical-reuse-259/fixture-repair-compile.log',log_sha256=sha(log),protected_object_sha256_before=before,protected_object_sha256_after={str(q):sha(q) for q in protected})
    (OUT/'fixture-repair-compile.execution.json').write_text(json.dumps(new,indent=2)+'\n',encoding='utf8',newline='\n')
    assert p.returncode==0,log.read_text(errors='replace')
    assert new['protected_object_sha256_before']==new['protected_object_sha256_after']
    print(json.dumps(dict(exit_code=p.returncode,seconds=new['seconds'],protected_objects=4)))
if __name__=='__main__':main()
