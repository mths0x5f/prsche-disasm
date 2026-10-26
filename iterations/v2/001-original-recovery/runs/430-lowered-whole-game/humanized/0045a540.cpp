/* 0045a540: sets the current index at +8 and the next (wrapped at the count in +4) at +0xc. */
struct Ring_0045a540 {
    unsigned long unknown_00;
    long count;
    long current;
    long next;
    void set_current(long index);
};

void Ring_0045a540::set_current(long index)
{
    long n = count;
    current = index;
    next = index + 1;
    if (index + 1 >= n)
        next = 0;
}
