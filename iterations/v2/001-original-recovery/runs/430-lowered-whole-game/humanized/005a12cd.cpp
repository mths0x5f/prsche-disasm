/* 005a12cd: Swaps two byte ranges of `size` bytes (the qsort element swap); nothing when they are the same. */
void __cdecl sort_swap_005a12cd(char *a, char *b, unsigned long size)
{
    char t;

    if (a == b)
        return;
    while (size--) {
        t = *a;
        *a++ = *b;
        *b++ = t;
    }
}
