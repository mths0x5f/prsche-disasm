/* 004ce9e0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004c7480_004ce9e0 {
    U call(void);
};

/* the original 004c7480 (thiscall) */
__declspec(naked) U Call_004c7480_004ce9e0::call(void)
{
    __asm mov eax, 0x004c7480
    __asm jmp eax
}

struct Object_004ce9e0 {
    U function_004ce9e0(void);
};

U Object_004ce9e0::function_004ce9e0(void)
{
    U self = (U)this;
    U t1 = ((Call_004c7480_004ce9e0 *)self)->call();
    *(unsigned long *)(self + 0x14cu) = (unsigned long)0x0u;
    *(unsigned long *)self = (unsigned long)0x5b6358u;
    return self;
}
