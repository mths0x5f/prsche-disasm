/* 004e0de0: whether the word at +0x12c is 3 or 1. */
struct Object_004e0de0 {
    unsigned char unknown_00[0x12c];
    long state;
    int is_active();
};

int Object_004e0de0::is_active()
{
    return state == 3 || state == 1;
}
