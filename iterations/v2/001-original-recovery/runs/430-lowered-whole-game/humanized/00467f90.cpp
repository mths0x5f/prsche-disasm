/* 00467f90: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00537890_00467f90 {
    U call(U);
};

/* the original 00537890 (thiscall) */
__declspec(naked) U Call_00537890_00467f90::call(U)
{
    __asm mov eax, 0x00537890
    __asm jmp eax
}

struct Object_00467f90 {
    U function_00467f90(void);
};

U Object_00467f90::function_00467f90(void)
{
    U self = (U)this;
    U t1 = *(unsigned long *)(self + 0x70u);
    U t2 = *(unsigned long *)(t1 + 0x4u);
    U t3 = *(unsigned long *)(t2 + 0x10u);
    U t4 = 0x3u - t3;
    U t5 = *(unsigned long *)0x00628130u;
    U t6 = *(unsigned long *)(t5 + 0x70u);
    U t7 = *(unsigned long *)(t6 + 0x4u);
    U t8 = ((Call_00537890_00467f90 *)t7)->call(t4);
    return t8;
}
