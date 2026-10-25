/* 005a8c02: getc: next byte of the stream buffer, or 005a77aa(stream) when the count runs out. */
struct Stream_005a8c02 {
    unsigned char *ptr;
    long count;
};
#define refill_005a77aa_from_005a8c02 ((unsigned long (__cdecl *)(Stream_005a8c02 *))0x005a77aa)

unsigned long __cdecl get_char_005a8c02(Stream_005a8c02 *stream)
{
    if (--stream->count < 0)
        return refill_005a77aa_from_005a8c02(stream);
    return *stream->ptr++;
}
