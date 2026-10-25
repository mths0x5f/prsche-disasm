/* 005ad2bf: strnlen: length of `text`, at most `limit`. */
unsigned long __cdecl locale_strnlen_005ad2bf(const char *text, unsigned long limit)
{
    unsigned long n = 0;

    while (n < limit && text[n])
        ++n;
    return n;
}
