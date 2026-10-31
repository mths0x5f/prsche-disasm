/* 00483640: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00477ba0_00483640 {
    U call(U);
};

/* the original 00477ba0 (thiscall) */
__declspec(naked) U Call_00477ba0_00483640::call(U)
{
    __asm mov eax, 0x00477ba0
    __asm jmp eax
}

struct Object_00483640 {
    U function_00483640(U a0);
};

U Object_00483640::function_00483640(U a0)
{
    U self = (U)this;
    U t1 = ((Call_00477ba0_00483640 *)self)->call(a0);
    *(unsigned long *)self = (unsigned long)0x5b4814u;
    return self;
}
