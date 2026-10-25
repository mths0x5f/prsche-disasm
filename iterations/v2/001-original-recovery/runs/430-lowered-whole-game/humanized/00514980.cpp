/* 00514980: Returns the dword at +0xe4 of the object at +0xfc. */
struct Inner_00514980 {
    unsigned char unknown_00[0xe4];
    unsigned long field_e4;
};

struct Object_00514980 {
    unsigned char unknown_00[0xfc];
    Inner_00514980 *inner;
    unsigned long read_00514980();
};

unsigned long Object_00514980::read_00514980()
{
    return inner->field_e4;
}
