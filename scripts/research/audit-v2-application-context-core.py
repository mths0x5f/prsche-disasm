"""Static liveness evidence and native compile audit for candidate177 only."""
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'iterations/v2/001-original-recovery/runs/177-application-context-core'
sys.path.insert(0,str(ROOT/'local/tools/python-unicorn'))
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
sys.path.insert(0,str(ROOT/'scripts/research'))
from v2_source_dependencies import source_hashes

def main():
    evidence=json.loads((RUN/'compile-candidate.json').read_text())
    stack=json.loads((RUN/'stack-evidence.json').read_text())
    decoder=Cs(CS_ARCH_X86,CS_MODE_32);decoder.detail=True
    code={int(x['va'],16):next(decoder.disasm(bytes.fromhex(x['original_hex']),int(x['va'],16))) for x in evidence['instructions']}
    jumps=[int(x,16) for x in stack['jump_table']['targets']]
    rows=[]
    scans=[]
    requirements={'je':{'ZF'},'jne':{'ZF'},'ja':{'CF','ZF'},'jbe':{'CF','ZF'},'jl':{'SF','OF'}}
    full_writes={'add','sub','xor','or','cmp','test','sbb'}
    aliases={'eax':('eax',0xffffffff),'ax':('eax',0xffff),'ah':('eax',0xff00),'al':('eax',0xff),
             'ecx':('ecx',0xffffffff),'cx':('ecx',0xffff),'ch':('ecx',0xff00),'cl':('ecx',0xff),
             'edx':('edx',0xffffffff),'dx':('edx',0xffff),'dh':('edx',0xff00),'dl':('edx',0xff)}
    ordered=sorted(code)
    branch_entries={int(i.op_str,16) for i in code.values() if i.mnemonic.startswith('j') and i.op_str.startswith('0x')}|set(jumps)
    for position,a in enumerate(ordered):
        if 'scasb' not in code[a].mnemonic:continue
        for j in range(position-1,-1,-1):
            ins=code[ordered[j]]
            _,writes=ins.regs_access()
            if any(ins.reg_name(r)=='ecx' for r in writes):
                assert ins.mnemonic=='or' and ins.op_str=='ecx, 0xffffffff',(hex(a),ins.mnemonic,ins.op_str)
                assert not set(ordered[j+1:position+1])&branch_entries
                scans.append({'scan_va':f'{a:08x}','counter_definition_va':f'{ins.address:08x}','initial_counter':'ffffffff'})
                break
            assert ins.mnemonic not in ['call','jmp','ret'] and not ins.mnemonic.startswith('j')
        else:raise AssertionError(hex(a))
    for a,call in code.items():
        if call.mnemonic!='call':continue
        work=[(a+call.size,(0,0,0),frozenset())];visited=set();flags=set();registers={r:0 for r in ['eax','ecx','edx']};fpu=[]
        while work:
            address,killed,changed=work.pop();key=(address,killed,changed)
            if key in visited:continue
            visited.add(key);ins=code[address];m=ins.mnemonic
            if m in ['call','ret']:continue
            flags.update(requirements.get(m,set())-changed)
            if m in ['sbb']:flags.update({'CF'}-changed)
            if 'scasb' in m:flags.update({'DF'}-changed)
            if m in ['fld','fstp']:fpu.append(f'{address:08x}')
            read,written=ins.regs_access();next_killed=list(killed)
            for reg in read:
                n=ins.reg_name(reg)
                if n in aliases:
                    r,mask=aliases[n];registers[r]|=mask&~killed[['eax','ecx','edx'].index(r)]
            for reg in written:
                n=ins.reg_name(reg)
                if n in aliases:
                    r,mask=aliases[n];next_killed[['eax','ecx','edx'].index(r)]|=mask
            next_changed=changed
            if m in full_writes:next_changed=changed|{'CF','ZF','SF','OF'}
            elif m=='dec':next_changed=changed|{'ZF','SF','OF'}
            elif 'scasb' in m:
                # Every source scan is entered after OR ECX,-1; current abstract
                # scan is therefore nonempty. No call or branch modifies that ECX.
                next_changed=changed|{'CF','ZF','SF','OF'}
            if m=='jmp':dest=[int(ins.op_str,16)] if ins.op_str.startswith('0x') else jumps
            elif m.startswith('j'):dest=[int(ins.op_str,16),address+ins.size]
            else:dest=[address+ins.size]
            work.extend((n,tuple(next_killed),frozenset(next_changed)) for n in dest)
        rows.append({'call_va':f'{a:08x}','target':call.op_str,'body_flags_live_before_next_call':sorted(flags),
            'volatile_register_bits_live_before_next_call':{r:f'{v:08x}' for r,v in registers.items() if v},
            'native_x87_instruction_sites_before_next_call':sorted(set(fpu))})
    source=ROOT/'iterations/v2/001-original-recovery/source/recovered/Porsche.exe/application_context_core_candidate.cpp'
    header=ROOT/'iterations/v2/001-original-recovery/source/include/porsche/application_context_core_candidate.hpp'
    build=ROOT/'local/builds/v2/application-context-core-177'
    obj=build/'application_context_core_candidate.dir/Release/application_context_core_candidate.obj'
    data=obj.read_bytes();assert struct.unpack_from('<H',data)[0]==0x14c
    log=ROOT/'local/reports/v2-application-context-core-177-build.log'
    text=log.read_text(encoding='utf-16' if log.read_bytes().startswith(b'\xff\xfe') else 'utf-8-sig')
    assert not re.search(r'\b(?:warning|error) C\d+',text),text[-3000:]
    cache=(build/'CMakeCache.txt').read_text();assert 'CMAKE_GENERATOR_PLATFORM:INTERNAL=Win32' in cache
    compiler=next((build/'CMakeFiles').glob('*/CMakeCXXCompiler.cmake')).read_text()
    assert 'set(CMAKE_CXX_COMPILER_ID "MSVC")' in compiler
    symbols=ROOT/'local/reports/v2-application-context-core-177-coff-symbols.txt'
    symbol_text=symbols.read_text(encoding='utf-16' if symbols.read_bytes().startswith(b'\xff\xfe') else 'utf-8-sig')
    undefined=[x.split('|',1)[1].strip() for x in symbol_text.splitlines() if 'UNDEF' in x and 'External' in x]
    assert sum('application_core_effect_' in x for x in undefined)==134
    assert sum('application_core_virtual_' in x for x in undefined)==10
    assert sum('application_core_address_' in x for x in undefined)==52
    paths=[str(x.relative_to(ROOT)).replace('\\','/') for x in [source,header,RUN/'README.md',RUN/'CMakeLists.txt',
        RUN/'stack-evidence.json',RUN/'virtual-target-evidence.json',RUN/'compile-candidate.json',Path(__file__),
        ROOT/'scripts/research/analyze-v2-application-context-core.py',ROOT/'scripts/research/generate-v2-application-context-core.py',
        ROOT/'research/binary-index/static/binaries.jsonl',
        ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl',
        ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/calls.jsonl',
        ROOT/'research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/references.jsonl',
        ROOT/'research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm']]
    report={'schema':1,'kind':'compile-candidate-static-audit-not-original-differential-proof',
        'function_va':'004d3420','emitted_original_bytes':8589,'emitted_instruction_sites':2575,
        'native_compile':{'compiler':'MSVC','platform':'Win32','coff_machine':'014c','warnings':0,'errors':0,
            'object_sha256':hashlib.sha256(data).hexdigest(),'object_bytes':len(data),
            'build_log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()},
        'coff_undefined_symbols':undefined,'coff_symbol_report_sha256':hashlib.sha256(symbols.read_bytes()).hexdigest(),
        'call_seam_liveness':rows,'nonempty_scan_counter_proof':scans,'scope':'Four arithmetic condition codes and DF are explicit mutable typed state; PF/AF are not body consumers. Native x87 hardware state remains live across external effects. Static liveness stops at the next call: each unresolved callee still needs a separate input/return contract audit.',
        'arithmetic_flags_live_call_sites':[x['call_va'] for x in rows if set(x['body_flags_live_before_next_call'])-{'DF'}],
        'direction_flag_live_call_sites':[x['call_va'] for x in rows if 'DF' in x['body_flags_live_before_next_call']],
        'x87_live_call_sites':[x['call_va'] for x in rows if x['native_x87_instruction_sites_before_next_call']],
        'source_sha256':source_hashes(paths,compiled_sources=[str(source.relative_to(ROOT)).replace('\\','/')]),
        'accepted_registry_changed':False,'game_production_bound':False,'behavioral_verification':False}
    (RUN/'compile-audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'compiled_bytes':8589,'sites':2575,'calls':len(rows),'arithmetic_flags_live':len(report['arithmetic_flags_live_call_sites']),
        'DF_live':len(report['direction_flag_live_call_sites']),'x87_live':len(report['x87_live_call_sites']),'source_files':len(report['source_sha256'])}))

if __name__=='__main__':main()
