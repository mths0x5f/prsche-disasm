/* 00572fdd: Byte-swaps its argument, then rotates it right by 8. */
unsigned long __cdecl swap_rotate_00572fdd(unsigned long value)
{
    unsigned long swapped = (value >> 24) | ((value >> 8) & 0xff00) | ((value << 8) & 0xff0000) | (value << 24);

    return (swapped >> 8) | (swapped << 24);
}
