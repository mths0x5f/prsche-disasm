/* 00406490: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_00406790_00406490 {
    U call(U);
};

/* the original 00406790 (thiscall) */
__declspec(naked) U Call_00406790_00406490::call(U)
{
    __asm mov eax, 0x00406790
    __asm jmp eax
}

struct Object_00406490 {
    U function_00406490(U a0);
};

U Object_00406490::function_00406490(U a0)
{
    U self = (U)this;
    U t1 = ((Call_00406790_00406490 *)self)->call(a0);
    *(unsigned long *)self = (unsigned long)0x5b2588u;
    *(unsigned long *)(self + 0x18u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x1cu) = (unsigned long)0u;
    return self;
}
