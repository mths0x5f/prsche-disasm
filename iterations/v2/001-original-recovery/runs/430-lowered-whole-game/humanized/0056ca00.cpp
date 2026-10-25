/* 0056ca00: calls 00567550(a, b, 0, c, 2). */
#define call_00567550_from_0056ca00 ((unsigned long (__cdecl *)(unsigned long, unsigned long, unsigned long, unsigned long, unsigned long))0x00567550)

unsigned long __cdecl call_five_0056ca00(unsigned long a, unsigned long b, unsigned long c)
{
    return call_00567550_from_0056ca00(a, b, 0, c, 2);
}
