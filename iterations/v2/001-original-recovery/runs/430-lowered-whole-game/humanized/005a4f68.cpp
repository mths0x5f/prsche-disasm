/* 005a4f68: CRT helper: the exponent bits of the high word, or the whole word when they are all set. */
unsigned long __cdecl exponent_bits_005a4f68(unsigned long low, unsigned long high)
{
    unsigned long bits = high & 0x7ff00000;
    if (bits == 0x7ff00000)
        return high;
    return bits;
}
