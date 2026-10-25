/* 005a4b50: va_arg for an int: advances the argument cursor and returns the value. */
long __cdecl format_next_int_005a4b50(char **cursor)
{
    *cursor += 4;
    return *(long *)(*cursor - 4);
}
