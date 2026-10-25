/* 00554930: stores 2 (argument non-zero) or 4 (zero) in the global at 0x5dedf4 and returns it. */
#define g_005dedf4_00554930 (*(unsigned long *)0x005dedf4)

unsigned long set_00554930(unsigned long a)
{
    unsigned long v = (a != 0) ? 2 : 4;
    g_005dedf4_00554930 = v;
    return v;
}
