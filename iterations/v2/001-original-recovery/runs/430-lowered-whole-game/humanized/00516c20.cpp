/* 00516c20: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004bc1f0_00516c20 {
    U call(U, U, U, U, U, U, U);
};

/* the original 004bc1f0 (thiscall) */
__declspec(naked) U Call_004bc1f0_00516c20::call(U, U, U, U, U, U, U)
{
    __asm mov eax, 0x004bc1f0
    __asm jmp eax
}

struct Call_004bc610_00516c20 {
    U call(void);
};

/* the original 004bc610 (thiscall) */
__declspec(naked) U Call_004bc610_00516c20::call(void)
{
    __asm mov eax, 0x004bc610
    __asm jmp eax
}

struct Object_00516c20 {
    U function_00516c20(U a0, U a1, U a2);
};

U Object_00516c20::function_00516c20(U a0, U a1, U a2)
{
    U self = (U)this;
    U t1 = ((Call_004bc1f0_00516c20 *)self)->call(a0, 0x0u, 0x0u, 0x0u, 0x1u, 0x0u, 0x0u);
    *(unsigned long *)self = (unsigned long)0x5ba3c4u;
    *(unsigned long *)(self + 0x28u) = (unsigned long)a2;
    U t2 = ((Call_004bc610_00516c20 *)self)->call();
    *(unsigned long *)(self + 0x24u) = (unsigned long)a1;
    return self;
}
