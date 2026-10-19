"""Isolated Win32 differential check of two PR3 Run400 bodies.

Reads merged PR3 sources and immutable retail PE; preserves each numbered attempt.
"""
from pathlib import Path
import hashlib
import json
import struct
import subprocess
import argparse
import importlib.util
import re
import time
from v2_source_dependencies import source_hashes
from v2_shared_manifests import externalize, ManifestReader

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "iterations/v2/001-original-recovery/runs/310-pr-intake-integration"
OUT = None
PR = "29ff619d06682819483d588143f028b18d834cc2"
REL = "iterations/v2/001-original-recovery/runs/400-frame-loop-clusters"
PE_SHA = "ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39"


def extract(name):
    source = ROOT / REL / name
    expected = subprocess.check_output(["git", "show", f"{PR}:{REL}/{name}"], cwd=ROOT)
    assert source.read_bytes().replace(b"\r\n", b"\n") == expected.replace(b"\r\n", b"\n"), name
    return source


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def capture(cmd, label):
    started = time.time()
    p = subprocess.run(list(map(str, cmd)), cwd=OUT, capture_output=True, timeout=120)
    log = OUT / (label + ".log")
    log.write_bytes(p.stdout + p.stderr)
    receipt = dict(command=list(map(str, cmd)), seconds=time.time()-started,
                   exit_code=p.returncode, log=log.relative_to(ROOT).as_posix(), log_sha256=sha(log))
    path = OUT / (label + ".receipt.json")
    path.write_text(json.dumps(receipt, indent=2)+"\n", encoding="utf8")
    assert p.returncode == 0, f"{label} failed: {log}"
    return receipt


def pe_body(data, va, size):
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    base = struct.unpack_from("<I", data, pe + 24 + 28)[0]
    section = pe + 24 + struct.unpack_from("<H", data, pe + 20)[0]
    for i in range(struct.unpack_from("<H", data, pe + 6)[0]):
        q = section + 40 * i
        vs, rva, raw_size, raw_ptr = struct.unpack_from("<IIII", data, q + 8)
        x = va - base
        if rva <= x and x + size <= rva + min(vs, raw_size):
            return data[raw_ptr + x - rva:raw_ptr + x - rva + size]
    raise ValueError(hex(va))


