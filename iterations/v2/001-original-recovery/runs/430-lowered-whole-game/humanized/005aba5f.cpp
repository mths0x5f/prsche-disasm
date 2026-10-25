/* 005aba5f: Nonzero when a 12-byte number of the float parser is zero. */
long __cdecl float_parse_is_zero_005aba5f(const unsigned long *value)
{
    long i;

    for (i = 0; i < 3; ++i)
        if (value[i])
            return 0;
    return 1;
}
