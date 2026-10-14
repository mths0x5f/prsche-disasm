"""Read-only export coverage/provenance audit; no pseudo-C rewriting."""
from collections import Counter
import hashlib,json,os,re,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[5]
OUT=ROOT/'iterations/v2/001-original-recovery/runs/179-ghidra-declarations'
EXPORT=OUT/'export'
CORPUS=ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=lambda p:[json.loads(t) for t in p.read_text(encoding='utf-8-sig').splitlines() if t.strip()]
functions=rows(EXPORT/'functions.jsonl');expected=rows(CORPUS/'functions.jsonl')
progress=json.loads((EXPORT/'progress.json').read_text());provenance=json.loads((EXPORT/'provenance.json').read_text(encoding='utf-8-sig'))
assert progress['complete'] and progress['attempted']==progress['total']==len(functions)==len(expected)==5772
assert not progress['program_changed_before'] and not progress['program_changed_after']
assert progress['failed_total']==progress['listing_declaration_errors']==progress['high_global_declaration_errors']==0
assert len({r['entry_va'] for r in functions})==5772
assert {r['entry_va'] for r in functions}=={r['entry_va'] for r in expected}
assert {r['export_identity_sha256'] for r in functions}=={provenance['capture_identity_sha256']}
assert {r['module_sha256'] for r in functions}=={progress['module_sha256']}
for pin in provenance['files']:assert sha(ROOT/pin['path'])==pin['sha256'],pin['path']
global_rows=rows(EXPORT/'globals.jsonl');conflicts=rows(EXPORT/'conflicts.jsonl')
assert len(global_rows)==progress['high_global_identities']
assert len(conflicts)==sum(r['conflict'] for r in global_rows)==progress['high_global_conflicts']
assert sum(len(v['consumer_vas']) for r in global_rows for v in r['variants'])==progress['high_global_occurrences']
raw=(CORPUS/'decompiled.c').read_text();markers=list(re.finditer(r'/\* VA ([0-9a-fA-F]+) \*/',raw));by_va={r['entry_va']:r for r in functions}
signature_mismatches=[];global_name_gaps=[]
for i,m in enumerate(markers):
    text=raw[m.end():markers[i+1].start() if i+1<len(markers) else len(raw)]
    clean=re.sub(r'/\*.*?\*/|//[^\n]*','',text,flags=re.S).strip();va=m[1].lower();f=by_va[va]
    signature=clean.split('{',1)[0].strip().rstrip(';')
    if re.sub(r'\s+','',signature)!=re.sub(r'\s+','',f['inferred_signature'].rstrip(';')):signature_mismatches.append(va)
    tokens=set(re.findall(r'\b(?:_?(?:DAT|PTR|LAB|IMAGE|JUMPTABLE)_[A-Za-z0-9_$]+|(?:switchdataD|switchD)_[A-Za-z0-9_$]+|[su]_[A-Za-z0-9_$]+)\b',clean))
    names={g.get('name') for g in f['globals']};missing=sorted(tokens-names)
    if missing:global_name_gaps.append({'va':va,'tokens':missing})
probe=(ROOT/'local/experiments/v2-declarations-179')/'types_probe.cpp';probe.write_text('#include "'+(EXPORT/'types.h').as_posix()+'"\n',encoding='utf8')
compiler=ROOT/'local/tools/BuildTools/VC/Tools/MSVC/14.44.35207/bin/Hostx64/x86/cl.exe'
check=subprocess.run([str(compiler),'/nologo','/Zs','/TP','/W3',str(probe)],capture_output=True,text=True,encoding='utf8',errors='replace',env={**os.environ,'VSLANG':'1033'})
log=(ROOT/'local/experiments/v2-declarations-179')/'types_probe.log';log.write_text(check.stdout+check.stderr,encoding='utf8')
summary={'schema':2,'module_sha256':progress['module_sha256'],'export_identity_sha256':provenance['export_identity_sha256'],'coverage_passed':True,'function_records':len(functions),'status_counts':dict(Counter(r['status'] for r in functions)),'calling_conventions':dict(Counter(r['inferred_calling_convention'] for r in functions)),'this_pointer_functions':sum(r['this_pointer'] for r in functions),'vararg_functions':sum(r['varargs'] for r in functions),'global_declaration_occurrences':progress['high_global_occurrences'],'global_identities':len(global_rows),'global_conflicts':len(conflicts),'unambiguous_header_globals':progress['high_global_header_declarations'],'signature_matches_frozen_corpus':len(functions)-len(signature_mismatches),'signature_mismatch_vas':signature_mismatches,'corpus_address_token_gaps_functions':len(global_name_gaps),'corpus_address_token_gaps':global_name_gaps,'native_type_header_probe':{'compiler':str(compiler.relative_to(ROOT)),'compiler_sha256':sha(compiler),'exit_code':check.returncode,'log':str(log.relative_to(ROOT)),'log_sha256':sha(log),'diagnostic_counts':dict(Counter(re.findall(r'\b(?:error|warning) (C\d+)',check.stdout+check.stderr)))},'artifacts':{p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(EXPORT.iterdir()) if p.is_file()},'boundary':'Native Ghidra declarations and observed inference only; conflicts/printed aliases/host type and ABI lowering remain explicit. No definitions, guessed bodies, linking, execution or behavior acceptance.'}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in summary.items() if k not in ('artifacts','corpus_address_token_gaps','signature_mismatch_vas')},indent=2))
