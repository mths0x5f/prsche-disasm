"""Compare four complete application service bodies against frozen x86."""
import argparse
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path

from v2_source_dependencies import source_hashes

ROOT = Path(__file__).resolve().parents[2]
SHA = "ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39"
BASE, STACK, EXIT = 0x400000, 0x2201000, 0x222F000
ARENA, ARENA_BYTES = 0x6573E8, 0x3E24
RESET, RESET_BYTES = 0x655D48, 0x2B8
NET_A, NET_B, LOCK_A, LOCK_B = 0x23000000, 0x23001000, 0x23002000, 0x23002004
FUNCTIONS = {0: (0x4A6960, 0x99), 1: (0x4A6E30, 0xD9),
             2: (0x48DAD0, 0xDA), 3: (0x48E6F0, 0x99)}
# address: (stack args, callee pops bytes, capture ECX)
BOUNDARIES = {
    0x5659F0: (1, 0, False), 0x531F90: (1, 0, False),
    0x4AE310: (0, 0, False), 0x4AB4B0: (0, 0, False),
    0x565890: (0, 0, False), 0x5A177B: (2, 0, False),
    0x5322B0: (1, 0, False), 0x5322C0: (1, 0, False),
    0x48C870: (5, 20, True), 0x48E9C0: (0, 0, True),
    0x48E1A0: (3, 12, True), 0x4935C0: (0, 0, True),
    0x59F050: (1, 0, False),
}


def cases():
    result = []
    def add(op, *args):
        result.append([op, *args, *([0] * (12 - len(args)))])
    # Every shutdown gate; wrapped SHL and signed division extrema.
    for active, secondary, buffer in ((0, 0, 0x23003000), (0, 1, 0x23003000),
                                      (1, 0, 0), (1, 0, 0x23003000),
                                      (0x80000000, 0, 0x23003000)):
        for record in (0, 0x23003600):
            add(0, record, 0x12345678, active, secondary, buffer, 7)
    for measure in (0, 1, 8190, 8191, 8192, 16382, 16383, 0x7FFFFFFF,
                    0x80000000, 0xFFFFFFFF, 0xFFFFDFFF):
        add(0, 0x23003600, 0x12345678, 1, 1, 0x23003000, measure)
    for mutation in (1, 2, 4, 8, 16, 31):
        add(0, 0, 0x12345678, 0, 0, 0, 8191, mutation)
        add(0, 0x23003600, 0x12345678, 1, 0, 0x23003000, 8192, mutation)
    for mode in (0, 1, 2, 3, 0xFFFFFFFF, 0x80000000, 0x7FFFFFFF):
        for count in (0, 1, 2, 3, 0xFFFFFFFF):
            add(1, mode, 1, count)
    for selected in (0, 2, 3, 0xFFFFFFFF, 0x7FFFFFFF):
        add(1, 2, selected, 3)
    add(2, 0, 1, 0, 0)
    add(2, 1, 0, 0, 0)
    add(2, 1, 1, 1, 0)
    for bd in (0, 1, 0xFF):
        add(2, 1, 1, 0, bd)
    for mutation in (1, 2, 4, 8, 16, 3, 6, 17, 31):
        add(2, 1, 1, 0, 0, mutation)
    for mode in (0, 2):
        for changed in (0, 1, 2):
            for initial in (0, 1, 2):
                add(3, mode, 0, 0, changed, 0, initial)
    for mode in (1, 3, 0x80000000, 0xFFFFFFFF):
        for flag, member in ((0, 0), (1, 0), (1, 1), (0xFF, 1)):
            add(3, mode, flag, member, 0, member)
    for mode, flag, member in ((0, 0, 0), (2, 0, 0), (3, 1, 1), (1, 0, 0)):
        add(4, mode, flag, member)
    return result


