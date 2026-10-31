/* 004d0e30: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00525e20_004d0e30 {
    U call(void);
};

/* the original 00525e20 (thiscall) */
__declspec(naked) U Call_00525e20_004d0e30::call(void)
{
    __asm mov eax, 0x00525e20
    __asm jmp eax
}

struct Object_004d0e30 {
    U function_004d0e30(U a0, U a1, U a2);
};

U Object_004d0e30::function_004d0e30(U a0, U a1, U a2)
{
    U self = (U)this;
    U t1 = ((Call_00525e20_004d0e30 *)self)->call();
    *(unsigned long *)(self + 0xd4u) = (unsigned long)a0;
    *(unsigned long *)(self + 0xd8u) = (unsigned long)a2;
    *(unsigned long *)(self + 0xdcu) = (unsigned long)0u;
    *(unsigned long *)(self + 0xe0u) = (unsigned long)0u;
    *(unsigned long *)(self + 0xe4u) = (unsigned long)0u;
    *(unsigned long *)(self + 0xe8u) = (unsigned long)0u;
    *(unsigned long *)(self + 0xecu) = (unsigned long)0u;
    *(unsigned long *)(self + 0xf8u) = (unsigned long)0u;
    *(unsigned long *)(self + 0xfcu) = (unsigned long)0u;
    *(unsigned long *)(self + 0x130u) = (unsigned long)a1;
    *(unsigned long *)self = (unsigned long)0x5b6764u;
    return self;
}
