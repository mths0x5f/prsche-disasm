/* 005673b0: counts the non-zero dwords of the 16-entry table at 006b7740. */
int __cdecl count_used_005673b0(void)
{
    int count = 0;
    unsigned long *p;
    for (p = (unsigned long *)0x006b7740; p < (unsigned long *)0x006b7780; ++p)
        if (*p != 0)
            ++count;
    return count;
}