def original(module, image, case):
    sys.path.insert(0, str(ROOT / "local/tools/python-unicorn"))
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
    from unicorn.x86_const import (UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_ECX,
        UC_X86_REG_EDI, UC_X86_REG_EBP, UC_X86_REG_EIP, UC_X86_REG_ESI, UC_X86_REG_ESP)
    uc = Uc(UC_ARCH_X86, UC_MODE_32)
    uc.mem_map(BASE, 0x300000)
    for section in module["sections"]:
        if section["raw_size"]:
            uc.mem_write(BASE + section["rva"], image[section["raw_offset"]:
                section["raw_offset"] + section["raw_size"]])
    uc.mem_map(0x2200000, 0x30000)
    uc.mem_map(NET_A, 0x10000)
    def put(addr, value): uc.mem_write(addr, struct.pack("<I", value & 0xFFFFFFFF))
    def get(addr): return struct.unpack("<I", uc.mem_read(addr, 4))[0]
    def putbyte(addr, value): uc.mem_write(addr, bytes([value & 0xFF]))
    def words(addr, size): return list(struct.unpack(f"<{size // 4}I", uc.mem_read(addr, size)))
    op, *a = case
    uc.mem_write(ARENA, struct.pack(f"<{ARENA_BYTES // 4}I", *([0xABABABAB] * (ARENA_BYTES // 4))))
    uc.mem_write(RESET, struct.pack(f"<{RESET_BYTES // 4}I", *[0x70000000 + i for i in range(RESET_BYTES // 4)]))
    uc.mem_write(0x6564A0, struct.pack("<32I", *[v for i in range(8) for v in (0x1000+i,0x2000+i,0x3000+i,0x4000+i)]))
    put(0x655D44, 0x12345678); put(0x5D1734, 0x55555555); put(0x5D1738, 0x66666666)
    put(LOCK_A, 0x11110000); put(LOCK_B, 0x22220000)
    for n, index in ((NET_A, 0), (NET_B, 1)):
        uc.mem_write(n, struct.pack("<64I", *([0xA0A00000 + index] * 64)))
        put(n+8,a[1]); putbyte(n+0xBF,a[2]); putbyte(n+0xBD,a[3])
        put(n+0xC,0x24000000 + index*0x1000); put(n+0x10,LOCK_B if index else LOCK_A)
    put(0x628C70, NET_A)
    receiver = NET_A
    if op == 0:
        for address, value in ((0x656518,a[0]), (0x656510,a[1]),
            (0x5D1734,a[2]), (0x5D1738,a[3]), (0x655D44,a[4])): put(address,value)
    elif op == 1:
        put(0x657404,a[0]); put(0x65741C,a[1]); put(0x5E8BFC,a[2])
        for i in range(1,16): put(0x5E8BFC+i*4,0x81000000+i*0x12345)
    elif op == 2:
        if not a[0]: put(0x628C70,0)
    else:
        put(NET_A+0x28,a[0]); putbyte(NET_A+0xC6,a[1]); put(NET_A+0x14,0x25000000 if a[2] else 0)
        if a[5] == 1: put(0x628C70,0)
        if a[5] == 2: put(0x628C70,NET_B)
        if op == 4: receiver = get(0x628C70)
    put(STACK,EXIT); uc.reg_write(UC_X86_REG_ESP,STACK); uc.reg_write(UC_X86_REG_ECX,receiver)
    saved = {UC_X86_REG_EBX: 0x11223344, UC_X86_REG_ESI: 0x55667788,
             UC_X86_REG_EDI: 0x99AABBCC, UC_X86_REG_EBP: 0xDDEEFF00}
    for reg,value in saved.items(): uc.reg_write(reg,value)
    trace, message_count = [], 0
    def hook(machine,address,_size,_user):
        nonlocal message_count
        if address == EXIT: machine.emu_stop(); return
        if address not in BOUNDARIES: return
        argc,pop,member = BOUNDARIES[address]
        sp = machine.reg_read(UC_X86_REG_ESP)
        args = [get(sp+4+i*4) for i in range(argc)]
        trace.append([address, *([machine.reg_read(UC_X86_REG_ECX)] if member else []), *args])
        result = 0
        if address == 0x5659F0 and a[6] & 1: put(0x656518,0x23003100)
        if address == 0x531F90:
            result = 1
            if a[6] & 2: put(0x655D44,0x23003200)
        if address == 0x4AE310 and a[6] & 4:
            put(0x5D1734,1); put(0x655D44,0x23003300)
        if address == 0x4AB4B0 and a[6] & 8: put(0x655D44,0x23003400)
        if address == 0x565890:
            result = a[5]
            if a[6] & 16: put(0x655D44,0x23003500)
        if address == 0x5A177B: trace[-1].append(get(0x655D44))
        if address == 0x5322B0 and op == 2:
            if a[4] & 1: put(0x628C70,NET_B)
            if a[4] & 2: put(LOCK_A,0x33330000)
        if address == 0x5322C0 and op == 2 and a[4] & 4: put(0x628C70,NET_A)
        if address == 0x48C870:
            message_count += 1
            if op == 2 and message_count == 1:
                if a[4] & 8: putbyte(get(0x628C70)+0xBF,1)
                if a[4] & 16: put(0x628C70,NET_B)
        if address == 0x48E9C0:
            if a[3] == 1: put(0x628C70,0)
            if a[3] == 2: put(0x628C70,NET_B)
        if address == 0x4935C0 and a[4]: put(NET_A+0xC,0x24004000)
        if address == 0x59F050:
            trace[-1].append(get(NET_A+0x14)); result = 1
        machine.reg_write(UC_X86_REG_EAX,result)
        machine.reg_write(UC_X86_REG_ESP,sp+4+pop)
        machine.reg_write(UC_X86_REG_EIP,get(sp))
    uc.hook_add(UC_HOOK_CODE,hook)
    start = FUNCTIONS[min(op,3)][0]
    try: uc.emu_start(start,EXIT+1,count=100000)
    except Exception as error:
        raise RuntimeError(f"x86 fault case={case}, EIP={uc.reg_read(UC_X86_REG_EIP):08x}, trace={trace}") from error
    assert uc.reg_read(UC_X86_REG_EIP) == EXIT
    assert uc.reg_read(UC_X86_REG_ESP) == STACK+4
    assert all(uc.reg_read(reg) == value for reg,value in saved.items())
    state = (words(ARENA,ARENA_BYTES) + words(RESET,RESET_BYTES) + words(0x6564A0,0x80) +
        [get(0x655D44),get(0x5D1734),get(0x5D1738)] + words(NET_A,0x100) + words(NET_B,0x100) +
        [get(0x628C70),get(LOCK_A),get(LOCK_B)])
    return {"state":state,"trace":trace}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe",type=Path,default=ROOT / "local/builds/v2/application-services-next-141/bin/Release/application_services_next_probe.exe")
    parser.add_argument("--report-dir",type=Path,required=True)
    args = parser.parse_args(); args.report_dir.mkdir(parents=True,exist_ok=True)
    module = next(x for x in map(json.loads,(ROOT / "research/binary-index/static/binaries.jsonl").read_text().splitlines()) if x["file"] == "Porsche.exe")
    image = (ROOT / "local/game" / module["path"]).read_bytes()
    assert hashlib.sha256(image).hexdigest() == SHA
    all_cases = cases()
    run = subprocess.run([str(args.probe)],input="".join(" ".join(map(str,c))+"\n" for c in all_cases),text=True,capture_output=True,check=True)
    actuals = [json.loads(line) for line in run.stdout.splitlines()]
    assert len(actuals) == len(all_cases)
    summary=[]
    for i,(case,actual) in enumerate(zip(all_cases,actuals)):
        expected=original(module,image,case)
        for key in ("state","trace"):
            if actual[key] != expected[key]:
                details = [(n,x,y) for n,(x,y) in enumerate(zip(expected[key],actual[key])) if x != y]
                raise AssertionError(f"case {i} {case}: {key} mismatch; first differences {details[:6]}; x86trace={expected['trace']}; native={actual['trace']}")
        summary.append({"index":i,"function_va":f"{FUNCTIONS[min(case[0],3)][0]:08x}","input":case,"boundary_calls":len(expected["trace"])})
    def raw(va,size):
        rva=va-BASE
        section=next(s for s in module['sections'] if s['rva'] <= rva and rva+size <= s['rva']+s['raw_size'])
        offset=section['raw_offset']+rva-section['rva']; return image[offset:offset+size]
    assert raw(0x5D1738,4) == b'\x01\x00\x00\x00'
    for va,size in ((RESET,RESET_BYTES),(0x5E8BFC,4)):
        rva=va-BASE
        section=next(s for s in module['sections'] if s['rva'] <= rva and rva+size <= s['rva']+s['vsize'])
        assert rva >= section['rva']+section['raw_size'], "new state must be proven zero-fill"
    # Callee-pop instruction evidence supplements the member callsite shape.
    assert raw(0x48C979,3) == b'\xc2\x14\x00'
    assert raw(0x48E6EA,3) == b'\xc2\x0c\x00'
    base="iterations/v2/001-original-recovery/"
    compiled=[base+"source/recovered/"+p for p in ("application_services_next_probe.cpp","Porsche.exe/application_services_next.cpp","Porsche.exe/application_services.cpp","Porsche.exe/application_state.cpp","Porsche.exe/install_paths_storage.cpp")]
    paths=compiled+[base+"runs/141-application-services-next/"+p for p in ("README.md","CMakeLists.txt")]+[
        "scripts/research/verify-v2-application-services-next.py","research/binary-index/static/binaries.jsonl",
        "research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/functions.jsonl",
        "research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/calls.jsonl",
        "research/binary-index/ghidra/Porsche.exe-ddd748fdbe6d/references.jsonl",
        "research/v2/binaries/Porsche.exe-ddd748fdbe6d/disassembly.asm"]
    report={"schema":1,"module":"Porsche.exe","sha256":SHA,"module_sha256":SHA,
        "function_vas":[f"{va:08x}" for va,_ in FUNCTIONS.values()],
        "full_function_vas":[f"{va:08x}" for va,_ in FUNCTIONS.values()],"partial_function_vas":[],
        "cases":len(all_cases),"native_cpp_equal_original_x86":True,
        "comparison_boundary":"Complete four bodies; full application arena, reset BSS span, existing eight audio records, audio active/buffer cells, both network objects, lock-cell state, ordered boundary calls including ECX/callee-pop args and post-callback rereads; original nonvolatile registers/ESP. Return EAX is undefined and unused by known callers.",
        "caller_vas":["004b6a50","00509170","0050a4b0"],
        "index_query":"Porsche.exe addresses 004b68f0/004a6960/004a6e30/0048dad0/0048e6f0; inspect callers/callees and full ASM. 004b68f0 is traced but not recovered in this packet.",
        "unresolved_effects":[f"{va:08x}" for va in BOUNDARIES],
        "unresolved_storage":["005e8bfc count followed by unsized 005e8c00 table; contiguous view declared, no guessed production extent/owner"],
        "new_storage":[{"va":"00655d48","bytes":RESET_BYTES,"initial":"PE section zero-fill"},{"va":"005d1738","bytes":4,"initial":1}],
        "aliases":{"00656510":"application_audio_records_006564a0[7].raw_00","00656518":"application_audio_records_006564a0[7].raw_08"},
        "original_functions":[{"va":f"{va:08x}","body_bytes":size,"body_sha256":hashlib.sha256(raw(va,size)).hexdigest()} for va,size in FUNCTIONS.values()],
        "cases_summary":summary,"source_sha256":source_hashes([ROOT/p for p in paths],compiled_sources=[ROOT/p for p in compiled])}
    (args.report_dir/"verification.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({k:report[k] for k in ("function_vas","cases","native_cpp_equal_original_x86")}))


if __name__ == "__main__": main()
