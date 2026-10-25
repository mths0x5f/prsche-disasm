/* 00539f40: Marks the object used, increments the counter at +0x10 and returns the dword at +4. */
struct Object_00539f40 {
    unsigned char unknown_00[4];
    unsigned long value;
    unsigned char unknown_08[8];
    unsigned long counter;
    unsigned char unknown_14[4];
    unsigned char used;
    unsigned long touch_00539f40();
};

unsigned long Object_00539f40::touch_00539f40()
{
    unsigned long count = counter;

    used = 1;
    counter = count + 1;
    return value;
}
