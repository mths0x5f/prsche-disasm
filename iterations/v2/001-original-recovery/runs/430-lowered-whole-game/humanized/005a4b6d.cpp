/* 005a4b6d: va_arg for a short: advances the argument cursor and returns the 16-bit value. */
short __cdecl format_next_short_005a4b6d(char **cursor)
{
    *cursor += 4;
    return *(short *)(*cursor - 4);
}
