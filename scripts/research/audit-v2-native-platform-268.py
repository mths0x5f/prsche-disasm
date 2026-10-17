"""Read-only checks of exact reused SDK adapters and the observed native fixture."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

import capstone
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/268-native-platform-providers'
OUT=ROOT/'local/experiments/v2-native-platform-providers-268'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def mod(name,path):
 spec=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def main():
 s=load(RUN/'summary.json');assert s['kind']=='native-platform-provider' and s['new_game_functions']==0
 assert s['actual_compiler_batches']==s['actual_native_commands']==1
 driver=mod('driver268','scripts/research/experiment-v2-native-platform-268.py')
 helper=mod('contract268audit','scripts/research/native-platform-contract-268.py')
 coff=mod('coff268audit','scripts/research/build-v2-compile-corpus.py')
 oracle=mod('oracle268audit','scripts/research/audit-v2-nested-calls-229.py')
 union=mod('union268audit','scripts/research/audit-v2-native-union-268.py')
 pins={}
 for name,h in s['input_sha256'].items():
  p=Path(name);p=p if p.is_absolute() else ROOT/p;p=p.resolve()
  assert sha(p)==h,('pin',name);pins[p]=h
 assert s['compiler_sha256']==sha(s['compiler_command'][0])
 assert s['original_sha256']==driver.SHA==sha(ROOT/'local/game/Porsche.exe')
 assert (OUT/'native-fixture.cpp').read_bytes()==driver.FIXTURE.encode()
 row,=s['support_objects'];obj=ROOT/row['object'];symbols=coff.coff_symbols(obj)
 assert row['symbols']==symbols and row['platform_contracts']==driver.CONTRACTS
 helper.validate(s['kind'],row,symbols,obj,ROOT,pins)
 roots=union.recorded_include_roots(row,pins)
 assert len(roots)==5 and roots[0]==ROOT/'iterations/v2/001-original-recovery/source/include'
 dep=load(ROOT/row['source_dependencies'])
 assert dep['Version']=='1.2' and Path(dep['Data']['Source']).resolve()==ROOT/row['generated_source']
 assert all(Path(n).resolve() in pins for n in dep['Data']['Includes'])
 cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);cs.detail=True
 bodies=[]
 for c in row['platform_contracts']:
  raw,relocs=oracle.coff_function(obj,c['symbol']);ins=list(cs.disasm(raw,0x1000))
  calls=[i for i in ins if i.mnemonic=='call'];rets=[i for i in ins if i.mnemonic=='ret']
  assert len(calls)==len(rets)==1 and rets[0].operands[0].imm==4
  assert relocs==[dict(offset=calls[0].address-0x1000+2,symbol=c['sdk_import'],type=6)]
  assert calls[0].bytes[:2]==b'\xff\x15' and len(calls[0].bytes)==6
  bodies.append(dict(symbol=c['symbol'],code_bytes=len(raw),ret_pop=4,relocations=relocs))
 for name in ('compile-001','link-001','native-001'):
  r=load(OUT/(name+'.execution.json'));assert r['exit_code']==0 and r['cwd']==str(OUT)
  assert not re.search(rb'(?:warning|error) [CDL]\d+',(OUT/(name+'.log')).read_bytes())
 assert load(OUT/'compile-001.execution.json')['command']==s['compiler_command']
 assert '/MP6' in s['compiler_command'] and '/showIncludes' not in s['compiler_command']
 assert s['native_fixture']['recursive_cycles']==64 and s['native_fixture']['provider_calls']==256
 # Meaningful negative guards against widening support into game code or guessed providers.
 rejected=[]
 def reject(label,kind='native-platform-provider',r=None,sy=None):
  try:helper.validate(kind,r or row,sy or symbols,obj,ROOT,pins)
  except AssertionError:rejected.append(label)
  else:raise AssertionError(('unsafe support accepted',label))
 reject('code in writable-data','original-writable-data')
 reject('code in proven-binding','proven-link-contract')
 r=copy.deepcopy(row);r['platform_contracts'][0]['symbol']='?FUN_00531f90@@YAIH@Z';reject('recovered function disguised as platform',r=r)
 r=copy.deepcopy(row);r['platform_contracts'][0]['module']='Porsche.exe';reject('game DLL disguised as platform',r=r)
 r=copy.deepcopy(row);r['platform_source_parts'].append(dict(literal='int guessed(){return 0;}\n'));reject('invented source literal',r=r)
 r=copy.deepcopy(row);r['platform_source_parts'][0]['sha256']='0'*64;reject('canonical fragment drift',r=r)
 sy=copy.deepcopy(symbols);sy['defined'].append('?extra@@YAXXZ');reject('undeclared definition',sy=sy)
 sy=copy.deepcopy(symbols);sy['undefined'].append('?guessed_callee@@YAXXZ');reject('undeclared dependency',sy=sy)
 validation=dict(schema=1,summary_sha256=sha(RUN/'summary.json'),audit_source_sha256=sha(__file__),passed=True,
                 input_pins=len(pins),provider_bodies=bodies,exact_canonical_fragments=True,observed_include_order=True,
                 native_exit=0,recursive_cycles=64,provider_calls=256,negative_guards=rejected,new_game_functions=0,
                 limits='Valid Win32 recursive lock operations only; not contention/fault/game behavior.')
 (RUN/'validation.json').write_bytes((json.dumps(validation,indent=2)+'\n').encode())
 print(json.dumps(dict(passed=True,input_pins=len(pins),provider_bodies=len(bodies),negative_guards=len(rejected),native_exit=0)))


if __name__=='__main__':main()
