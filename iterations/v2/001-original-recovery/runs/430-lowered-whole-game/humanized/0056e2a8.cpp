/* 0056e2a8: dword ending at p + n, shifted right by 32 - 8*n (mod 32). */
unsigned long __cdecl load_tail_shifted_0056e2a8(unsigned long p, unsigned long n)
{
    unsigned long v = *(unsigned long *)(p + n - 4);
    return v >> ((0x20 - n * 8) & 31);
}
