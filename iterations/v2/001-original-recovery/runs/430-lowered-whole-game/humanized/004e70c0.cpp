/* 004e70c0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_0052ade0_004e70c0 {
    U call(U, U);
};

/* the original 0052ade0 (thiscall) */
__declspec(naked) U Call_0052ade0_004e70c0::call(U, U)
{
    __asm mov eax, 0x0052ade0
    __asm jmp eax
}

struct Object_004e70c0 {
    U function_004e70c0(U a0, U a1, U a2);
};

U Object_004e70c0::function_004e70c0(U a0, U a1, U a2)
{
    U self = (U)this;
    U t1 = ((Call_0052ade0_004e70c0 *)self)->call(a0, a2);
    *(unsigned long *)(self + 0x1c8u) = (unsigned long)0x0u;
    *(unsigned long *)self = (unsigned long)0x5b6e8cu;
    U t2 = ((U (__cdecl *)(U, U, U, U, U))0x005a134bu)(a1, 0x0u, 0x5d75e8u, 0x5d7608u, 0x0u);
    *(unsigned long *)(self + 0x1c4u) = (unsigned long)t2;
    return self;
}
