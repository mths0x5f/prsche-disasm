/* 0052dee0: copies the two dwords at +0x8 and +0xc of the object to the buffer given. */
struct Object_0052dee0 {
    unsigned char unknown_00[8];
    unsigned long first;
    unsigned long second;
    unsigned long *copy(unsigned long *out);
};

unsigned long *Object_0052dee0::copy(unsigned long *out)
{
    unsigned long a = first;
    unsigned long b = second;
    out[0] = a;
    out[1] = b;
    return out;
}
