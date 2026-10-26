/* 00415e70: Sets the global bytes at 0x005cc81c and 0x005cc81d to 1. */
#define flag_005cc81c (*(unsigned char *)0x005cc81c)
#define flag_005cc81d (*(unsigned char *)0x005cc81d)

void __cdecl set_flags_00415e70(void)
{
    flag_005cc81c = 1;
    flag_005cc81d = 1;
}
