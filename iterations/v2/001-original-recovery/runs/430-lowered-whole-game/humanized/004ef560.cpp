/* 004ef560: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004f1d40_004ef560 {
    U call(U);
};

/* the original 004f1d40 (thiscall) */
__declspec(naked) U Call_004f1d40_004ef560::call(U)
{
    __asm mov eax, 0x004f1d40
    __asm jmp eax
}

struct Object_004ef560 {
    U function_004ef560(U a0);
};

U Object_004ef560::function_004ef560(U a0)
{
    U self = (U)this;
    U t1 = self + 0x4u;
    U t2 = a0 + 0x4u;
    U t3 = ((Call_004f1d40_004ef560 *)t1)->call(t2);
    return t3;
}
