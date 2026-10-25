/* 005abc89: calls 005abb07 with the two arguments and the constant 0x5e6140. */
#define call_005abb07_from_005abc89 ((unsigned long (__cdecl *)(unsigned long, unsigned long, unsigned long))0x005abb07)

unsigned long __cdecl call_with_table_005abc89(unsigned long a, unsigned long b)
{
    return call_005abb07_from_005abc89(a, b, 0x5e6140);
}
