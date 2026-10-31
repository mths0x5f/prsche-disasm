/* 004b87f0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004f0980_004b87f0 {
    U call(U, U, U);
};

/* the original 004f0980 (thiscall) */
__declspec(naked) U Call_004f0980_004b87f0::call(U, U, U)
{
    __asm mov eax, 0x004f0980
    __asm jmp eax
}

struct Object_004b87f0 {
    U function_004b87f0(U a0);
};

U Object_004b87f0::function_004b87f0(U a0)
{
    U self = (U)this;
    U t1 = ((Call_004f0980_004b87f0 *)self)->call(a0, 0x0u, 0x0u);
    *(unsigned long *)self = (unsigned long)0x5b4ce0u;
    return self;
}
