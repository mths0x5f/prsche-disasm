/* 00557400: number of set bits of its argument. */
unsigned long popcount_00557400(unsigned long x)
{
    unsigned long n = 0;
    while (x != 0) {
        x &= x - 1;
        n++;
    }
    return n;
}
