/* 004beb80: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004bc1f0_004beb80 {
    U call(U, U, U, U, U, U, U);
};

/* the original 004bc1f0 (thiscall) */
__declspec(naked) U Call_004bc1f0_004beb80::call(U, U, U, U, U, U, U)
{
    __asm mov eax, 0x004bc1f0
    __asm jmp eax
}

struct Call_004bc610_004beb80 {
    U call(void);
};

/* the original 004bc610 (thiscall) */
__declspec(naked) U Call_004bc610_004beb80::call(void)
{
    __asm mov eax, 0x004bc610
    __asm jmp eax
}

struct Object_004beb80 {
    U function_004beb80(U a0);
};

U Object_004beb80::function_004beb80(U a0)
{
    U self = (U)this;
    U t1 = ((Call_004bc1f0_004beb80 *)self)->call(a0, 0x0u, 0x0u, 0x0u, 0x1u, 0x0u, 0x0u);
    *(unsigned long *)self = (unsigned long)0x5b5648u;
    U t2 = ((Call_004bc610_004beb80 *)self)->call();
    return self;
}
