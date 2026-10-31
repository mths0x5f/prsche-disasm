/* 004f1a30: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004f14b0_004f1a30 {
    U call(void);
};

/* the original 004f14b0 (thiscall) */
__declspec(naked) U Call_004f14b0_004f1a30::call(void)
{
    __asm mov eax, 0x004f14b0
    __asm jmp eax
}

struct Call_004ef4e0_004f1a30 {
    U call(void);
};

/* the original 004ef4e0 (thiscall) */
__declspec(naked) U Call_004ef4e0_004f1a30::call(void)
{
    __asm mov eax, 0x004ef4e0
    __asm jmp eax
}

struct Object_004f1a30 {
    U function_004f1a30(void);
};

U Object_004f1a30::function_004f1a30(void)
{
    U self = (U)this;
    U t1 = ((Call_004f14b0_004f1a30 *)self)->call();
    U t2 = *(unsigned long *)(self + 0x284u);
    U t3 = ((Call_004ef4e0_004f1a30 *)t2)->call();
    return t3;
}
