/* 004baba0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004bb870_004baba0 {
    U call(U, U);
};

/* the original 004bb870 (thiscall) */
__declspec(naked) U Call_004bb870_004baba0::call(U, U)
{
    __asm mov eax, 0x004bb870
    __asm jmp eax
}

struct Object_004baba0 {
    U function_004baba0(U a0, U a1);
};

U Object_004baba0::function_004baba0(U a0, U a1)
{
    U self = (U)this;
    U t1 = ((Call_004bb870_004baba0 *)self)->call(a0, a1);
    *(unsigned long *)self = (unsigned long)0x5b511cu;
    return self;
}
