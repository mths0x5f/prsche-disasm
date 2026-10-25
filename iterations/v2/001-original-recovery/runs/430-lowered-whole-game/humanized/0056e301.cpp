/* 0056e301: Stores the low 1..4 bytes of a value at a pointer (size 3 as word then byte) and returns the advanced pointer. */
unsigned char *__cdecl store_bytes_0056e301(unsigned char *dst, unsigned long value, long size)
{
    if (size >= 3) {
        if (size == 3) {
            *(unsigned short *)dst = (unsigned short)value;
            value >>= 16;
            *dst = (unsigned char)value;
            return dst + 3;
        }
        *(unsigned long *)dst = value;
        return dst + 4;
    }
    if (size < 1)
        return dst;
    if (size == 1) {
        *dst = (unsigned char)value;
        return dst + 1;
    }
    *(unsigned short *)dst = (unsigned short)value;
    return dst + 2;
}
