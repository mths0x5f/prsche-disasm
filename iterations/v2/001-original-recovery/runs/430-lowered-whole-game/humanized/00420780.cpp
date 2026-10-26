/* 00420780: stores its two arguments in the globals at 0x60c870 and 0x60c874. */
#define g_0060c870_00420780 (*(unsigned long *)0x0060c870)
#define g_0060c874_00420780 (*(unsigned long *)0x0060c874)

void set_00420780(unsigned long a, unsigned long b)
{
    g_0060c870_00420780 = a;
    g_0060c874_00420780 = b;
}
