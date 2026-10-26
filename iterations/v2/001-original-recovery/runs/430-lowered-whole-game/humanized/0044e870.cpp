/* 0044e870: stores the low bytes of its two arguments in the bytes at 0x6197ab and 0x6197ac. */
#define g_006197ab_0044e870 (*(unsigned char *)0x006197ab)
#define g_006197ac_0044e870 (*(unsigned char *)0x006197ac)

void set_0044e870(unsigned char a, unsigned char b)
{
    g_006197ab_0044e870 = a;
    g_006197ac_0044e870 = b;
}
