/* 00525570: Returns the dword at +0x38 of the object at +0xf4. */
struct Inner_00525570 {
    unsigned char unknown_00[0x38];
    unsigned long field_38;
};

struct Object_00525570 {
    unsigned char unknown_00[0xf4];
    Inner_00525570 *inner;
    unsigned long read_00525570();
};

unsigned long Object_00525570::read_00525570()
{
    return inner->field_38;
}
