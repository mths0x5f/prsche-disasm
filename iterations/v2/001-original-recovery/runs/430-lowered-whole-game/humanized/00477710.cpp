/* 00477710: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00477ba0_00477710 {
    U call(U);
};

/* the original 00477ba0 (thiscall) */
__declspec(naked) U Call_00477ba0_00477710::call(U)
{
    __asm mov eax, 0x00477ba0
    __asm jmp eax
}

struct Object_00477710 {
    U function_00477710(U a0);
};

U Object_00477710::function_00477710(U a0)
{
    U self = (U)this;
    U t1 = ((Call_00477ba0_00477710 *)self)->call(a0);
    U t2 = (t1 & 0xffffff00u) | (0x1u & 0xffu);
    *(unsigned long *)self = (unsigned long)0x5b46b8u;
    *(unsigned char *)(self + 0x4u) = (unsigned char)(t2 & 0xffu);
    *(unsigned char *)(self + 0x5u) = (unsigned char)(t2 & 0xffu);
    return self;
}
