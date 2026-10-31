/* 004b8580: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004bc1f0_004b8580 {
    U call(U, U, U, U, U, U, U);
};

/* the original 004bc1f0 (thiscall) */
__declspec(naked) U Call_004bc1f0_004b8580::call(U, U, U, U, U, U, U)
{
    __asm mov eax, 0x004bc1f0
    __asm jmp eax
}

struct Object_004b8580 {
    U function_004b8580(U a0, U a1);
};

U Object_004b8580::function_004b8580(U a0, U a1)
{
    U self = (U)this;
    U t1 = ((Call_004bc1f0_004b8580 *)self)->call(a0, 0x0u, 0x0u, 0x0u, 0x0u, 0x0u, 0x0u);
    *(unsigned long *)self = (unsigned long)0x5b4be4u;
    *(unsigned long *)(self + 0x24u) = (unsigned long)a1;
    return self;
}
