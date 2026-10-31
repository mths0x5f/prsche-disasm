/* 005896d0: generated from the original by humanize-generate-430.py (straight-line code). */
U __cdecl function_005896d0(void)
{
    U t1 = ((U (__cdecl *)(void))0x0058e2f0u)();
    U t2 = *(unsigned char *)0x006b499fu;
    U t3 = (t1 & 0xffffff00u) | (t2 & 0xffu);
    U t4 = (t3 & 0xffffff00u) | (((t3 & 0xffu) + 1u) & 0xffu & 0xffu);
    *(unsigned char *)0x006b499fu = (unsigned char)(t4 & 0xffu);
    return t4;
}
