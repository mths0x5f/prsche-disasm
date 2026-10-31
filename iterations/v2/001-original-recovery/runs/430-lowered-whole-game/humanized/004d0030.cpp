/* 004d0030: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004c7480_004d0030 {
    U call(void);
};

/* the original 004c7480 (thiscall) */
__declspec(naked) U Call_004c7480_004d0030::call(void)
{
    __asm mov eax, 0x004c7480
    __asm jmp eax
}

struct Object_004d0030 {
    U function_004d0030(void);
};

U Object_004d0030::function_004d0030(void)
{
    U self = (U)this;
    U t1 = ((Call_004c7480_004d0030 *)self)->call();
    *(unsigned long *)self = (unsigned long)0x5b667cu;
    *(unsigned long *)(self + 0x140u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x150u) = (unsigned long)0u;
    return self;
}
