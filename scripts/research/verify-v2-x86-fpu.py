"""Bounded hardware-oracle checks for the experimental lowering backend.

107 supported fragments run 109568 cases. One additional FSQRT fragment must
be rejected explicitly until guest x87 status/control-word behavior is modeled.
This fixture does not establish whole-game or complete x87 correctness.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
BACKEND_REL = 'scripts/research/x86-cpp-backend-fpu.py'
WORK_DIR = ROOT / 'local/experiments/v2-x86-fpu'

# Synthetic fragments: integer, x87, SSE and MMX
FRAGMENTS = [
    # 0..5 Unary
    ('inc-ah', 'fec4c3', 'inc ah\n ret', 'unary', 8),
    ('inc-ax', '6640c3', 'inc ax\n ret', 'unary', 16),
    ('inc-eax', '40c3', 'inc eax\n ret', 'unary', 32),
    ('dec-ah', 'feccc3', 'dec ah\n ret', 'unary', 8),
    ('dec-ax', '6648c3', 'dec ax\n ret', 'unary', 16),
    ('dec-eax', '48c3', 'dec eax\n ret', 'unary', 32),
    # 6..15 Shifts
    ('shl-eax-1', 'd1e0c3', 'shl eax, 1\n ret', 'shift', 32),
    ('shl-eax-cl', 'd3e0c3', 'shl eax, cl\n ret', 'shift_cl', 32),
    ('shl-ah-1', 'd0e4c3', 'shl ah, 1\n ret', 'shift', 8),
    ('shl-ax-1', '66d1e0c3', 'shl ax, 1\n ret', 'shift', 16),
    ('shr-eax-1', 'd1e8c3', 'shr eax, 1\n ret', 'shift', 32),
    ('shr-eax-cl', 'd3e8c3', 'shr eax, cl\n ret', 'shift_cl', 32),
    ('shr-ah-1', 'd0ecc3', 'shr ah, 1\n ret', 'shift', 8),
    ('sar-eax-1', 'd1f8c3', 'sar eax, 1\n ret', 'shift', 32),
    ('sar-eax-cl', 'd3f8c3', 'sar eax, cl\n ret', 'shift_cl', 32),
    ('sar-ah-1', 'd0fcc3', 'sar ah, 1\n ret', 'shift', 8),
    # 16 CDQ
    ('cdq', '99c3', 'cdq\n ret', 'cdq', 32),
    # 17..26 SETcc
    ('sete-al', '0f94c0c3', 'sete al\n ret', 'setcc', 8),
    ('setne-al', '0f95c0c3', 'setne al\n ret', 'setcc', 8),
    ('setl-al', '0f9cc0c3', 'setl al\n ret', 'setcc', 8),
    ('setle-al', '0f9ec0c3', 'setle al\n ret', 'setcc', 8),
    ('setg-al', '0f9fc0c3', 'setg al\n ret', 'setcc', 8),
    ('setge-al', '0f9dc0c3', 'setge al\n ret', 'setcc', 8),
    ('setb-al', '0f92c0c3', 'setb al\n ret', 'setcc', 8),
    ('setae-al', '0f93c0c3', 'setae al\n ret', 'setcc', 8),
    ('setbe-al', '0f96c0c3', 'setbe al\n ret', 'setcc', 8),
    ('seta-al', '0f97c0c3', 'seta al\n ret', 'setcc', 8),
    # 27..36 Mul / Div / Rep / Leave
    ('imul-2op-ecx-eax', '0fafc8c3', 'imul ecx, eax\n ret', 'imul_2op', 32),
    ('imul-3op-eax-imm', '6bc03cc3', 'imul eax, eax, 0x3c\n ret', 'imul_3op', 32),
    ('imul-3op-eax-ecx-imm', '6bc164c3', 'imul eax, ecx, 100\n ret', 'imul_3op', 32),
    ('imul-1op-ecx', 'f7e9c3', 'imul ecx\n ret', 'imul_1op', 32),
    ('mul-1op-ecx', 'f7e1c3', 'mul ecx\n ret', 'mul_1op', 32),
    ('idiv-1op-ecx', 'f7f9c3', 'idiv ecx\n ret', 'idiv_1op', 32),
    ('leave', 'c9c3', 'leave\n ret', 'leave', 32),
    ('repne-scasb', 'f2aec3', 'repne scasb\n ret', 'repne_scasb', 8),
    ('rep-stosd', 'f3abc3', 'rep stosd\n ret', 'rep_stosd', 32),
    ('rep-movsd', 'f3a5c3', 'rep movsd\n ret', 'rep_movsd', 32),
    # 37..60 FPU Fragments
    ('fld-mem32', 'd900c3', 'fld dword ptr [eax]\n ret', 'fpu_load_mem32', 32),
    ('fld-mem64', 'dd00c3', 'fld qword ptr [eax]\n ret', 'fpu_load_mem64', 32),
    ('fld-st1', 'd9c1c3', 'fld st(1)\n ret', 'fpu_load_st1', 32),
    ('fild-mem32', 'db00c3', 'fild dword ptr [eax]\n ret', 'fpu_iload_mem32', 32),
    ('fstp-mem32', 'd918c3', 'fstp dword ptr [eax]\n ret', 'fpu_store_mem32', 32),
    ('fstp-mem64', 'dd18c3', 'fstp qword ptr [eax]\n ret', 'fpu_store_mem64', 32),
    ('fistp-mem32', 'db18c3', 'fistp dword ptr [eax]\n ret', 'fpu_istore_mem32', 32),
    ('fadd-mem32', 'd800c3', 'fadd dword ptr [eax]\n ret', 'fpu_op_mem32', 32),
    ('fadd-st1', 'd8c1c3', 'fadd st(0), st(1)\n ret', 'fpu_op_st1', 32),
    ('faddp', 'dec1c3', 'faddp st(1), st(0)\n ret', 'fpu_opp_st1', 32),
    ('fsub-mem32', 'd820c3', 'fsub dword ptr [eax]\n ret', 'fpu_op_mem32', 32),
    ('fsubr-mem32', 'd828c3', 'fsubr dword ptr [eax]\n ret', 'fpu_op_mem32', 32),
    ('fsubp', 'dee9c3', 'fsubp st(1), st(0)\n ret', 'fpu_opp_st1', 32),
    ('fmul-mem32', 'd808c3', 'fmul dword ptr [eax]\n ret', 'fpu_op_mem32', 32),
    ('fmulp', 'dec9c3', 'fmulp st(1), st(0)\n ret', 'fpu_opp_st1', 32),
    ('fdiv-mem32', 'd830c3', 'fdiv dword ptr [eax]\n ret', 'fpu_op_mem32', 32),
    ('fdivr-mem32', 'd838c3', 'fdivr dword ptr [eax]\n ret', 'fpu_op_mem32', 32),
    ('fdivp', 'def9c3', 'fdivp st(1), st(0)\n ret', 'fpu_opp_st1', 32),
    ('fchs', 'd9e0c3', 'fchs\n ret', 'fpu_unary', 32),
    ('fsqrt', 'd9fac3', 'fsqrt\n ret', 'fpu_unary', 32),
    ('fxch-st1', 'd9c9c3', 'fxch st(1)\n ret', 'fpu_xch_st1', 32),
    ('fcomp-mem32', 'd818c3', 'fcomp dword ptr [eax]\n ret', 'fpu_comp_mem32', 32),
    ('fcompp', 'ded9c3', 'fcompp\n ret', 'fpu_compp', 32),
    ('fnstsw-ax', 'dfe0c3', 'fnstsw ax\n ret', 'fpu_status_ax', 32),
    ('movss-load', 'f30f1000c3', 'movss xmm0, dword ptr [eax]\n ret', 'simd_sse', 32),
    ('movss-store', 'f30f1108c3', 'movss dword ptr [eax], xmm1\n ret', 'simd_sse', 32),
    ('movss-reg', 'f30f10d4c3', 'movss xmm2, xmm4\n ret', 'simd_sse', 32),
    ('movaps-load', '0f2808c3', 'movaps xmm1, xmmword ptr [eax]\n ret', 'simd_sse', 32),
    ('movaps-reg', '0f28c3c3', 'movaps xmm0, xmm3\n ret', 'simd_sse', 32),
    ('movaps-store', '0f2910c3', 'movaps xmmword ptr [eax], xmm2\n ret', 'simd_sse', 32),
    ('movups-load', '0f1008c3', 'movups xmm1, xmmword ptr [eax]\n ret', 'simd_sse', 32),
    ('movlps-load', '0f1200c3', 'movlps xmm0, qword ptr [eax]\n ret', 'simd_sse', 32),
    ('movlps-store', '0f1300c3', 'movlps qword ptr [eax], xmm0\n ret', 'simd_sse', 32),
    ('movntps-store', '0f2b08c3', 'movntps xmmword ptr [eax], xmm1\n ret', 'simd_sse', 32),
    ('addss-reg', 'f30f58c1c3', 'addss xmm0, xmm1\n ret', 'simd_sse', 32),
    ('addss-mem', 'f30f5808c3', 'addss xmm1, dword ptr [eax]\n ret', 'simd_sse', 32),
    ('addps-reg', '0f58c1c3', 'addps xmm0, xmm1\n ret', 'simd_sse', 32),
    ('addps-mem', '0f5818c3', 'addps xmm3, xmmword ptr [eax]\n ret', 'simd_sse', 32),
    ('subss-reg', 'f30f5ce2c3', 'subss xmm4, xmm2\n ret', 'simd_sse', 32),
    ('subss-mem', 'f30f5c10c3', 'subss xmm2, dword ptr [eax]\n ret', 'simd_sse', 32),
    ('subps-reg', '0f5ce0c3', 'subps xmm4, xmm0\n ret', 'simd_sse', 32),
    ('subps-mem', '0f5c08c3', 'subps xmm1, xmmword ptr [eax]\n ret', 'simd_sse', 32),
    ('mulss-reg', 'f30f59c1c3', 'mulss xmm0, xmm1\n ret', 'simd_sse', 32),
    ('mulss-mem', 'f30f5910c3', 'mulss xmm2, dword ptr [eax]\n ret', 'simd_sse', 32),
    ('mulss-self', 'f30f59ffc3', 'mulss xmm7, xmm7\n ret', 'simd_sse', 32),
    ('mulps-reg', '0f59dac3', 'mulps xmm3, xmm2\n ret', 'simd_sse', 32),
    ('mulps-mem', '0f5920c3', 'mulps xmm4, xmmword ptr [eax]\n ret', 'simd_sse', 32),
    ('shufps-0', '0fc6c000c3', 'shufps xmm0, xmm0, 0\n ret', 'simd_sse', 32),
    ('shufps-1b', '0fc6db1bc3', 'shufps xmm3, xmm3, 1bh\n ret', 'simd_sse', 32),
    ('shufps-2reg', '0fc6ca4ec3', 'shufps xmm1, xmm2, 4eh\n ret', 'simd_sse', 32),
    ('cvtsi2ss', 'f30f2af1c3', 'cvtsi2ss xmm6, ecx\n ret', 'simd_sse', 32),
    ('cvtpi2ps-mem', '0f2a28c3', 'cvtpi2ps xmm5, qword ptr [eax]\n ret', 'simd_sse', 32),
    ('stmxcsr', '0fae18c3', 'stmxcsr dword ptr [eax]\n ret', 'simd_sse', 32),
    ('ldmxcsr', '0fae10c3', 'ldmxcsr dword ptr [eax]\n ret', 'simd_ldmxcsr', 32),
    ('movd-load', '0f6e00c3', 'movd mm0, dword ptr [eax]\n ret', 'simd_mmx', 32),
    ('movd-reg', '0f6ec1c3', 'movd mm0, ecx\n ret', 'simd_mmx', 32),
    ('movd-store', '0f7e08c3', 'movd dword ptr [eax], mm1\n ret', 'simd_mmx', 32),
    ('movq-load', '0f6f00c3', 'movq mm0, qword ptr [eax]\n ret', 'simd_mmx', 32),
    ('movq-reg', '0f6fc8c3', 'movq mm1, mm0\n ret', 'simd_mmx', 32),
    ('movq-store', '0f7f10c3', 'movq qword ptr [eax], mm2\n ret', 'simd_mmx', 32),
    ('por', '0febc1c3', 'por mm0, mm1\n ret', 'simd_mmx', 32),
    ('psllq-20', '0f73f020c3', 'psllq mm0, 20h\n ret', 'simd_mmx', 32),
    ('psllq-40', '0f73f040c3', 'psllq mm0, 40h\n ret', 'simd_mmx', 32),
    ('pslld-10', '0f72f110c3', 'pslld mm1, 10h\n ret', 'simd_mmx', 32),
    ('psrad-10', '0f72e110c3', 'psrad mm1, 10h\n ret', 'simd_mmx', 32),
    ('psrad-21', '0f72e121c3', 'psrad mm1, 21h\n ret', 'simd_mmx', 32),
    ('punpckldq-mem', '0f6200c3', 'punpckldq mm0, dword ptr [eax]\n ret', 'simd_mmx', 32),
    ('punpckldq-reg', '0f62fcc3', 'punpckldq mm7, mm4\n ret', 'simd_mmx', 32),
    ('punpcklwd', '0f61c8c3', 'punpcklwd mm1, mm0\n ret', 'simd_mmx', 32),
    ('punpckhwd', '0f69d0c3', 'punpckhwd mm2, mm0\n ret', 'simd_mmx', 32),
    ('emms-after-mmx', '0f6fc80f77c3', 'movq mm1, mm0\n emms\n ret', 'simd_mmx', 32),
]


def find_toolchain():
    vswhere = Path(os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)')) / 'Microsoft Visual Studio/Installer/vswhere.exe'
    vs_install = None
    if vswhere.exists():
        try:
            out = subprocess.check_output([str(vswhere), '-latest', '-products', '*', '-format', 'json'], text=True)
            info = json.loads(out)
            if info:
                vs_install = Path(info[0]['installationPath'])
        except Exception:
            pass

    if not vs_install:
        cand = Path(r'C:\Program Files\Microsoft Visual Studio\18\Community')
        if cand.exists():
            vs_install = cand

    if not vs_install:
        raise RuntimeError('Visual Studio installation not found')

    vc_tools_dir = vs_install / 'VC/Tools/MSVC'
    msvc_versions = sorted(vc_tools_dir.glob('*'), reverse=True)
    if not msvc_versions:
        raise RuntimeError(f'No MSVC toolchains found in {vc_tools_dir}')
    msvc_dir = msvc_versions[0]

    cl = msvc_dir / 'bin/Hostx64/x86/cl.exe'
    if not cl.exists():
        cl = msvc_dir / 'bin/Hostx86/x86/cl.exe'
    link = msvc_dir / 'bin/Hostx64/x86/link.exe'
    if not link.exists():
        link = msvc_dir / 'bin/Hostx86/x86/link.exe'
    msvc_lib = msvc_dir / 'lib/x86'

    sdk_base = Path(os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)')) / 'Windows Kits/10/Lib'
    sdk_versions = sorted(sdk_base.glob('*.*.*.*'), reverse=True)
    if not sdk_versions:
        raise RuntimeError(f'No Windows 10 SDKs found in {sdk_base}')
    sdk_dir = sdk_versions[0]

    return {
        'cl': cl,
        'link': link,
        'msvc_lib': msvc_lib,
        'sdk_ucrt': sdk_dir / 'ucrt/x86',
        'sdk_um': sdk_dir / 'um/x86'
    }


def main():
    global WORK_DIR
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true', help='Output JSON summary')
    parser.add_argument('--output-dir', type=Path, help='Use a fresh directory for this verification attempt')
    args = parser.parse_args()

    if args.output_dir:
        WORK_DIR = args.output_dir.resolve()
        WORK_DIR.mkdir(parents=True, exist_ok=False)
    else:
        parent = WORK_DIR
        attempt = 1
        while (parent / f'attempt-{attempt:03d}').exists():
            attempt += 1
        WORK_DIR = parent / f'attempt-{attempt:03d}'
        WORK_DIR.mkdir(parents=True, exist_ok=False)
    objects_dir = WORK_DIR / 'objects'
    objects_dir.mkdir(parents=True, exist_ok=True)

    spec = importlib.util.spec_from_file_location('backend_fpu', ROOT / BACKEND_REL)
    backend = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(backend)

    translated_sources = []
    dispatch_cases = []

    expected_unsupported = ('fsqrt',)  # guest exception/CW state is not yet exact
    for i, (name, raw_hex, asm_text, kind, bits) in enumerate(FRAGMENTS):
        if name in expected_unsupported:
            try:
                backend.translate(bytes.fromhex(raw_hex), 0x20001000 + i * 0x100)
            except ValueError as error:
                if 'Unsupported fsqrt' not in str(error):
                    raise
            else:
                raise AssertionError('FSQRT unexpectedly lowered without guest-status proof')
            continue
        entry_va = 0x20001000 + i * 0x100
        raw_bytes = bytes.fromhex(raw_hex)
        cpp_source, witness = backend.translate(raw_bytes, entry_va)
        cpp_source = cpp_source.replace(f'void translated_{entry_va:08x}(Machine257&s)', f'void frag_{i}(Machine257&s)')
        translated_sources.append(cpp_source)
        dispatch_cases.append(f'        case 0x{entry_va:08x}u: frag_{i}(s); break;')

    dispatcher_cpp = f'''
void dispatch257(Machine257& s, U target) {{
    switch (target) {{
{chr(10).join(dispatch_cases)}
        default: s.stop = Stop257::MissingEntry; return;
    }}
}}
'''

    oracle_funcs = []
    targets_list = []
    for i, (name, raw_hex, asm_text, kind, bits) in enumerate(FRAGMENTS):
        oracle_funcs.append(f'''__declspec(naked) void oracle_frag_{i}() {{
    __asm {{
{chr(10).join("        " + l for l in asm_text.splitlines())}
    }}
}}''')
        targets_list.append(f'reinterpret_cast<void*>(&oracle_frag_{i})')

    fixture_cpp = f'''#include "machine257.h"

extern "C" int __cdecl memcmp(const void*,const void*,unsigned int);
#pragma intrinsic(memcmp)

extern "C" __declspec(dllimport) void __stdcall ExitProcess(U);
extern "C" __declspec(dllimport) void* __stdcall CreateFileA(const char*,U,U,void*,U,U,void*);
extern "C" __declspec(dllimport) int __stdcall WriteFile(void*,const void*,U,U*,void*);
extern "C" __declspec(dllimport) int __stdcall CloseHandle(void*);
extern "C" __declspec(dllimport) void* __stdcall GetStdHandle(int);

static inline bool str_eq(const char* a, const char* b) {{
    while (*a && *b && *a == *b) {{ ++a; ++b; }}
    return *a == *b;
}}

static inline void print_str(const char* s) {{
    void* h = GetStdHandle(-11);
    U written = 0;
    U len = 0; while (s[len]) ++len;
    WriteFile(h, s, len, &written, 0);
}}

static inline void print_num(U v) {{
    char buf[12]; int i = 10; buf[11] = 0;
    if (!v) {{ buf[--i] = '0'; }}
    while (v) {{ buf[--i] = '0' + (v % 10); v /= 10; }}
    void* h = GetStdHandle(-11); U written = 0;
    WriteFile(h, buf + i, 11 - i, &written, 0);
}}

U saved_sp, saved_bp, saved_bx, saved_si, saved_di;
U seed_regs[8], seen_regs[8], seed_flags, seen_flags, target_addr, continuation_addr, guest_sp;
double seed_st0, seed_st1, seen_st0, seen_st1;
unsigned short seen_fpu_status;
U failures = 0, total_cases = 0;
__declspec(align(16)) B stack_arena[256];
B before_stack[256], native_stack[256];
U seed_xmm[32], seen_xmm[32], seed_mxcsr, seen_mxcsr, host_mxcsr, seed_mmx;
U64 seed_mm[8], seen_mm[8];
const U halt_pc = 0x0badf00du;

U current_test_id = 0;
const char* simd_kinds[] = {{ {', '.join(chr(34) + f[3] + chr(34) for f in FRAGMENTS[61:])} }};
U last_failed_id = 9999;
void require(bool val, const char* reason = 0) {{
    if (!val) {{
        if (current_test_id != last_failed_id) {{
            last_failed_id = current_test_id;
            print_str("FAIL id="); print_num(current_test_id);
            if (reason) {{ print_str(" expr="); print_str(reason); }}
            print_str("\\n");
        }}
        ++failures;
    }}
}}
#define require_msg(v) require((v), #v)

bool valid_addr(U a, U n) {{
    U base = reinterpret_cast<U>(stack_arena);
    return (n == 1u || n == 2u || n == 4u || n == 8u) && a >= base && a - base <= 256u - n;
}}
U read257(U a, U n) {{
    U v = 0; require(valid_addr(a, n));
    if (valid_addr(a, n)) memcpy(&v, reinterpret_cast<const B*>(a), n);
    return v;
}}
void write257(U a, U n, U v) {{
    require(valid_addr(a, n));
    if (valid_addr(a, n)) memcpy(reinterpret_cast<B*>(a), &v, n);
}}

__declspec(naked) void capture_state() {{
    __asm {{
        mov seen_regs[0], eax
        mov seen_regs[4], ecx
        mov seen_regs[8], edx
        mov seen_regs[12], ebx
        mov seen_regs[16], esp
        mov seen_regs[20], ebp
        mov seen_regs[24], esi
        mov seen_regs[28], edi
        fnstsw seen_fpu_status
        fstp seen_st0
        fstp seen_st1
        movups xmmword ptr seen_xmm[0], xmm0
        movups xmmword ptr seen_xmm[16], xmm1
        movups xmmword ptr seen_xmm[32], xmm2
        movups xmmword ptr seen_xmm[48], xmm3
        movups xmmword ptr seen_xmm[64], xmm4
        movups xmmword ptr seen_xmm[80], xmm5
        movups xmmword ptr seen_xmm[96], xmm6
        movups xmmword ptr seen_xmm[112], xmm7
        stmxcsr seen_mxcsr
        ldmxcsr host_mxcsr
        movq qword ptr seen_mm[0], mm0
        movq qword ptr seen_mm[8], mm1
        movq qword ptr seen_mm[16], mm2
        movq qword ptr seen_mm[24], mm3
        movq qword ptr seen_mm[32], mm4
        movq qword ptr seen_mm[40], mm5
        movq qword ptr seen_mm[48], mm6
        movq qword ptr seen_mm[56], mm7
        emms
        mov esp, saved_sp
        pushfd
        pop seen_flags
        mov ebx, saved_bx
        mov esi, saved_si
        mov edi, saved_di
        mov ebp, saved_bp
        jmp dword ptr continuation_addr
    }}
}}

__declspec(naked) void native_edge() {{
    __asm {{
        mov saved_sp, esp
        mov saved_bp, ebp
        mov saved_bx, ebx
        mov saved_si, esi
        mov saved_di, edi
        mov eax, offset resume_point
        mov continuation_addr, eax
        fninit
        fld seed_st1
        fld seed_st0
        movups xmm0, xmmword ptr seed_xmm[0]
        movups xmm1, xmmword ptr seed_xmm[16]
        movups xmm2, xmmword ptr seed_xmm[32]
        movups xmm3, xmmword ptr seed_xmm[48]
        movups xmm4, xmmword ptr seed_xmm[64]
        movups xmm5, xmmword ptr seed_xmm[80]
        movups xmm6, xmmword ptr seed_xmm[96]
        movups xmm7, xmmword ptr seed_xmm[112]
        stmxcsr host_mxcsr
        ldmxcsr seed_mxcsr
        cmp seed_mmx, 0
        je no_mmx_seed
        movq mm0, qword ptr seed_mm[0]
        movq mm1, qword ptr seed_mm[8]
        movq mm2, qword ptr seed_mm[16]
        movq mm3, qword ptr seed_mm[24]
        movq mm4, qword ptr seed_mm[32]
        movq mm5, qword ptr seed_mm[40]
        movq mm6, qword ptr seed_mm[48]
        movq mm7, qword ptr seed_mm[56]
    no_mmx_seed:
        push seed_flags
        popfd
        mov eax, seed_regs[0]
        mov ecx, seed_regs[4]
        mov edx, seed_regs[8]
        mov ebx, seed_regs[12]
        mov ebp, seed_regs[20]
        mov esi, seed_regs[24]
        mov edi, seed_regs[28]
        mov esp, guest_sp
        jmp dword ptr target_addr
    resume_point:
        ret
    }}
}}

{chr(10).join(oracle_funcs)}

void* targets[{len(FRAGMENTS)}] = {{
    {", ".join(targets_list)}
}};

U edge_val(U n, U bits) {{
    U mask = bits == 8 ? 0xffu : (bits == 16 ? 0xffffu : 0xffffffffu);
    U sign = (mask >> 1) + 1u;
    switch(n) {{
        case 0: return 0;
        case 1: return 1;
        case 2: return mask;
        case 3: return sign - 1u;
        case 4: return sign;
        case 5: return sign + 1u;
        case 6: return mask - 1u;
        default: return 2;
    }}
}}

void run_test(U id, const char* kind, U width, U val_a, U val_b, U flag_seed) {{
    current_test_id = id;
    U entry = 0x20001000u + id * 0x100u;
    U sp = reinterpret_cast<U>(stack_arena + 192);
    U capture = reinterpret_cast<U>(&capture_state);

    for (U i = 0; i < 256; ++i) stack_arena[i] = static_cast<B>(i * 37u + id * 19u + val_a);
    write257(sp, 4u, capture);

    // Seed registers
    for (U i = 0; i < 8; ++i) seed_regs[i] = 0x13579bdfu * (i + 1u);
    seed_regs[4] = sp;

    // Setup inputs
    if (width == 8) seed_regs[0] = (seed_regs[0] & 0xffff00ffu) | ((val_a & 0xffu) << 8u); // AH
    else if (width == 16) seed_regs[0] = (seed_regs[0] & 0xffff0000u) | (val_a & 0xffffu); // AX
    else seed_regs[0] = val_a; // EAX

    seed_regs[1] = val_b; // ECX

    // Float values for FPU
    float f_val = (static_cast<int>(val_a) % 100) + 0.25f;
    double d_val = (static_cast<int>(val_b) % 100) + 0.5;
    if (f_val == 0.0f) f_val = 1.0f;
    if (d_val == 0.0) d_val = 2.0;

    U mem_addr = reinterpret_cast<U>(stack_arena + 16);
    write_f32(mem_addr, f_val);
    write_f64(mem_addr + 8, d_val);

    seed_st0 = static_cast<double>(f_val);
    seed_st1 = d_val;

    U expected_sp = sp + 4u;
    if (str_eq(kind, "leave")) {{
        U bp = sp - 16u;
        write257(bp, 4u, 0x55aa3322u);
        write257(bp + 4u, 4u, capture);
        seed_regs[5] = bp;
        expected_sp = bp + 8u;
    }} else if (str_eq(kind, "repne_scasb")) {{
        seed_regs[0] = (seed_regs[0] & 0xffffff00u) | 0x42u;
        seed_regs[7] = reinterpret_cast<U>(stack_arena + 16);
        seed_regs[1] = val_b & 0x0fu;
        stack_arena[16 + 5] = 0x42;
    }} else if (str_eq(kind, "rep_stosd")) {{
        seed_regs[7] = reinterpret_cast<U>(stack_arena + 16);
        seed_regs[1] = val_b & 0x07u;
    }} else if (str_eq(kind, "rep_movsd")) {{
        seed_regs[6] = reinterpret_cast<U>(stack_arena + 16);
        seed_regs[7] = reinterpret_cast<U>(stack_arena + 64);
        seed_regs[1] = val_b & 0x07u;
    }} else if (str_eq(kind, "idiv_1op")) {{
        int div = (int)val_b;
        if (div == 0) div = 7;
        if (div == -1) div = 3;
        seed_regs[1] = (U)div;
        int num = (int)val_a;
        seed_regs[0] = (U)num;
        seed_regs[2] = (num < 0) ? 0xffffffffu : 0u;
    }} else if (kind[0] == 'f' && kind[1] == 'p' && kind[2] == 'u') {{
        seed_regs[0] = mem_addr;
    }}

    // SIMD seeds: normal floats, edge bit patterns (NaN, denormal, -0, max), all
    // four MXCSR rounding modes and FTZ+DAZ.
    for (U k = 0; k < 32u; ++k) {{
        U a = val_a + k * 0x01010101u, b = val_b ^ (k * 0x9e3779b9u);
        float f;
        switch ((k + (val_a & 7u)) % 6u) {{
            case 0: f = (static_cast<float>(static_cast<int>(val_a) % 100) + 0.375f) * static_cast<float>(k + 1u); memcpy(&seed_xmm[k], &f, 4); break;
            case 1: seed_xmm[k] = edge_val((val_a + k) & 7u, 32); break;
            case 2: seed_xmm[k] = edge_val((val_b + k) & 7u, 32) ^ (k & 1u ? 0x00400000u : 0u); break;
            case 3: f = static_cast<float>(static_cast<int>(b) % 1000) / 3.0f; memcpy(&seed_xmm[k], &f, 4); break;
            case 4: seed_xmm[k] = (k & 1u) ? 0x7f7fffffu : 0x00800001u; break;
            default: seed_xmm[k] = a; break;
        }}
    }}
    for (U k = 0; k < 8u; ++k) seed_mm[k] = static_cast<U64>(seed_xmm[2u * k]) | (static_cast<U64>(seed_xmm[2u * k + 1u]) << 32);
    seed_mxcsr = 0x1f80u | ((flag_seed & 3u) << 13u) | ((flag_seed & 4u) ? 0x8040u : 0u);
    seed_mmx = str_eq(kind, "simd_mmx") ? 1u : 0u;
    if (kind[0] == 's' && kind[1] == 'i') {{
        seed_regs[0] = mem_addr;
        if (str_eq(kind, "simd_ldmxcsr")) {{
            write257(mem_addr, 4u, 0x1f80u | ((val_a & 3u) << 13u) | (val_b & 0x3fu) | ((val_a & 4u) ? 0x8040u : 0u));
        }}
    }}

    for (U i = 0; i < 256; ++i) before_stack[i] = stack_arena[i];

    seed_flags = 0x202u | (flag_seed & 1u) | ((flag_seed & 2u) << 5u) | ((flag_seed & 4u) << 5u) | ((flag_seed & 8u) << 8u);

    target_addr = reinterpret_cast<U>(targets[id]);
    guest_sp = sp;
    native_edge();

    for (U i = 0; i < 256; ++i) native_stack[i] = stack_arena[i];
    if (str_eq(kind, "leave")) {{
        U bp = sp - 16u;
        memcpy(native_stack + (bp + 4u - reinterpret_cast<U>(stack_arena)), &halt_pc, 4);
    }} else {{
        memcpy(native_stack + (sp - reinterpret_cast<U>(stack_arena)), &halt_pc, 4);
    }}
    for (U i = 0; i < 256; ++i) stack_arena[i] = before_stack[i];
    if (str_eq(kind, "leave")) {{
        U bp = sp - 16u;
        write257(bp + 4u, 4u, halt_pc);
    }} else {{
        write257(sp, 4u, halt_pc);
    }}

    // Run simulation
    Machine257 state = {{}};
    for (U i = 0; i < 8; ++i) state.r[i] = seed_regs[i];
    state.flags = seed_flags;
    state.pc = entry;
    state.stop = Stop257::Running;
    state.budget = 128u;

    state.fpu_top = 6u;
    state.st[7] = seed_st1;
    state.st[6] = seed_st0;
    state.fpu_cw = 0x037fu;
    for (U k = 0; k < 32u; ++k) state.xmm[k / 4u][k % 4u] = seed_xmm[k];
    state.mxcsr = seed_mxcsr;
    if (seed_mmx) for (U k = 0; k < 8u; ++k) state.mm[k] = seed_mm[k];

    dispatch257(state, entry);

    // Validate registers
    if (!str_eq(kind, "fpu_status_ax")) {{
        for (U i = 0; i < 8; ++i) {{
            require_msg(state.r[i] == seen_regs[i]);
        }}
    }} else {{
        require_msg((state.r[0] & 0xffffu) == (seen_regs[0] & 0xffffu));
    }}

    // Validate memory
    require_msg(memcmp(native_stack, stack_arena, 256) == 0);

    // Validate flags
    U flag_mask = 0x8c1u;
    if (str_eq(kind, "cdq") || str_eq(kind, "setcc") || str_eq(kind, "leave") || str_eq(kind, "rep_stosd") || str_eq(kind, "rep_movsd") || (kind[0] == 'f' && kind[1] == 'p' && kind[2] == 'u') || (kind[0] == 's' && kind[1] == 'i')) {{
        require_msg(((state.flags ^ seed_flags) & flag_mask) == 0);
    }} else if (str_eq(kind, "unary")) {{
        require_msg(((state.flags ^ seen_flags) & 0x8c0u) == 0);
        require_msg((state.flags & 1u) == (seed_flags & 1u));
    }} else if (str_eq(kind, "shift") || str_eq(kind, "shift_cl")) {{
        if ((val_b & 0x1fu) == 0 && str_eq(kind, "shift_cl")) {{
            require_msg(((state.flags ^ seed_flags) & flag_mask) == 0);
        }} else {{
            require_msg(((state.flags ^ seen_flags) & 0x0c1u) == 0);
            if (str_eq(kind, "shift") || ((val_b & 0x1fu) == 1)) {{
                require_msg(((state.flags ^ seen_flags) & 0x800u) == 0);
            }}
        }}
    }} else if (str_eq(kind, "imul_2op") || str_eq(kind, "imul_3op") || str_eq(kind, "imul_1op") || str_eq(kind, "mul_1op")) {{
        require_msg(((state.flags ^ seen_flags) & 0x801u) == 0);
    }} else if (str_eq(kind, "repne_scasb")) {{
        if ((val_b & 0x0fu) > 0) {{
            require_msg(((state.flags ^ seen_flags) & 0x40u) == 0);
        }}
    }}

    // Validate the x87 result: stack top, live ST0/ST1 bit patterns, and C0/C2/C3 for compares.
    if (kind[0] == 'f' && kind[1] == 'p' && kind[2] == 'u' && !str_eq(kind, "fpu_status_ax")) {{
        U native_top = (static_cast<U>(seen_fpu_status) >> 11u) & 7u;
        require_msg(native_top == (state.fpu_top & 7u));
        U depth = (8u - native_top) & 7u;
        if (depth >= 1u) require_msg(memcmp(&state.st[state.fpu_top & 7u], &seen_st0, 8) == 0);
        if (depth >= 2u) require_msg(memcmp(&state.st[(state.fpu_top + 1u) & 7u], &seen_st1, 8) == 0);
        if (str_eq(kind, "fpu_comp_mem32") || str_eq(kind, "fpu_compp")) {{
            require_msg(((static_cast<U>(seen_fpu_status) ^ state.fpu_status) & 0x4500u) == 0);
        }}
    }}

    // SSE state is compared for every case: integer and x87 code must not touch it.
    for (U k = 0; k < 32u; ++k) require_msg(state.xmm[k / 4u][k % 4u] == seen_xmm[k]);
    require_msg(state.mxcsr == seen_mxcsr);
    if (seed_mmx) {{
        for (U k = 0; k < 8u; ++k) require_msg(state.mm[k] == seen_mm[k]);
        require_msg(((static_cast<U>(seen_fpu_status) >> 11u) & 7u) == (state.fpu_top & 7u));
    }}

    require_msg(state.r[4] == expected_sp && state.pc == halt_pc && state.stop == Stop257::Returned);
    ++total_cases;
}}

extern "C" void __cdecl entry() {{
    for (U id = 0; id < {len(FRAGMENTS)}; ++id) {{
        if ({' || '.join(f'id == {i}u' for i, fragment in enumerate(FRAGMENTS) if fragment[0] in expected_unsupported) or 'false'}) continue;
        const char* kind = "unary";
        U width = 32;
        if (id >= 61u) {{
            kind = simd_kinds[id - 61u]; width = 32;
        }} else if (id <= 5) {{
            kind = "unary";
            width = (id % 3 == 0) ? 8 : ((id % 3 == 1) ? 16 : 32);
        }} else if (id <= 15) {{
            kind = (id == 7 || id == 11 || id == 14) ? "shift_cl" : "shift";
            width = (id == 8 || id == 12 || id == 15) ? 8 : ((id == 9) ? 16 : 32);
        }} else if (id == 16) {{
            kind = "cdq"; width = 32;
        }} else if (id <= 26) {{
            kind = "setcc"; width = 8;
        }} else if (id == 27) {{
            kind = "imul_2op"; width = 32;
        }} else if (id == 28 || id == 29) {{
            kind = "imul_3op"; width = 32;
        }} else if (id == 30) {{
            kind = "imul_1op"; width = 32;
        }} else if (id == 31) {{
            kind = "mul_1op"; width = 32;
        }} else if (id == 32) {{
            kind = "idiv_1op"; width = 32;
        }} else if (id == 33) {{
            kind = "leave"; width = 32;
        }} else if (id == 34) {{
            kind = "repne_scasb"; width = 8;
        }} else if (id == 35) {{
            kind = "rep_stosd"; width = 32;
        }} else if (id == 36) {{
            kind = "rep_movsd"; width = 32;
        }} else {{
            if (id == 37) kind = "fpu_load_mem32";
            else if (id == 38) kind = "fpu_load_mem64";
            else if (id == 39) kind = "fpu_load_st1";
            else if (id == 40) kind = "fpu_iload_mem32";
            else if (id == 41) kind = "fpu_store_mem32";
            else if (id == 42) kind = "fpu_store_mem64";
            else if (id == 43) kind = "fpu_istore_mem32";
            else if (id == 44 || id == 47 || id == 48 || id == 50 || id == 52 || id == 53) kind = "fpu_op_mem32";
            else if (id == 45) kind = "fpu_op_st1";
            else if (id == 46 || id == 49 || id == 51 || id == 54) kind = "fpu_opp_st1";
            else if (id == 55 || id == 56) kind = "fpu_unary";
            else if (id == 57) kind = "fpu_xch_st1";
            else if (id == 58) kind = "fpu_comp_mem32";
            else if (id == 59) kind = "fpu_compp";
            else if (id == 60) kind = "fpu_status_ax";
            width = 32;
        }}

        for (U a = 0; a < 8; ++a) {{
            U val_a = edge_val(a, width);
            for (U b = 0; b < 8; ++b) {{
                U val_b = edge_val(b, 32);
                if (kind[0] == 's' && kind[1] == 'h') {{
                    val_b = (b * 5);
                    if (b == 1) val_b = 1;
                }}
                for (U flags = 0; flags < 16; ++flags) {{
                    run_test(id, kind, width, val_a, val_b, flags);
                }}
            }}
        }}
    }}

    print_str("CASES: ");
    print_num(total_cases);
    print_str(", FAILURES: ");
    print_num(failures);
    print_str("\\n");
    ExitProcess(failures ? 1 : 0);
}}
'''

    (WORK_DIR / 'machine257.h').write_text(backend.HEADER, encoding='utf-8')
    (WORK_DIR / 'primitives.cpp').write_text('\n'.join(translated_sources) + '\n' + dispatcher_cpp, encoding='utf-8')
    (WORK_DIR / 'state-fixture.cpp').write_text(fixture_cpp, encoding='utf-8')

    toolchain = find_toolchain()

    cmd_compile = [
        str(toolchain['cl']), '/nologo', '/c', '/std:c++17', '/Od', '/Oi', '/Gy', '/TP', '/GS-', '/GR-', '/W3', '/utf-8',
        '/Fo' + str(objects_dir) + os.sep,
        str(WORK_DIR / 'primitives.cpp'),
        str(WORK_DIR / 'state-fixture.cpp')
    ]
    p_comp = subprocess.run(cmd_compile, cwd=WORK_DIR, capture_output=True, text=True)
    if p_comp.returncode != 0:
        raise RuntimeError(f"MSVC Compilation failed:\n{p_comp.stdout}\n{p_comp.stderr}")

    exe = WORK_DIR / 'state-fixture.exe'
    cmd_link = [
        str(toolchain['link']), '/nologo', '/MACHINE:X86', '/SUBSYSTEM:CONSOLE', '/ENTRY:entry', '/NODEFAULTLIB',
        f'/OUT:{exe}',
        str(objects_dir / 'primitives.obj'),
        str(objects_dir / 'state-fixture.obj'),
        str(toolchain['msvc_lib'] / 'libcmt.lib'),
        str(toolchain['msvc_lib'] / 'libvcruntime.lib'),
        str(toolchain['sdk_ucrt'] / 'libucrt.lib'),
        str(toolchain['sdk_um'] / 'kernel32.lib')
    ]
    p_link = subprocess.run(cmd_link, cwd=WORK_DIR, capture_output=True, text=True)
    if p_link.returncode != 0:
        raise RuntimeError(f"MSVC Linking failed:\n{p_link.stdout}\n{p_link.stderr}")

    t0 = time.perf_counter()
    p_run = subprocess.run([str(exe)], cwd=WORK_DIR, capture_output=True, text=True)
    dur = time.perf_counter() - t0

    if p_run.returncode != 0:
        raise RuntimeError(f"Fixture failed with code {p_run.returncode}: {p_run.stdout}\n{p_run.stderr}")

    output_line = p_run.stdout.replace('\x00', '').strip()
    # Output expected: CASES: 62464, FAILURES: 0
    parts = dict(p.strip().split(': ') for p in output_line.split(','))
    total_cases = int(parts['CASES'])
    failures = int(parts['FAILURES'])

    report = {
        'candidate_fragments': len(FRAGMENTS),
        'expected_unsupported': list(expected_unsupported),
        'total_fragments': len(FRAGMENTS) - len(expected_unsupported),
        'total_cases': total_cases,
        'failures': failures,
        'duration_seconds': round(dur, 3),
        'hardware_match': (failures == 0 and total_cases == (len(FRAGMENTS) - len(expected_unsupported)) * 8 * 8 * 16),
        'exit_code': p_run.returncode
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Total fragments tested: {report['total_fragments']}")
        print(f"Total input permutations: {report['total_cases']}")
        print(f"Physical CPU mismatches: {report['failures']}")
        print(f"Execution time: {report['duration_seconds']}s")
        if report['hardware_match']:
            print("\n100% SUCCESS: All synthetic fragments match physical x86 CPU hardware bit-for-bit!")
        else:
            print("\nFAILED: Verification failed.")

    if not report['hardware_match']:
        sys.exit(1)


if __name__ == '__main__':
    main()
