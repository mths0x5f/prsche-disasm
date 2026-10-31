/* 004dbac0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004dbba0_004dbac0 {
    U call(U, U);
};

/* the original 004dbba0 (thiscall) */
__declspec(naked) U Call_004dbba0_004dbac0::call(U, U)
{
    __asm mov eax, 0x004dbba0
    __asm jmp eax
}

struct Object_004dbac0 {
    U function_004dbac0(void);
};

U Object_004dbac0::function_004dbac0(void)
{
    U self = (U)this;
    *(unsigned long *)(self + 0x4u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x8u) = (unsigned long)0u;
    *(unsigned char *)(self + 0xcu) = (unsigned char)(0u & 0xffu);
    *(unsigned long *)self = (unsigned long)0x5b6a98u;
    U t1 = ((Call_004dbba0_004dbac0 *)self)->call(0x5d9010u, 0xffffffffu);
    return self;
}
