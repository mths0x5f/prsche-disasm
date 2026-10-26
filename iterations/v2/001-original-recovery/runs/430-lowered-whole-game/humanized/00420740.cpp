/* 00420740: stores its two arguments in the globals at 0x60c848 and 0x60c84c. */
#define g_0060c848_00420740 (*(unsigned long *)0x0060c848)
#define g_0060c84c_00420740 (*(unsigned long *)0x0060c84c)

void set_00420740(unsigned long a, unsigned long b)
{
    g_0060c848_00420740 = a;
    g_0060c84c_00420740 = b;
}
