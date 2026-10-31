/* 004cdb90: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004cd190_004cdb90 {
    U call(void);
};

/* the original 004cd190 (thiscall) */
__declspec(naked) U Call_004cd190_004cdb90::call(void)
{
    __asm mov eax, 0x004cd190
    __asm jmp eax
}

struct Call_004cdc80_004cdb90 {
    U call(void);
};

/* the original 004cdc80 (thiscall) */
__declspec(naked) U Call_004cdc80_004cdb90::call(void)
{
    __asm mov eax, 0x004cdc80
    __asm jmp eax
}

struct Object_004cdb90 {
    U function_004cdb90(void);
};

U Object_004cdb90::function_004cdb90(void)
{
    U self = (U)this;
    U t1 = ((Call_004cd190_004cdb90 *)self)->call();
    U t2 = ((Call_004cdc80_004cdb90 *)self)->call();
    U t3 = ((U (__cdecl *)(void))0x0053c2e0u)();
    *(unsigned long *)(self + 0x240u) = (unsigned long)t3;
    *(unsigned long *)(self + 0x244u) = (unsigned long)0x0u;
    *(unsigned long *)(self + 0x23cu) = (unsigned long)0x1770u;
    return t3;
}
