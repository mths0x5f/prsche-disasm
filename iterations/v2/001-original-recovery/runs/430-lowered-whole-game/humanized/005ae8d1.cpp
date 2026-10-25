/* 005ae8d1: wide-character string length, at most n characters. */
unsigned long __cdecl wcsnlen_005ae8d1(const unsigned short *s, unsigned long n)
{
    const unsigned short *p = s;
    unsigned long k = n;
    while (k != 0 && *p != 0) {
        p++;
        k--;
    }
    if (*p == 0)
        return p - s;
    return n;
}
