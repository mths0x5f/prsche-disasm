/* 005a8bcb: ctype check of c (bit 2); when it fails, folds the case and subtracts 7 (letter digit adjustment). */
#define ctype_mode_005e54dc (*(long *)0x005e54dc)
#define ctype_table_005e52d0 (*(unsigned char **)0x005e52d0)
#define isctype_005a2eae ((long (__cdecl *)(long, long))0x005a2eae)

long __cdecl digit_adjust_005a8bcb(long c)
{
    long check;

    if (ctype_mode_005e54dc > 1)
        check = isctype_005a2eae(c, 4);
    else
        check = ctype_table_005e52d0[c * 2] & 4;
    if (check == 0)
        c = (c & 0xffffffdf) - 7;
    return c;
}
