/* 00539d90: copies 16 dwords from the argument into the object. */
struct Object_00539d90 {
    unsigned long data[16];
    void copy(unsigned long *src);
};

void Object_00539d90::copy(unsigned long *src)
{
    int i;
    for (i = 0; i < 16; i++)
        data[i] = src[i];
}
