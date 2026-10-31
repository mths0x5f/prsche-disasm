/* 00405910: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00405c30_00405910 {
    U call(U);
};

/* the original 00405c30 (thiscall) */
__declspec(naked) U Call_00405c30_00405910::call(U)
{
    __asm mov eax, 0x00405c30
    __asm jmp eax
}

struct Object_00405910 {
    U function_00405910(U a0);
};

U Object_00405910::function_00405910(U a0)
{
    U self = (U)this;
    U t1 = ((Call_00405c30_00405910 *)self)->call(a0);
    *(unsigned long *)self = (unsigned long)0x5b2560u;
    *(unsigned long *)(self + 0xb0u) = (unsigned long)0u;
    *(unsigned long *)(self + 0xb4u) = (unsigned long)0u;
    *(unsigned long *)(self + 0xb8u) = (unsigned long)0u;
    *(unsigned long *)(self + 0xbcu) = (unsigned long)0u;
    *(unsigned long *)(self + 0x10u) = (unsigned long)0x1u;
    return self;
}
