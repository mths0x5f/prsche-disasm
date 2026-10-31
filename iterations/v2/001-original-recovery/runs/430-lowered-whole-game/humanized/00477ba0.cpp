/* 00477ba0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00489160_00477ba0 {
    U call(U, U);
};

/* the original 00489160 (thiscall) */
__declspec(naked) U Call_00489160_00477ba0::call(U, U)
{
    __asm mov eax, 0x00489160
    __asm jmp eax
}

struct Object_00477ba0 {
    U function_00477ba0(U a0);
};

U Object_00477ba0::function_00477ba0(U a0)
{
    U self = (U)this;
    U t1 = ((Call_00489160_00477ba0 *)self)->call(0x41727469u, a0);
    *(unsigned long *)(self + 0x30u) = (unsigned long)0x0u;
    *(unsigned long *)self = (unsigned long)0x5b46e8u;
    return self;
}
