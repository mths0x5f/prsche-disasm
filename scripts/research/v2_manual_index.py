"""SHA-guarded supplementary function index for callbacks missed by Ghidra."""
import hashlib
import json
from pathlib import Path
from v2_proof_cache import ProofCache

ROOT=Path(__file__).resolve().parents[2]
INDEX=ROOT/'research/binary-index/manual-functions.jsonl'

def records(sha=None):
    rows=[json.loads(l) for l in INDEX.read_text().splitlines()] if INDEX.exists() else []
    seen=set()
    cache=ProofCache()
    originals={}
    for row in rows:
        key=(row['sha256'],row['entry_va'])
        if key in seen:raise RuntimeError(f'Duplicate manual function {key}')
        seen.add(key)
        path=(ROOT/'local/game'/row['path']).resolve()
        data=cache.data(path)
        if path not in originals:originals[path]=hashlib.sha256(data).hexdigest()
        if originals[path]!=row['sha256']:raise RuntimeError('Manual index original SHA differs')
        body=data[row['file_offset']:row['file_offset']+row['body_bytes']]
        if hashlib.sha256(body).hexdigest()!=row['body_sha256']:raise RuntimeError('Manual index instruction bytes differ')
        start,end=map(lambda x:int(x,16),row['ranges'][0])
        terminal_ret=body[-1]==0xc3 or (len(body)>=3 and body[-3]==0xc2)
        if start!=int(row['entry_va'],16) or end-start+1!=row['body_bytes'] or not terminal_ret:
            raise RuntimeError('Invalid manual function range/RET')
    cache.check_stable()
    return [row for row in rows if sha is None or row['sha256']==sha]

if __name__=='__main__':print(json.dumps({'verified_manual_functions':len(records())}))
