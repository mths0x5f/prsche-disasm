/* 00502500: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004f0980_00502500 {
    U call(U, U, U);
};

/* the original 004f0980 (thiscall) */
__declspec(naked) U Call_004f0980_00502500::call(U, U, U)
{
    __asm mov eax, 0x004f0980
    __asm jmp eax
}

struct Object_00502500 {
    U function_00502500(U a0, U a1, U a2);
};

U Object_00502500::function_00502500(U a0, U a1, U a2)
{
    U self = (U)this;
    U t1 = ((Call_004f0980_00502500 *)self)->call(a0, a1, a2);
    *(unsigned long *)self = (unsigned long)0x5b85dcu;
    return self;
}
