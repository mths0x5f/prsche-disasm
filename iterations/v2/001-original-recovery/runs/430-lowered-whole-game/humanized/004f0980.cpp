/* 004f0980: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004bc1f0_004f0980 {
    U call(U, U, U, U, U, U, U);
};

/* the original 004bc1f0 (thiscall) */
__declspec(naked) U Call_004bc1f0_004f0980::call(U, U, U, U, U, U, U)
{
    __asm mov eax, 0x004bc1f0
    __asm jmp eax
}

struct Object_004f0980 {
    U function_004f0980(U a0, U a1, U a2);
};

U Object_004f0980::function_004f0980(U a0, U a1, U a2)
{
    U self = (U)this;
    U t1 = ((Call_004bc1f0_004f0980 *)self)->call(a0, a1, 0x0u, a2, 0x0u, 0x0u, 0x0u);
    *(unsigned char *)(self + 0x24u) = (unsigned char)0x0u;
    *(unsigned char *)(self + 0x25u) = (unsigned char)0x0u;
    *(unsigned long *)self = (unsigned long)0x5b74c0u;
    return self;
}
