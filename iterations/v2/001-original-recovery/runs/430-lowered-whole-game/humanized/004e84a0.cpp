/* 004e84a0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004d6240_004e84a0 {
    U call(U);
};

/* the original 004d6240 (thiscall) */
__declspec(naked) U Call_004d6240_004e84a0::call(U)
{
    __asm mov eax, 0x004d6240
    __asm jmp eax
}

struct Object_004e84a0 {
    U function_004e84a0(void);
};

U Object_004e84a0::function_004e84a0(void)
{
    U self = (U)this;
    U t1 = *(unsigned long *)(self + 0x290u);
    U t2 = *(unsigned long *)0x0065b928u;
    U t3 = ((Call_004d6240_004e84a0 *)t2)->call(t1);
    return t3;
}
