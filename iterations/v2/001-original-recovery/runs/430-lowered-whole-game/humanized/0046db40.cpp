/* 0046db40: copies the dwords [first, last) backwards so that they end just before dest_end; returns the new start. */
unsigned long *__cdecl copy_backward_0046db40(unsigned long *first, unsigned long *last, unsigned long *dest_end)
{
    long n = last - first;
    if (n > 0) {
        do {
            last--;
            dest_end--;
            *dest_end = *last;
            n--;
        } while (n != 0);
        return dest_end;
    }
    return dest_end;
}
