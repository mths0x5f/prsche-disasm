/* 0051cbc0: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004b7b30_0051cbc0 {
    U call(U, U, U, U);
};

/* the original 004b7b30 (thiscall) */
__declspec(naked) U Call_004b7b30_0051cbc0::call(U, U, U, U)
{
    __asm mov eax, 0x004b7b30
    __asm jmp eax
}

struct Object_0051cbc0 {
    U function_0051cbc0(U a0, U a1);
};

U Object_0051cbc0::function_0051cbc0(U a0, U a1)
{
    U self = (U)this;
    U t1 = ((Call_004b7b30_0051cbc0 *)self)->call(a0, a1, 0u, 0u);
    *(unsigned long *)(self + 0x14u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x18u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x1cu) = (unsigned long)0u;
    *(unsigned long *)(self + 0x20u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x24u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x28u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x14u) = (unsigned long)0u;
    *(unsigned long *)self = (unsigned long)0x5bacf4u;
    return self;
}
