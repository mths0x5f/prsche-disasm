/* 005adb2d: shifts a 96-bit value (three dwords, low first) left by one bit. */
void *__cdecl shl1_96_005adb2d(unsigned long *v)
{
    unsigned long low = v[0];
    unsigned long mid = v[1];
    v[0] = low << 1;
    v[1] = (mid << 1) | (low >> 31);
    v[2] = (v[2] << 1) | (mid >> 31);
    return v;
}
