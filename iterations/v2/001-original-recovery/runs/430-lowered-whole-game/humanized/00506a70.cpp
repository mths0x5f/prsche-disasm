/* 00506a70: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004bb6f0_00506a70 {
    U call(U, U, U, U, U, U, U);
};

/* the original 004bb6f0 (thiscall) */
__declspec(naked) U Call_004bb6f0_00506a70::call(U, U, U, U, U, U, U)
{
    __asm mov eax, 0x004bb6f0
    __asm jmp eax
}

struct Object_00506a70 {
    U function_00506a70(U a0, U a1, U a2);
};

U Object_00506a70::function_00506a70(U a0, U a1, U a2)
{
    U self = (U)this;
    U t1 = ((Call_004bb6f0_00506a70 *)self)->call(a0, 0x0u, a1, a2, 0x0u, 0x0u, 0x0u);
    *(unsigned long *)self = (unsigned long)0x5b8960u;
    return self;
}
