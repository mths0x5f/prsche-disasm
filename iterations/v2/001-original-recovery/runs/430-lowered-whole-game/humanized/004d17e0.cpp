/* 004d17e0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00443db0_004d17e0 {
    U call(U);
};

/* the original 00443db0 (thiscall) */
__declspec(naked) U Call_00443db0_004d17e0::call(U)
{
    __asm mov eax, 0x00443db0
    __asm jmp eax
}

struct Call_00442d50_004d17e0 {
    U call(void);
};

/* the original 00442d50 (thiscall) */
__declspec(naked) U Call_00442d50_004d17e0::call(void)
{
    __asm mov eax, 0x00442d50
    __asm jmp eax
}

struct Object_004d17e0 {
    U function_004d17e0(U a0);
};

U Object_004d17e0::function_004d17e0(U a0)
{
    U self = (U)this;
    U t1 = *(unsigned long *)(self + 0x10u);
    U t2 = ((Call_00443db0_004d17e0 *)t1)->call(a0);
    U t3 = *(unsigned long *)(self + 0x10u);
    U t4 = ((Call_00442d50_004d17e0 *)t3)->call();
    return t4;
}
