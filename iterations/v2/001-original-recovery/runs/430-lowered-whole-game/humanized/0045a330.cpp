/* 0045a330: sets the current index at +0xc and the next (wrapped at the count in +8) at +0x10. */
struct Ring_0045a330 {
    unsigned long unknown_00;
    unsigned long unknown_04;
    long count;
    long current;
    long next;
    void set_current(long index);
};

void Ring_0045a330::set_current(long index)
{
    long n = count;
    current = index;
    next = index + 1;
    if (index + 1 >= n)
        next = 0;
}
