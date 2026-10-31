/* 004056b0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00405c30_004056b0 {
    U call(U);
};

/* the original 00405c30 (thiscall) */
__declspec(naked) U Call_00405c30_004056b0::call(U)
{
    __asm mov eax, 0x00405c30
    __asm jmp eax
}

struct Object_004056b0 {
    U function_004056b0(U a0);
};

U Object_004056b0::function_004056b0(U a0)
{
    U self = (U)this;
    U t1 = ((Call_00405c30_004056b0 *)self)->call(a0);
    *(unsigned long *)self = (unsigned long)0x5b2544u;
    return self;
}
