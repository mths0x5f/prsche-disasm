/* 00570610: Converts an array of values with 00572f30, keeping each source's top byte. */
#define convert_00572f30 ((unsigned long (__cdecl *)(unsigned long))0x00572f30)

void __cdecl convert_array_00570610(unsigned long *dst, const unsigned long *src, long count)
{
    while (count > 0) {
        unsigned long value = *src;

        *dst = convert_00572f30(value) | (value & 0xff000000);
        ++src;
        ++dst;
        --count;
    }
}
