/* 004f0a30: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004bc240_004f0a30 {
    U call(U);
};

/* the original 004bc240 (thiscall) */
__declspec(naked) U Call_004bc240_004f0a30::call(U)
{
    __asm mov eax, 0x004bc240
    __asm jmp eax
}

struct Object_004f0a30 {
    U function_004f0a30(U a0);
};

U Object_004f0a30::function_004f0a30(U a0)
{
    U self = (U)this;
    U t1 = ((Call_004bc240_004f0a30 *)self)->call(a0);
    *(unsigned char *)(self + 0x24u) = (unsigned char)0x0u;
    return t1;
}
