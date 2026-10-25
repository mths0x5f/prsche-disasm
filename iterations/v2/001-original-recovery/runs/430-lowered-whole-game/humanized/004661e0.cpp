/* 004661e0: Initializes two 36-byte blocks from the template at 005bb2d0 and zeroes the words around them. */
struct Pair_004661e0 {
    unsigned long first_00[9];
    unsigned long zero_24[3];
    unsigned long second_30[9];
    unsigned long zero_54[3];
    Pair_004661e0 *init_004661e0();
};

Pair_004661e0 *Pair_004661e0::init_004661e0()
{
    const unsigned long *tmpl = (const unsigned long *)0x005bb2d0;
    long i;

    for (i = 0; i < 9; ++i)
        second_30[i] = tmpl[i];
    zero_54[0] = 0;
    zero_54[1] = 0;
    zero_54[2] = 0;
    for (i = 0; i < 9; ++i)
        first_00[i] = tmpl[i];
    zero_24[0] = 0;
    zero_24[1] = 0;
    zero_24[2] = 0;
    return this;
}
