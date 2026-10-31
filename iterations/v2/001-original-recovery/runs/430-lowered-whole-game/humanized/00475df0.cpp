/* 00475df0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00475e80_00475df0 {
    U call(U);
};

/* the original 00475e80 (thiscall) */
__declspec(naked) U Call_00475e80_00475df0::call(U)
{
    __asm mov eax, 0x00475e80
    __asm jmp eax
}

struct Object_00475df0 {
    U function_00475df0(U a0);
};

U Object_00475df0::function_00475df0(U a0)
{
    U self = (U)this;
    U t1 = ((Call_00475e80_00475df0 *)self)->call(a0);
    *(unsigned long *)(self + 0x1cu) = (unsigned long)a0;
    *(unsigned long *)self = (unsigned long)0x5b469cu;
    return self;
}
