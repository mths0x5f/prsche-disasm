/* 0056e290: big-endian load of the dword at the pointer, shifted right by 32 - 8*n (mod 32). */
unsigned long __cdecl load_be_shifted_0056e290(const unsigned long *p, unsigned long n)
{
    unsigned long v = *p;
    v = (v << 24) | ((v & 0xff00) << 8) | ((v >> 8) & 0xff00) | (v >> 24);
    return v >> ((0x20 - n * 8) & 31);
}
