/* 004fa9e0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004c7b00_004fa9e0 {
    U call(void);
};

/* the original 004c7b00 (thiscall) */
__declspec(naked) U Call_004c7b00_004fa9e0::call(void)
{
    __asm mov eax, 0x004c7b00
    __asm jmp eax
}

struct Object_004fa9e0 {
    U function_004fa9e0(void);
};

U Object_004fa9e0::function_004fa9e0(void)
{
    U self = (U)this;
    U t1 = ((Call_004c7b00_004fa9e0 *)self)->call();
    U t2 = (self + 0x140u);
    U t3 = ((U (__cdecl *)(U, U))0x005a0fbfu)(t2, 0x5e8e50u);
    *(unsigned long *)(self + 0x178u) = (unsigned long)0x0u;
    return t3;
}
