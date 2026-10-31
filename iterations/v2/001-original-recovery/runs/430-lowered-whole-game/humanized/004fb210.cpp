/* 004fb210: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_004bc1f0_004fb210 {
    U call(U, U, U, U, U, U, U);
};

/* the original 004bc1f0 (thiscall) */
__declspec(naked) U Call_004bc1f0_004fb210::call(U, U, U, U, U, U, U)
{
    __asm mov eax, 0x004bc1f0
    __asm jmp eax
}

struct Call_004bc240_004fb210 {
    U call(U);
};

/* the original 004bc240 (thiscall) */
__declspec(naked) U Call_004bc240_004fb210::call(U)
{
    __asm mov eax, 0x004bc240
    __asm jmp eax
}

struct Object_004fb210 {
    U function_004fb210(U a0, U a1);
};

U Object_004fb210::function_004fb210(U a0, U a1)
{
    U self = (U)this;
    U t1 = ((U (__cdecl *)(void))0x004fb190u)();
    U t2 = ((Call_004bc1f0_004fb210 *)self)->call(a0, a1, t1, 0x0u, 0x0u, 0x0u, 0x0u);
    *(unsigned long *)self = (unsigned long)0x5b7f68u;
    U t3 = ((Call_004bc240_004fb210 *)self)->call(0x0u);
    return self;
}