def main():
    global OUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args()
    assert args.attempt.isascii() and args.attempt.isalnum()
    OUT = ROOT / "local/experiments/v2-pr-intake-310" / ("native-"+args.attempt)
    assert not OUT.exists(), "Preserve attempts"
    OUT.mkdir(parents=True)
    header = extract("frame_loop_clusters_400.hpp")
    sources = [extract(x.name) for x in sorted((ROOT / REL).glob("*.cpp"))]
    selected = [ROOT / REL / x for x in ("00412030.cpp", "00425780.cpp")]
    assert len(sources) == 21
    registry = json.loads((ROOT / "iterations/v2/001-original-recovery/source/recovered/functions.json").read_bytes())["functions"]
    assert not ({p.stem for p in sources} & {x["entry_va"] for x in registry})
    pe_path = ROOT / "local/game/Porsche.exe"
    pe = pe_path.read_bytes()
    assert hashlib.sha256(pe).hexdigest() == PE_SHA
    raw1 = pe_body(pe, 0x412030, 91)
    raw2 = pe_body(pe, 0x425780, 135)
    def arr(data):
        return ",".join(f"0x{x:02x}" for x in data)
    fixture = r'''#include "frame_loop_clusters_400.hpp"
#include <windows.h>
#include <cstdint>
#include <cstring>
using U = std::uint32_t;
namespace porsche {
U frame_control_enabled_005e940c=0;
U frame_control_index_005e9410=0;
FrameControlIndexTuple_400 frame_control_table_005e9420[4]{};
FrameVector_400* frame_callback_vector_0060c9f4=nullptr;
FrameVector_400* frame_compact_vector_0060c9c4=nullptr;
int release_log[16]{}; int release_count=0; int mutate_release=0;
void __cdecl frame_control_slot_release_005338d0(int x) {
    release_log[release_count++]=x;
    if (mutate_release && release_count==1) frame_control_index_005e9410=1;
}
FrameVector_400 alt_vec{}; int poll_log[16]{}; int notify_log[16]{};
int poll_count=0,notify_count=0,mutate_vector=0;
struct Callback final : FrameCallbackObject_400 {
    int id=0; int poll_result=0;
    void __thiscall slot_00() override {}
    void __thiscall slot_04() override {}
    void __thiscall slot_08() override {}
    void __thiscall slot_0c() override {}
    void __thiscall slot_10() override {}
    void __thiscall notify_14(U x) override { notify_log[notify_count++]=id*10+int(x); }
    U __thiscall poll_18() override {
        poll_log[poll_count++]=id;
        if (mutate_vector && poll_count==1) frame_callback_vector_0060c9f4=&alt_vec;
        return U(poll_result);
    }
};
Callback a[2],b[2]; U pairs_a[4]{},pairs_b[4]{};
}
static unsigned char original1[]={RAW1};
static unsigned char original2[]={RAW2};
static unsigned char* code1=nullptr; static unsigned char* code2=nullptr;
static int failures=0; static int checks=0;
void check(bool x){ ++checks; if(!x) ++failures; }
void patch32(unsigned char* code,unsigned n,U old,U replacement,int expected){
    int found=0;
    for(unsigned i=0;i+4<=n;++i){U x;std::memcpy(&x,code+i,4);
        if(x==old){std::memcpy(code+i,&replacement,4);++found;i+=3;}}
    check(found==expected);
}
void patch_call(unsigned char* code,U va,U call_va,void* target){
    unsigned off=call_va-va;check(code[off]==0xe8);
    U next=U(reinterpret_cast<std::uintptr_t>(code+off+5));
    U dest=U(reinterpret_cast<std::uintptr_t>(target));
    U rel=dest-next;std::memcpy(code+off+1,&rel,4);
}
void init_code(){
    code1=(unsigned char*)VirtualAlloc(nullptr,sizeof(original1),MEM_COMMIT|MEM_RESERVE,PAGE_EXECUTE_READWRITE);
    code2=(unsigned char*)VirtualAlloc(nullptr,sizeof(original2),MEM_COMMIT|MEM_RESERVE,PAGE_EXECUTE_READWRITE);
    check(code1 && code2);if(!code1||!code2)return;
    std::memcpy(code1,original1,sizeof(original1));std::memcpy(code2,original2,sizeof(original2));
    using namespace porsche;
    patch32(code1,sizeof(original1),0x005e940c,U(reinterpret_cast<std::uintptr_t>(&frame_control_enabled_005e940c)),1);
    patch32(code1,sizeof(original1),0x005e9410,U(reinterpret_cast<std::uintptr_t>(&frame_control_index_005e9410)),4);
    for(int off=0;off<8;off+=2)
        patch32(code1,sizeof(original1),0x005e9420+off,U(reinterpret_cast<std::uintptr_t>(frame_control_table_005e9420))+off,1);
    for(U va: {0x00412047u,0x0041205bu,0x0041206fu,0x00412082u})
        patch_call(code1,0x00412030,va,(void*)&frame_control_slot_release_005338d0);
    patch32(code2,sizeof(original2),0x0060c9f4,U(reinterpret_cast<std::uintptr_t>(&frame_callback_vector_0060c9f4)),3);
    patch32(code2,sizeof(original2),0x0060c9c4,U(reinterpret_cast<std::uintptr_t>(&frame_compact_vector_0060c9c4)),1);
}
struct Result { int n; int event[16]; U index; U end; };
Result run_control(bool original,int enabled,int mutate){
    using namespace porsche;
    frame_control_enabled_005e940c=enabled;frame_control_index_005e9410=0;
    frame_control_table_005e9420[0]={0,1,2,3};
    frame_control_table_005e9420[1]={4,5,6,7};
    release_count=0;mutate_release=mutate;
    if(original)((void(__cdecl*)())code1)(); else application_main_function_00412030();
    Result r{};r.n=release_count;r.index=frame_control_index_005e9410;
    for(int i=0;i<r.n;++i)r.event[i]=release_log[i];return r;
}
Result run_vector(bool original,int mutate){
    using namespace porsche;
    a[0].id=1;a[0].poll_result=1;a[1].id=2;a[1].poll_result=0;
    b[0].id=3;b[0].poll_result=1;b[1].id=4;b[1].poll_result=1;
    pairs_a[0]=U(reinterpret_cast<std::uintptr_t>(&a[0]));pairs_a[2]=U(reinterpret_cast<std::uintptr_t>(&a[1]));
    pairs_b[0]=U(reinterpret_cast<std::uintptr_t>(&b[0]));pairs_b[2]=U(reinterpret_cast<std::uintptr_t>(&b[1]));
    FrameVector_400 first{U(reinterpret_cast<std::uintptr_t>(pairs_a)),U(reinterpret_cast<std::uintptr_t>(pairs_a))+16};
    alt_vec={U(reinterpret_cast<std::uintptr_t>(pairs_b)),U(reinterpret_cast<std::uintptr_t>(pairs_b))+16};
    U compact_bytes[6]{};FrameVector_400 compact{U(reinterpret_cast<std::uintptr_t>(compact_bytes)),U(reinterpret_cast<std::uintptr_t>(compact_bytes))+20};
    frame_callback_vector_0060c9f4=&first;frame_compact_vector_0060c9c4=&compact;
    poll_count=0;notify_count=0;mutate_vector=mutate;
    if(original)((void(__cdecl*)())code2)(); else application_main_function_00425780();
    Result r{};r.n=poll_count+notify_count;r.end=compact.end;
    for(int i=0;i<poll_count;++i)r.event[i]=poll_log[i];
    for(int i=0;i<notify_count;++i)r.event[poll_count+i]=notify_log[i]+100;
    return r;
}
bool same(const Result&a,const Result&b){
    if(a.n!=b.n||a.index!=b.index||a.end!=b.end)return false;
    for(int i=0;i<a.n;++i)if(a.event[i]!=b.event[i])return false;
    return true;
}
extern "C" int main(){
    init_code();if(!code1||!code2)return 2;
    check(same(run_control(true,0,0),run_control(false,0,0)));
    check(same(run_control(true,1,0),run_control(false,1,0)));
    check(same(run_control(true,1,1),run_control(false,1,1)));
    check(same(run_vector(true,0),run_vector(false,0)));
    check(same(run_vector(true,1),run_vector(false,1)));
    char msg[80];int n=wsprintfA(msg,"checks=%d failures=%d\n",checks,failures);
    DWORD written=0;WriteFile(GetStdHandle(STD_OUTPUT_HANDLE),msg,n,&written,nullptr);
    return failures?1:0;
}
'''.replace("RAW1",arr(raw1)).replace("RAW2",arr(raw2)).replace(
        '#include "frame_loop_clusters_400.hpp"', '#include "'+header.as_posix()+'"')
    (OUT / "fixture.cpp").write_text(fixture,encoding="utf-8")
    vc = ROOT / "local/tools/BuildTools/VC/Tools/MSVC/14.44.35207"
    sdk = Path("C:/Program Files (x86)/Windows Kits/10")
    cl = vc / "bin/Hostx64/x86/cl.exe"
    link = vc / "bin/Hostx64/x86/link.exe"
    includes = [ROOT/"iterations/v2/001-original-recovery/source/include",ROOT/REL,vc/"include"]
    includes += [sdk/"Include/10.0.26100.0"/x for x in ("ucrt","shared","um")]
    cmd = [str(cl),"/nologo","/c","/std:c++17","/Od","/Oi","/GS-","/GR-","/EHsc","/TP","/W4","/utf-8"]
    cmd += ["/I"+str(x) for x in includes]
    cmd += ["/Fo"+str(OUT)+"\\",*[str(x) for x in sources],str(OUT/"fixture.cpp")]
    deps = source_hashes([Path(__file__), ROOT / "scripts/research/build-v2-compile-corpus.py",
                          ROOT / "scripts/research/v2_shared_manifests.py",
                          ROOT / "iterations/v2/001-original-recovery/source/recovered/functions.json"],
                         compiled_sources=[*sources, OUT / "fixture.cpp"])
    before = externalize(ROOT, dict(source_sha256=deps), "source", "crlf-to-lf")
    (OUT / "before.json").write_text(json.dumps(before,indent=2)+"\n",encoding="utf8")
    compile_receipt = capture(cmd, "compile")
    assert not re.search(rb"(?:warning|error) [CD]\d+", (OUT/"compile.log").read_bytes())
    libs=[vc/"lib/x86/libcmt.lib",vc/"lib/x86/libvcruntime.lib",sdk/"Lib/10.0.26100.0/ucrt/x86/libucrt.lib",sdk/"Lib/10.0.26100.0/um/x86/kernel32.lib",sdk/"Lib/10.0.26100.0/um/x86/user32.lib"]
    exe=OUT/"fixture.exe"
    cmd=[link,"/nologo","/MACHINE:X86","/SUBSYSTEM:CONSOLE","/NODEFAULTLIB","/OUT:"+str(exe)]
    cmd += [OUT/(x.stem+".obj") for x in selected]+[OUT/"fixture.obj"]+libs
    link_receipt = capture(cmd, "link")
    native_receipt = capture([exe], "native")
    assert (OUT/"native.log").read_text().strip() == "checks=18 failures=0"
    spec=importlib.util.spec_from_file_location("coff310",ROOT/"scripts/research/build-v2-compile-corpus.py")
    coff=importlib.util.module_from_spec(spec);spec.loader.exec_module(coff)
    objects={p.stem:dict(path=(OUT/(p.stem+".obj")).relative_to(ROOT).as_posix(),
                        sha256=sha(OUT/(p.stem+".obj")), symbols=coff.coff_symbols(OUT/(p.stem+".obj"))) for p in sources}
    assert all(not x["symbols"]["common"] and not x["symbols"]["weak"] for x in objects.values())
    for va in ("00412030","00425780"):
        assert f"?application_main_function_{va}@porsche@@YAXXZ" in objects[va]["symbols"]["defined"]
    after=source_hashes([Path(__file__), ROOT/"scripts/research/build-v2-compile-corpus.py",
                         ROOT/"scripts/research/v2_shared_manifests.py",
                         ROOT/"iterations/v2/001-original-recovery/source/recovered/functions.json"],
                        compiled_sources=[*sources,OUT/"fixture.cpp"])
    assert deps==after, "Source drift"
    report=dict(schema=1, pr=3, upstream_commit=PR, original_sha256=PE_SHA,
                original_body_hex={"00412030":raw1.hex(),"00425780":raw2.hex()},
                source_sha256=deps, source_count=len(sources), source_unchanged=True,
                native_cases=5, assertions=18, native_original_bytes=226,
                native_vas=["00412030","00425780"], untested_native_vas=[x.stem for x in sources if x not in selected],
                objects=objects, receipts=[compile_receipt,link_receipt,native_receipt],
                fixture_sha256=sha(OUT/"fixture.cpp"), executable_sha256=sha(exe),
                tool_sha256={str(x):sha(x) for x in [cl,link,*libs]},
                game_executed=False, production_data_providers=0)
    report=externalize(ROOT,report,"source","crlf-to-lf",before["source_manifest"])
    ManifestReader(ROOT).verify(report,"source",expected_hash_mode="crlf-to-lf")
    target=RUN/("native-"+args.attempt+".json")
    assert not target.exists()
    target.write_text(json.dumps(report,indent=2)+"\n",encoding="utf8")
    print(json.dumps(dict(compiled_sources=21,native_cases=5,assertions=18,original_bytes=226)))


if __name__=="__main__": main()
