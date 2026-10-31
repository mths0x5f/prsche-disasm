/* 004c7480: generated from the original by humanize-generate-430.py (straight-line code). */
struct Call_005246e0_004c7480 {
    U call(void);
};

/* the original 005246e0 (thiscall) */
__declspec(naked) U Call_005246e0_004c7480::call(void)
{
    __asm mov eax, 0x005246e0
    __asm jmp eax
}

struct Object_004c7480 {
    U function_004c7480(void);
};

U Object_004c7480::function_004c7480(void)
{
    U self = (U)this;
    U t1 = ((Call_005246e0_004c7480 *)self)->call();
    *(unsigned long *)(self + 0x10cu) = (unsigned long)0u;
    *(unsigned long *)(self + 0x110u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x114u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x118u) = (unsigned long)0u;
    *(unsigned long *)(self + 0x11cu) = (unsigned long)0u;
    U t2 = ((U (__cdecl *)(U))0x004d87d0u)(0xffu);
    *(unsigned long *)(self + 0x120u) = (unsigned long)t2;
    *(unsigned char *)(self + 0x125u) = (unsigned char)(0u & 0xffu);
    *(unsigned char *)(self + 0x126u) = (unsigned char)(0u & 0xffu);
    *(unsigned long *)self = (unsigned long)0x5b5ca0u;
    return self;
}
