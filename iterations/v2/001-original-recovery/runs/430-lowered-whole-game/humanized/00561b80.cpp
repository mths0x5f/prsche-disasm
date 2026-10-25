/* 00561b80: calls 00533f00(argument, global 0x5df770). */
#define callee_00533f00_00561b80 ((unsigned long (__cdecl *)(unsigned long, unsigned long))0x00533f00)
#define g_005df770_00561b80 (*(unsigned long *)0x005df770)

unsigned long call_00561b80(unsigned long a)
{
    return callee_00533f00_00561b80(a, g_005df770_00561b80);
}
