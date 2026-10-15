"""Read-only relocation and consumer-bound RTTI graph inventory."""
import hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]
module=next(x for x in map(json.loads,(ROOT/'research/binary-index/static/binaries.jsonl').read_text().splitlines()) if x['file']=='Porsche.exe')
image=(ROOT/'local/game'/module['path']).read_bytes()
assert hashlib.sha256(image).hexdigest()=='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
def raw(va,n):
 return next(image[s['raw_offset']+va-0x400000-s['rva']:s['raw_offset']+va-0x400000-s['rva']+n] for s in module['sections'] if s['rva']<=va-0x400000 and va-0x400000+n<=s['rva']+s['raw_size'])
pending=[(a,'COL') for a in (0x5c98d0,0x5c5190,0x5c51d8,0x5c5228)];seen=set();lengths={'COL':20,'CHD':16,'BCD':24};records=[]
while pending:
 va,kind=pending.pop(0)
 if va in seen:continue
 seen.add(va)
 if kind=='TD':data=raw(va,8)+raw(va+8,128).split(b'\0',1)[0]+b'\0';words=struct.unpack('<2I',data[:8])
 else:
  n=lengths[kind] if kind in lengths else int(kind);data=raw(va,n);words=struct.unpack('<'+'I'*(n//4),data)
 rec={'va':f'{va:08x}','kind':kind,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'hex':data.hex(),'words':[f'{w:08x}' for w in words]}
 if kind=='TD':rec['name']=data[8:-1].decode('ascii')
 records.append(rec)
 if kind=='COL':pending.extend([(words[3],'TD'),(words[4],'CHD')])
 elif kind=='CHD':pending.append((words[3],str(words[2]*4)))
 elif kind=='BCD':pending.append((words[0],'TD'))
 elif kind!='TD':pending.extend((w,'BCD') for w in words)
for rec in records:print(rec['va'],rec['kind'],rec['bytes'],' '.join(rec['words']),rec.get('name',''))
(Path(__file__).parent/'graph-inventory.json').write_text(json.dumps(records,indent=2)+'\n')
