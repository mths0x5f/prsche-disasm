/* 004206e0: stores its two arguments in the globals at 0x60c840 and 0x60c844. */
#define g_0060c840_004206e0 (*(unsigned long *)0x0060c840)
#define g_0060c844_004206e0 (*(unsigned long *)0x0060c844)

void set_004206e0(unsigned long a, unsigned long b)
{
    g_0060c840_004206e0 = a;
    g_0060c844_004206e0 = b;
}
