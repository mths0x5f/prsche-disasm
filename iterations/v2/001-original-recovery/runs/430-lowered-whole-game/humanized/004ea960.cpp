/* 004ea960: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004e84a0_004ea960 {
    U call(void);
};

/* the original 004e84a0 (thiscall) */
__declspec(naked) U Call_004e84a0_004ea960::call(void)
{
    __asm mov eax, 0x004e84a0
    __asm jmp eax
}

struct Call_004d1700_004ea960 {
    U call(U, U, U);
};

/* the original 004d1700 (thiscall) */
__declspec(naked) U Call_004d1700_004ea960::call(U, U, U)
{
    __asm mov eax, 0x004d1700
    __asm jmp eax
}

struct Object_004ea960 {
    U function_004ea960(void);
};

U Object_004ea960::function_004ea960(void)
{
    U self = (U)this;
    U t1 = ((Call_004e84a0_004ea960 *)self)->call();
    U t2 = *(unsigned long *)(self + 0x280u);
    U t3 = *(unsigned long *)(self + 0x27cu);
    U t4 = *(unsigned long *)(self + 0x278u);
    U t5 = *(unsigned long *)(self + 0x314u);
    U t6 = ((Call_004d1700_004ea960 *)t5)->call(t4, t3, t2);
    U t7 = *(unsigned long *)(self + 0x280u);
    U t8 = *(unsigned long *)(self + 0x27cu);
    U t9 = *(unsigned long *)(self + 0x278u);
    U t10 = *(unsigned long *)(self + 0x318u);
    U t11 = ((Call_004d1700_004ea960 *)t10)->call(t9, t8, t7);
    return t11;
}
