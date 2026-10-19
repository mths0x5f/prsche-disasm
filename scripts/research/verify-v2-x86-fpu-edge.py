"""Native regressions for PR20 review: NaN status, signed zero, rejected widths."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import traceback

ROOT = Path(__file__).resolve().parents[2]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--attempt', required=True)
    args = parser.parse_args()
    assert args.attempt.isdigit() and len(args.attempt) == 3
    work = ROOT / 'local/experiments/v2-x86-fpu-edge' / ('attempt-' + args.attempt)
    work.mkdir(parents=True, exist_ok=False)
    helper = module('helpers_edge', ROOT / 'scripts/research/verify-v2-scalar-fill-317.py')
    backend_path = ROOT / 'scripts/research/x86-cpp-backend-fpu.py'
    backend = module('backend_edge', backend_path)
    sha, write = helper.sha, helper.write
    receipt = dict(schema=1, status='started', commands=[], rejected=[])
    try:
        for name, raw in [('fld-m80', 'db28c3'), ('fstp-m80', 'db38c3'), ('fsqrt', 'd9fac3')]:
            try:
                backend.translate(bytes.fromhex(raw), 0x20001000)
            except ValueError as error:
                assert 'Unsupported' in str(error)
                receipt['rejected'].append(dict(name=name, reason=str(error)))
            else:
                raise AssertionError(name + ' was silently accepted')
        write(work / 'machine257.h', backend.HEADER)
        parts = []
        for address, raw in [(0x20001000, 'd9e1c3'), (0x20002000, 'ded9dfe0c3')]:
            code, _ = backend.translate(bytes.fromhex(raw), address)
            parts.append(code)
        write(work / 'translated.cpp', '\n'.join(parts))
        fixture = r'''#include "machine257.h"
extern void translated_20001000(Machine257&);
extern void translated_20002000(Machine257&);
U read257(U address,U size){ U v=0;for(U i=0;i<size;++i)v|=U(reinterpret_cast<B*>(address)[i])<<(8*i);return v; }
void write257(U address,U size,U value){for(U i=0;i<size;++i)reinterpret_cast<B*>(address)[i]=B(value>>(8*i));}
void dispatch257(Machine257&,U){}
static double from_bits(U64 bits){double x;for(U i=0;i<8;++i)reinterpret_cast<B*>(&x)[i]=B(bits>>(8*i));return x;}
static U64 bits(double x){U64 value=0;for(U i=0;i<8;++i)value|=U64(reinterpret_cast<B*>(&x)[i])<<(8*i);return value;}
static Machine257 seed(double a,double b,U* stack){Machine257 s={};s.budget=32;s.r[4]=U(stack);s.fpu_top=6;s.fpu_cw=0x37f;s.st[6]=a;s.st[7]=b;return s;}
int main(){
 const U64 values[]={0,0x8000000000000000ull,0xbff0000000000000ull,0x3ff0000000000000ull,0xfff8000000001234ull,0x7ff8000000001234ull};
 U stack[]={0x12345678};
 for(U64 v:values){
  double input=from_bits(v),expected=0;
  __asm {fninit
   fld qword ptr input
   fabs
   fstp qword ptr expected}
  auto s=seed(input,1.0,stack);translated_20001000(s);
  if(bits(fpu_st(s))!=bits(expected)||s.stop!=Stop257::Returned||s.pc!=stack[0]||s.r[4]!=U(stack+1))return 11;
 }
 const U64 pairs[][2]={{0x7ff8000000000000ull,0x3ff0000000000000ull},{0x3ff0000000000000ull,0x7ff8000000000000ull},
  {0x7ff8000000000000ull,0x7ff8000000000000ull},{0xbff0000000000000ull,0x3ff0000000000000ull},
  {0x3ff0000000000000ull,0xbff0000000000000ull},{0,0x8000000000000000ull},
  {0x3ff0000000000000ull,0x3ff0000000000000ull},{0xfff8000000000000ull,0}};
 for(const auto& pair:pairs){
  double a=from_bits(pair[0]),b=from_bits(pair[1]);unsigned short sw=0;
  __asm {fninit
   fld qword ptr b
   fld qword ptr a
   fcompp
   fnstsw sw}
  auto s=seed(a,b,stack);translated_20002000(s);
  if(((s.r[0]^sw)&0x7f01u)!=0||s.fpu_top!=0||s.stop!=Stop257::Returned||s.pc!=stack[0])return 12;
 }
 __asm {fninit}
 return 0;
}
'''
        write(work / 'fixture.cpp', fixture)
        vc, sdk = helper.VC, helper.SDK
        cl, link = [vc / 'bin/Hostx64/x86' / (x + '.exe') for x in ('cl', 'link')]
        libraries = [vc / 'lib/x86/libcmt.lib', vc / 'lib/x86/libvcruntime.lib',
                     sdk / 'Lib/10.0.26100.0/ucrt/x86/libucrt.lib', sdk / 'Lib/10.0.26100.0/um/x86/kernel32.lib']
        inputs = [Path(__file__), Path(helper.__file__), backend_path, backend.BASELINE_PATH,
                  backend.BASELINE_PATH.with_name('x86-cpp-backend-257.py'),
                  *[work / name for name in ('machine257.h', 'translated.cpp', 'fixture.cpp')]]
        receipt['inputs_sha256'] = {p.resolve().relative_to(ROOT).as_posix(): sha(p) for p in inputs}
        receipt['tools_sha256'] = {str(p): sha(p) for p in (cl, link)}
        receipt['libraries_sha256'] = {str(p): sha(p) for p in libraries}
        objects = [work / 'translated.obj', work / 'fixture.obj']
        exe = work / 'fixture.exe'
        commands = [[cl, '/nologo', '/c', '/std:c++17', '/Od', '/MT', '/GS-', '/EHsc', '/utf-8',
                     '/Fo' + str(work) + '\\', work / 'translated.cpp', work / 'fixture.cpp'],
                    [link, '/nologo', '/MACHINE:X86', '/SUBSYSTEM:CONSOLE', '/NODEFAULTLIB',
                     '/OUT:' + str(exe), *objects, *libraries], [exe]]
        for number, command in enumerate(commands):
            run = subprocess.run(list(map(str, command)), cwd=work, capture_output=True, text=True, timeout=60)
            log = work / ('command-' + str(number) + '.log')
            write(log, run.stdout + run.stderr)
            receipt['commands'].append(dict(argv=list(map(str, command)), exit_code=run.returncode,
                                            log=log.name, log_sha256=sha(log)))
            assert run.returncode == 0, str(log)
        receipt.update(status='pass', native_cases=14, expected_rejections=3,
                       objects_sha256={p.name: sha(p) for p in objects}, exe_sha256=sha(exe))
    except Exception as error:
        receipt.update(status='fail', error=str(error))
        write(work / 'error.log', traceback.format_exc())
    write(work / 'receipt.json', json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(status=receipt['status'], receipt=(work / 'receipt.json').relative_to(ROOT).as_posix())))
    if receipt['status'] != 'pass':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
