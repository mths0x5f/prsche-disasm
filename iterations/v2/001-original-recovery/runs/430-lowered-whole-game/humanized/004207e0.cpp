/* 004207e0: stores its two arguments in the globals at 0x60c868 and 0x60c86c. */
#define g_0060c868_004207e0 (*(unsigned long *)0x0060c868)
#define g_0060c86c_004207e0 (*(unsigned long *)0x0060c86c)

void set_004207e0(unsigned long a, unsigned long b)
{
    g_0060c868_004207e0 = a;
    g_0060c86c_004207e0 = b;
}
