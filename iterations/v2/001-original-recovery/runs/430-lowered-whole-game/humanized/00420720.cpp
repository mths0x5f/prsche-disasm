/* 00420720: stores its two arguments in the globals at 0x60c850 and 0x60c854. */
#define g_0060c850_00420720 (*(unsigned long *)0x0060c850)
#define g_0060c854_00420720 (*(unsigned long *)0x0060c854)

void set_00420720(unsigned long a, unsigned long b)
{
    g_0060c850_00420720 = a;
    g_0060c854_00420720 = b;
}
