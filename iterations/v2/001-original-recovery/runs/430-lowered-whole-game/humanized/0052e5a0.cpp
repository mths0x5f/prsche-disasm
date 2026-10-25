/* 0052e5a0: whether the first character is a decimal digit. */
int __cdecl is_digit_0052e5a0(const char *text)
{
    char c = text[0];
    return c >= '0' && c <= '9';
}
