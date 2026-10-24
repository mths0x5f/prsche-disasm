/* 005a2870: the C runtime's strrchr: last occurrence of `ch` in `text`; the terminator
 * itself is found when `ch` is 0. The original scans backwards with std / repne scasb.
 */
char * __cdecl formatter_text_find_last_005a2870(const char *text, int ch)
{
    const char *p = text;
    char c = (char)ch;

    while (*p)
        ++p;
    for (;;) {
        if (*p == c)
            return (char *)p;
        if (p == text)
            return 0;
        --p;
    }
}
