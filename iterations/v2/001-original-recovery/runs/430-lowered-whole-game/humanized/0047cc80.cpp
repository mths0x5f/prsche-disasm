/* 0047cc80: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00477ba0_0047cc80 {
    U call(U);
};

/* the original 00477ba0 (thiscall) */
__declspec(naked) U Call_00477ba0_0047cc80::call(U)
{
    __asm mov eax, 0x00477ba0
    __asm jmp eax
}

struct Object_0047cc80 {
    U function_0047cc80(U a0);
};

U Object_0047cc80::function_0047cc80(U a0)
{
    U self = (U)this;
    U t1 = ((Call_00477ba0_0047cc80 *)self)->call(a0);
    U t2 = (t1 & 0xffffff00u) | (0u & 0xffu);
    *(unsigned long *)self = (unsigned long)0x5b477cu;
    *(unsigned char *)(self + 0x4u) = (unsigned char)(t2 & 0xffu);
    *(unsigned char *)(self + 0x5u) = (unsigned char)(t2 & 0xffu);
    return self;
}
