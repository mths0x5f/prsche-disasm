/* 005a4b5d: va_arg for a 64-bit integer: advances the argument cursor by 8 and returns it in EDX:EAX. */
__int64 __cdecl format_next_int64_005a4b5d(char **cursor)
{
    *cursor += 8;
    return *(__int64 *)(*cursor - 8);
}
