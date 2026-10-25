/* 004d55c0: strlen. */
unsigned long __cdecl context_strlen_004d55c0(const char *text)
{
    const char *p = text;
    while (*p)
        ++p;
    return (unsigned long)(p - text);
}
