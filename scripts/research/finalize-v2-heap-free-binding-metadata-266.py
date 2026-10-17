"""Pin observed include-root metadata for Run266 without recompiling or linking."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/266-heap-free-binding'
OUT=ROOT/'local/experiments/v2-heap-free-binding-266'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):
 p=Path(p).resolve();return p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else p.as_posix()
def main():
 path=RUN/'summary.json';s=json.loads(path.read_bytes());receipt=json.loads((OUT/'compile.execution.json').read_bytes())
 assert receipt['exit_code']==0 and s['compiler_command']==receipt['command'] and s['native_fixture']['exit_code']==0
 roots=[Path(receipt['command'][i+1]).resolve() for i,x in enumerate(receipt['command'][:-1]) if x=='/I']
 assert len(roots)==5 and all(x.is_dir() for x in roots)
 row=s['support_objects'][0];assert row['generated_source']==rel(OUT/'binding.cpp')
 dep=OUT/'dependencies/binding.cpp.json';assert dep.exists()
 row.update(include_directories=[rel(x) for x in roots],compiler_command=receipt['command'],compiler_execution_receipt=rel(OUT/'compile.execution.json'),source_dependencies=rel(dep),source_dependencies_sha256=sha(dep))
 for p in [ROOT/'scripts/research/experiment-v2-heap-free-binding-266.py',Path(__file__),dep]:s['input_sha256'][rel(p)]=sha(p)
 path.write_text(json.dumps(s,indent=2)+'\n',encoding='utf8',newline='\n')
 print(json.dumps(dict(include_roots=len(roots),summary_sha256=sha(path))))
if __name__=='__main__':main()
