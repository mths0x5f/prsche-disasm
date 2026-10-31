/* 0048bb30: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_0048c870_0048bb30 {
    U call(U, U, U, U, U);
};

/* the original 0048c870 (thiscall) */
__declspec(naked) U Call_0048c870_0048bb30::call(U, U, U, U, U)
{
    __asm mov eax, 0x0048c870
    __asm jmp eax
}

struct Object_0048bb30 {
    U function_0048bb30(U a0);
};

U Object_0048bb30::function_0048bb30(U a0)
{
    U self = (U)this;
    U t1 = *(unsigned long *)(self + 0x70u);
    U t2 = self + 0x64u;
    U t3 = ((Call_0048c870_0048bb30 *)t2)->call(0xb5u, t1, 0x0u, 0x0u, a0);
    return t3;
}
