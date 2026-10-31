/* 004b9550: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004bc480_004b9550 {
    U call(U);
};

/* the original 004bc480 (thiscall) */
__declspec(naked) U Call_004bc480_004b9550::call(U)
{
    __asm mov eax, 0x004bc480
    __asm jmp eax
}

struct Object_004b9550 {
    U function_004b9550(U a0);
};

U Object_004b9550::function_004b9550(U a0)
{
    U self = (U)this;
    U t1 = ((Call_004bc480_004b9550 *)self)->call(a0);
    U t2 = *(unsigned long *)a0;
    U t3 = *(unsigned long *)t2;
    *(unsigned long *)(self + 0x2cu) = (unsigned long)t3;
    U t4 = *(unsigned long *)a0;
    U t5 = t4 + 0x4u;
    *(unsigned long *)a0 = (unsigned long)t5;
    return t5;
}
