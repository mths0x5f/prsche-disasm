/* 00570490: copies count 16-bit values from the low words of a dword array into a packed word array. */
void __cdecl pack_words_00570490(unsigned short *dest, unsigned long *src, long count)
{
    if (count > 0) {
        do {
            *dest = *(unsigned short *)src;
            src++;
            dest++;
        } while (--count != 0);
    }
}
