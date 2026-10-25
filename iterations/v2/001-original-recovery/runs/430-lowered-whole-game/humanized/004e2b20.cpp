/* 004e2b20: Returns the dword at +0x38 of the object the first dword points to plus *argument. */
struct Inner_004e2b20 {
    unsigned char unknown_00[0x38];
    unsigned long field_38;
};

struct Object_004e2b20 {
    Inner_004e2b20 *inner;
    unsigned long sum_004e2b20(unsigned long *addend);
};

unsigned long Object_004e2b20::sum_004e2b20(unsigned long *addend)
{
    unsigned long base = inner->field_38;

    return base + *addend;
}
