"""Original-x86 differential for audio transitions and ordered shutdown effects."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
from v2_source_dependencies import source_hashes

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / 'iterations/v2/001-original-recovery'
SHA = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'
BASE, STACK, EXIT = 0x400000, 0x2201000, 0x222f000
ARENA, ARENA_BYTES = 0x6573e8, 0x3e24
STATE, STATE_BYTES = 0x6b48b0, 0x18c
FUNCTIONS = {'004a6a00':375, '004ab470':63, '004ab4b0':47, '00565890':135}
BOUNDARIES = {
    0x531ca0:(1,3), 0x531f90:(2,1), 0x4a66b0:(3,0),
    0x4ae100:(4,3), 0x4a8b80:(5,0), 0x4ae2b0:(6,0),
    0x4ae010:(7,2), 0x4ae4d0:(8,2), 0x5659f0:(9,1),
    0x565c70:(10,5), 0x58ff10:(11,0), 0x58fe80:(12,0),
    0x58ac30:(13,1), 0x58e2e0:(14,0), 0x58aac0:(15,0),
}

def cases():
    base = [0,0,1,0x40000,0x400,2,0,0,0,0,0,1,15,1,1,0]
    result = []
    def add(label, **changes):
        row = base.copy()
        for key, value in changes.items(): row[int(key[1:])] = value
        result.append((label,row))
    add('transition_success')
    add('transition_init_failure',v13=0)
    add('transition_null_allocate',v14=0)
    add('transition_disabled',v1=1)
    add('transition_high_disable_byte',v1=0x100)
    add('transition_mode3_forces_disabled',v2=3)
    add('transition_early_equal',v2=2,v3=0)
    add('transition_equal_flag_forces_work',v2=2,v3=0,v7=1)
    add('transition_negative_mode_unclamped',v2=0xfffffff6)
    add('transition_release_and_restart',v8=0x12345000,v9=0xabcdef00,v10=0x55667788)
    add('transition_release_disabled',v1=0x101,v8=0x12345000,v9=0xabcdef00,v10=0)
    add('transition_mutated_callback_reload',v8=0x12345000,v9=0xabcdef00,v10=0x55667788,v15=63)
    add('finish_empty',v0=1)
    add('finish_release',v0=1,v9=0xabcdef00)
    add('finish_control_rebinds_pointer',v0=1,v9=0xabcdef00,v15=1)
    add('measure_inactive',v0=2,v11=0)
    add('measure_no_callbacks',v0=2,v12=0)
    add('measure_all_callbacks',v0=2)
    add('measure_callback_rebind_and_clear',v0=2,v15=6)
    add('measure_quiet_installs_callback',v0=2,v12=7,v15=8)
    add('measure_backend_rebinds_release',v0=2,v15=48)
    add('post_not_configured',v0=3)
    add('post_configured',v0=3,v10=1)
    add('setup_composed_shutdown',v0=4)
    add('setup_composed_null_callbacks',v0=4,v12=0)
    add('setup_composed_init_failure',v0=4,v13=0)
    return result

def original(module, image, row):
    sys.path.insert(0,str(ROOT/'local/tools/python-unicorn'))
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
    from unicorn.x86_const import (UC_X86_REG_EAX,UC_X86_REG_EIP,UC_X86_REG_ESP,
        UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP)
    uc=Uc(UC_ARCH_X86,UC_MODE_32)
    uc.mem_map(BASE,0x300000)
    for section in module['sections']:
        if section['raw_size']:
            p=section['raw_offset'];uc.mem_write(BASE+section['rva'],image[p:p+section['raw_size']])
    uc.mem_map(0x2100000,0x10000)
    uc.mem_map(0x2200000,0x30000)
    def put(va,value):uc.mem_write(va,struct.pack('<I',value&0xffffffff))
    def get(va):return struct.unpack('<I',uc.mem_read(va,4))[0]
    uc.mem_write(ARENA,struct.pack('<I',0xabababab)*(ARENA_BYTES//4))
    for va,val in ((0x657c94,0x12345678),(0x657c98,row[5]),(0x657c9c,0xcccccccc),
        (0x655d34,row[6]),(0x655d38,row[5]),(0x655d44,row[8]),
        (0x6568e4,row[9]),(0x5d1734,0x55555555),(0x655d40,row[10])):put(va,val)
    uc.mem_write(0x655d3c,bytes([row[7]&255]))
    uc.mem_write(0x656868,bytes([0x87,0x98]))
    records=[]
    for i in range(8):records.extend([0x1000+i,0x2000+i,0x3000+i,0x4000+i])
    records[30]=row[10]
    uc.mem_write(0x6564a0,struct.pack('<32I',*records))
    uc.mem_write(STATE,bytes((i*29+7)&255 for i in range(STATE_BYTES)))
    uc.mem_write(0x6b499c,bytes([row[11]&255]))
    for bit,cell,target in ((1,0x6b49f8,0x2100100),(2,0x6b49fc,0x2100200),
        (4,0x6b49f4,0x2100300),(8,0x6b49f0,0x2100500)):
        put(cell,target if row[12]&bit else 0)
    put(0x6b4a00,0x11111111);put(0x6b4a04,0x22222222)
    function=row[0]
    entry=[0x4a6a00,0x4ab4b0,0x565890,0x4ab470,0x4a6840][function]
    args=([row[1],0xdeadbeef,row[2],row[3],row[4]] if function==0 else
          [row[3],row[4]] if function==4 else [])
    put(STACK,EXIT)
    for i,value in enumerate(args):put(STACK+4+i*4,value)
    uc.reg_write(UC_X86_REG_ESP,STACK)
    saved={UC_X86_REG_EBX:0x13572468,UC_X86_REG_ESI:0x24681357,
        UC_X86_REG_EDI:0xdeadbabe,UC_X86_REG_EBP:0x76543210}
    for reg,value in saved.items():uc.reg_write(reg,value)
    trace=[]
    def hook(machine,address,_size,_user):
        if address==EXIT:machine.emu_stop();return
        callback=0x2100100<=address<=0x2100500 and address%0x100==0
        if callback:
            index=(address-0x2100100)//0x100;event=20+index;argc=1 if index==4 else 0
        elif address in BOUNDARIES:event,argc=BOUNDARIES[address]
        else:return
        sp=machine.reg_read(UC_X86_REG_ESP)
        values=[get(sp+4+4*i) for i in range(argc)]
        trace.append([event,*values,*([0]*(5-argc))])
        result=0
        if event==1:result=0x23000000 if row[14] else 0
        elif event==2:result=0x71717171
        elif event==3:result=row[13]&255
        elif event==9:result=0xfffffff8
        elif event==15:result=(-123)&0xffffffff
        mutation=row[15]
        if event==10 and mutation&1:put(0x6568e4,0x76543210)
        if event==20 and mutation&2:put(0x6b49fc,0x2100400)
        if event==21 and mutation&4:put(0x6b49f4,0)
        if event==11 and mutation&8:put(0x6b49f0,0x2100500)
        if event==12 and mutation&16:put(0x6b4a00,0xa0a0a0a0)
        if event==13 and mutation&32:put(0x6b4a04,0xb0b0b0b0)
        machine.reg_write(UC_X86_REG_EAX,result)
        machine.reg_write(UC_X86_REG_ESP,sp+4)
        machine.reg_write(UC_X86_REG_EIP,get(sp))
    uc.hook_add(UC_HOOK_CODE,hook)
    uc.emu_start(entry,EXIT+1,count=10000)
    assert uc.reg_read(UC_X86_REG_EIP)==EXIT
    assert uc.reg_read(UC_X86_REG_ESP)==STACK+4
    for reg,value in saved.items():assert uc.reg_read(reg)==value
    result=uc.reg_read(UC_X86_REG_EAX) if function==2 else 0
    if result&0x80000000:result-=1<<32
    return {'result':result,'trace':trace,
        'arena':list(struct.unpack(f'<{ARENA_BYTES//4}I',uc.mem_read(ARENA,ARENA_BYTES))),
        'records':list(struct.unpack('<32I',uc.mem_read(0x6564a0,0x80))),
        'outside':[get(0x655d34),get(0x655d38),uc.mem_read(0x655d3c,1)[0],get(0x655d44),
            get(0x6568e4),get(0x5d1734),get(0x655d40),uc.mem_read(0x656868,1)[0],uc.mem_read(0x656869,1)[0]],
        'audio':list(uc.mem_read(STATE,STATE_BYTES))}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--probe',type=Path,required=True)
    ap.add_argument('--report-dir',type=Path,required=True)
    args=ap.parse_args()
    module=next(json.loads(l) for l in (ROOT/'research/binary-index/static/binaries.jsonl').read_text().splitlines()
        if json.loads(l)['file']=='Porsche.exe')
    image=(ROOT/'local/game'/module['path']).read_bytes();assert hashlib.sha256(image).hexdigest()==SHA
    functions={json.loads(l)['entry_va']:json.loads(l) for l in
        (ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl').read_text().splitlines()}
    def raw(va,size):
        rva=va-BASE;s=next(s for s in module['sections'] if s['rva']<=rva and rva+size<=s['rva']+s['raw_size'])
        p=s['raw_offset']+rva-s['rva'];return image[p:p+size]
    pins={}
    for va,size in FUNCTIONS.items():
        f=functions[va];assert f['body_bytes']==size
        pins[va]={'bytes':size,'ranges':f['ranges'],'sha256':hashlib.sha256(raw(int(va,16),size)).hexdigest()}
    # Independent original caller: five pushes around the two virtual methods.
    assert raw(0x4e48a2,23).hex()=='68000400006800000400508b442414506a00e84721fcff'
    assert raw(0x5d13ec,11)==b'audio heap\0'
    for va in (0x6568e4,0x655d40,0x656868,0x656869):
        s=next(s for s in module['sections'] if s['rva']<=va-BASE<s['rva']+s['vsize'])
        assert va-BASE>=s['rva']+s['raw_size']
    rows=cases()
    proc=subprocess.run([str(args.probe)],input=''.join(' '.join(map(str,r))+'\n' for _,r in rows),
        text=True,capture_output=True,check=True,timeout=30)
    actual=[json.loads(line) for line in proc.stdout.splitlines()];assert len(actual)==len(rows)
    passed=[]
    for (label,row),native in zip(rows,actual):
        expected=original(module,image,row)
        if native!=expected:
            differences={k:{'original':expected[k],'native':native[k]} for k in expected if native[k]!=expected[k]}
            raise AssertionError(f'{label}: {str(differences)[:2400]}')
        passed.append({'case':label,'input':row,'ordered_calls':len(expected['trace']),
            'state_sha256':hashlib.sha256(json.dumps(expected,sort_keys=True).encode()).hexdigest()})
    paths=[__file__,PACKET/'runs/142-audio-lifecycle/CMakeLists.txt',
        ROOT/'scripts/research/v2_source_dependencies.py']
    compiled=[PACKET/'source/recovered'/name for name in ('application_audio_lifecycle_probe.cpp',
        'Porsche.exe/application_audio_lifecycle.cpp','Porsche.exe/application_services.cpp',
        'Porsche.exe/application_state.cpp')]
    report={'schema':1,'module':'Porsche.exe','sha256':SHA,'function_vas':sorted(FUNCTIONS),
        'full_function_vas':sorted(FUNCTIONS),'partial_function_vas':[],
        'cases':len(rows),'native_cpp_equal_original_x86':True,'original_body_pins':pins,
        'comparison':'Entire canonical application arena, all eight audio records, preceding/state audio bytes, exact effect order/arguments, return of00565890; three cases execute original004a6840 with real shutdown bodies.',
        'void_return_contract':'004a6a00,004ab470,004ab4b0 callers ignore incidental EAX; no arbitrary register return parity is claimed.',
        'scope':['004a6a00 writes unbounded virtual-method-derived mode unchanged; this does not establish the input domain of004a66b0.',
            'Actual allocation/audio/control/initializer effects are controlled boundaries; no live audio or startup acceptance.',
            'New state cells are PE zero-fill; existing arena, records and device bytes reuse canonical owners.'],
        'case_results':passed,'source_sha256':source_hashes(paths,compiled_sources=compiled),
        'probe_sha256':hashlib.sha256(args.probe.read_bytes()).hexdigest(),
        'game_launch_verified':False,'binary_matched':False}
    args.report_dir.mkdir(parents=True,exist_ok=True)
    (args.report_dir/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({'cases':len(rows),'full_functions':sorted(FUNCTIONS),'original_equal':True}))
if __name__=='__main__':main()
