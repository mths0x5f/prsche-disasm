/* 004e07c0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00527f90_004e07c0 {
    U call(void);
};

/* the original 00527f90 (thiscall) */
__declspec(naked) U Call_00527f90_004e07c0::call(void)
{
    __asm mov eax, 0x00527f90
    __asm jmp eax
}

struct Object_004e07c0 {
    U function_004e07c0(void);
};

U Object_004e07c0::function_004e07c0(void)
{
    U self = (U)this;
    U t1 = ((Call_00527f90_004e07c0 *)self)->call();
    *(unsigned long *)(self + 0x124u) = (unsigned long)0x3u;
    *(unsigned long *)(self + 0x128u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x12cu) = (unsigned long)0u;
    *(unsigned char *)(self + 0x261u) = (unsigned char)(0u & 0xffu);
    *(unsigned char *)(self + 0x1fcu) = (unsigned char)(0u & 0xffu);
    *(unsigned long *)self = (unsigned long)0x5b6b34u;
    *(unsigned long *)(self + 0x130u) = (unsigned long)0x200u;
    return self;
}
