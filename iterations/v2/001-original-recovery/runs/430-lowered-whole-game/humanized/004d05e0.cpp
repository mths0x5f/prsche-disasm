/* 004d05e0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004c7480_004d05e0 {
    U call(void);
};

/* the original 004c7480 (thiscall) */
__declspec(naked) U Call_004c7480_004d05e0::call(void)
{
    __asm mov eax, 0x004c7480
    __asm jmp eax
}

struct Object_004d05e0 {
    U function_004d05e0(U a0);
};

U Object_004d05e0::function_004d05e0(U a0)
{
    U self = (U)this;
    U t1 = ((Call_004c7480_004d05e0 *)self)->call();
    *(unsigned long *)(self + 0x144u) = (unsigned long)0x0u;
    *(unsigned long *)(self + 0x140u) = (unsigned long)a0;
    *(unsigned long *)self = (unsigned long)0x5b66f4u;
    return self;
}
