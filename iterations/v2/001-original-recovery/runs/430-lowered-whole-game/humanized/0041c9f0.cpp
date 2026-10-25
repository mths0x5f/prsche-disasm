/* 0041c9f0: stdcall: calls 004340a0(a, b, b / 2); the third argument is unused. */
#define call_004340a0_from_0041c9f0 ((unsigned long (__stdcall *)(unsigned long, long, long))0x004340a0)

unsigned long __stdcall call_half_0041c9f0(unsigned long a, long b, unsigned long unused)
{
    return call_004340a0_from_0041c9f0(a, b, b / 2);
}
