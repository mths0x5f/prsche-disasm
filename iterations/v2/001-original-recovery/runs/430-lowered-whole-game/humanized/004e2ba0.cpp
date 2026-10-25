/* 004e2ba0: returns a word of the object that the member at 0x4 points to. */
struct Inner_004e2ba0 {
    char pad_00[60];
    unsigned long value;
};

struct Object_004e2ba0 {
    char pad_00[4];
    Inner_004e2ba0 *inner;
    unsigned long fn_004e2ba0();
};

unsigned long Object_004e2ba0::fn_004e2ba0()
{
    return inner->value;
}
