/* 004e2b90: returns a word of the object that the member at 0x4 points to. */
struct Inner_004e2b90 {
    char pad_00[56];
    unsigned long value;
};

struct Object_004e2b90 {
    char pad_00[4];
    Inner_004e2b90 *inner;
    unsigned long fn_004e2b90();
};

unsigned long Object_004e2b90::fn_004e2b90()
{
    return inner->value;
}
