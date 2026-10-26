/* 0053eea0: stores its two further arguments at +0x3c and +0x40 of the first. */
struct Block_0053eea0 {
    unsigned char unknown_00[0x3c];
    unsigned long first;
    unsigned long second;
};

void set_0053eea0(Block_0053eea0 *p, unsigned long a, unsigned long b)
{
    p->first = a;
    p->second = b;
}
