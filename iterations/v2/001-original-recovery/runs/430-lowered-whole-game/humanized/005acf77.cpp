/* 005acf77: calls 005acf88 with (argument, 0, 4). */
#define callee_005acf88_005acf77 ((unsigned long (__cdecl *)(unsigned long, unsigned long, unsigned long))0x005acf88)

unsigned long call_005acf77(unsigned long a)
{
    return callee_005acf88_005acf77(a, 0, 4);
}
