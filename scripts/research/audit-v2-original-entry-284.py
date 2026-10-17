"""Bounded read-only original PE startup-chain and first-game-link audit."""
import hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/284-original-entry-audit'
SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def relative(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def load(p):return json.loads(Path(p).read_bytes())
def main():
 RUN.mkdir(parents=True,exist_ok=True)
 game=ROOT/'local/game/Porsche.exe';raw=game.read_bytes();assert digest(game)==SHA
 pe=struct.unpack_from('<I',raw,0x3c)[0];assert raw[pe:pe+4]==b'PE\0\0'
 entry_rva=struct.unpack_from('<I',raw,pe+24+16)[0];base=struct.unpack_from('<I',raw,pe+24+28)[0]
 assert base==0x400000 and base+entry_rva==0x5a2d1a
 n=struct.unpack_from('<H',raw,pe+6)[0];oh=struct.unpack_from('<H',raw,pe+20)[0]
 sections=[]
 for i in range(n):
  q=pe+24+oh+i*40
  sections.append((raw[q:q+8].split(b'\0')[0].decode(),*struct.unpack_from('<IIII',raw,q+8)))
 def bytes_at(va,size):
  rva=va-base
  matches=[raw[rp+rva-sva:rp+rva-sva+size] for name,vs,sva,rs,rp in sections if sva<=rva and rva+size<=sva+rs]
  assert len(matches)==1,(hex(va),size)
  return matches[0]
 def word(va):return struct.unpack('<I',bytes_at(va,4))[0]
 entry=bytes_at(0x5a2d1a,233)
 assert entry[0x59:0x5E]==bytes.fromhex('e882690000') # 005a2d73 call 005a96fa
 assert entry[0xA5:0xAA]==bytes.fromhex('e87df6ffff') # 005a2dbf call 005a2441
 assert entry[0xDB:0xE0]==bytes.fromhex('e81639f1ff') # 005a2df5 call 004b6710
 init=bytes_at(0x5a2441,45)
 assert init[:5]==bytes.fromhex('a1b4515e00')
 assert word(0x5e51b4)==0x5a0f45
 assert bytes_at(0x5a2547,26).find(bytes.fromhex('ffd0'))>=0
 tables=[(0x5cb000,0x5cb780),(0x5cb784,0x5cb798)]
 leading=[]
 for start,end in tables:
  assert start<end and (end-start)%4==0
  entries=[(va,word(va)) for va in range(start,end,4)]
  leading.append(dict(start=f'{start:08x}',end_exclusive=f'{end:08x}',slots=len(entries),first_nonzero=next(dict(slot=f'{va:08x}',target=f'{target:08x}') for va,target in entries if target)))
 assert leading[0]['first_nonzero']==dict(slot='005cb004',target='004035e0')
 assert leading[1]['first_nonzero']==dict(slot='005cb788',target='005a2412')
 first=bytes_at(0x4035e0,20);second=bytes_at(0x403600,19)
 assert bytes.fromhex('c744240000008000') in first and bytes.fromhex('a324675e00') in first
 assert second[:6]==bytes.fromhex('d905a8245b00') and bytes.fromhex('d83524675e00') in second and bytes.fromhex('d91d20675e00') in second
 assert word(0x5e6724)==word(0x5e6720)==0 and word(0x5b24a8)==0x3f800000
 registry_path=ROOT/'iterations/v2/001-original-recovery/source/recovered/functions.json';owners=load(registry_path)['functions']
 status={va:[dict(source=x['source'],status=x['status']) for x in owners if x['entry_va']==va] for va in ('005a2d1a','005a96fa','005aa96c','005a53f5','005a953e','005a940c','005a91bf','005a9106','005a2441','005a2547','005a0f45','004035e0','00403600','004b6710','004b6a50')}
 assert not any(status[va] for va in ('005a2d1a','005a940c','005a91bf','005a9106','005a2441','005a0f45','004035e0','00403600'))
 assert all(status[va] for va in ('005a96fa','005aa96c','005a53f5','005a953e','005a2547','004b6710','004b6a50'))
 host=ROOT/'iterations/v2/001-original-recovery/runs/102-original-game-link/host-entry.cpp';host_text=host.read_text()
 assert 'WinMain(' in host_text and 'win_main_004b6710' in host_text and '005a2d1a' not in host_text
 old_path=ROOT/'iterations/v2/001-original-recovery/runs/173-float-transport-integration/original-game-link/link-report.json';old=load(old_path)
 assert old['status']=='link_failed_unresolved_frontier' and not old['game_executable_executed']
 assert old['entry_chain'][0].startswith('WinMain@16')
 direct=[x['symbol'] for x in old['unresolved_frontier'] if any(y['caller']=='?app_main_004b6a50@porsche@@YAHHPAPAD@Z' for y in x['references'])]
 assert '?application_main_log@porsche@@YAXPBD@Z' in direct
 app=ROOT/'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/application_main.cpp';source=app.read_text()
 assert source.index('application_main_setup_heaps(0x40000,0x8000)')<source.index('application_main_log("Initializing rendering")')
 imports=ROOT/'research/binary-index/static/imports.jsonl';names={x['iat_rva']:x['symbol'] for x in map(json.loads,imports.read_text().splitlines()) if x['path']=='Porsche.exe'}
 assert names['0x1b2174']=='GetVersion' and names['0x1b20d8']=='HeapCreate' and names['0x1b2138']=='GetModuleHandleA'
 paths=[game,registry_path,host,old_path,app,ROOT/'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/startup.cpp',ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl',imports]
 report=dict(schema=1,kind='read-only-original-entry-audit',original_sha256=SHA,input_sha256={relative(x):digest(x) for x in paths},original_pe_entry='005a2d1a',original_crt_chain=['005a2d1a','005a96fa','005a53f5','005a953e','005a940c','005a91bf','005a9106','005a2441','005a2547','004b6710','004b6a50'],original_crt_initial_iat=dict(va='005b2174',symbol='GetVersion'),optional_initializer_pointer=dict(storage_va='005e51b4',initial_target='005a0f45'),constructor_tables=leading,first_game_state_write=dict(function='004035e0',global_va='005e6724',initial_hex='00000000',written_hex='00008000',next_function='00403600',next_global_va='005e6720',next_original_operation='1.0f / float(0x00800000)'),registry_owners=status,host_entry=dict(source=relative(host),target='004b6710',original_crt_entry_called=False),old_link=dict(report=relative(old_path),status=old['status'],game_executable_executed=False,first_direct_app_main_unresolved_symbol='?application_main_log@porsche@@YAXPBD@Z',direct_app_main_unresolved_names=len(direct)),limits=['The MSVC host has its own runtime; equivalence of original CRT state and constructor order is unproved','No current native game link or original executable execution in this audit','First constructor global semantics and consumers need tracing before adding providers'])
 (RUN/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
 validation=dict(schema=1,summary_sha256=digest(RUN/'summary.json'),script_sha256=digest(__file__),original_sha256=SHA,read_only=True,original_entry_and_constructor_bytes_checked=True,registry_owner_checks=True,old_link_status_checked=True)
 (RUN/'validation.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf8',newline='\n')
 print(json.dumps(dict(original_entry='005a2d1a',first_missing_direct_startup_call='005a940c',first_constructor='004035e0',old_link_direct_app_main_unresolved=len(direct))))
if __name__=='__main__':main()
