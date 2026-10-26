/* 004207a0: stores its two arguments in the globals at 0x60c878 and 0x60c87c. */
#define g_0060c878_004207a0 (*(unsigned long *)0x0060c878)
#define g_0060c87c_004207a0 (*(unsigned long *)0x0060c87c)

void set_004207a0(unsigned long a, unsigned long b)
{
    g_0060c878_004207a0 = a;
    g_0060c87c_004207a0 = b;
}
