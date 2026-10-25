/* 004e2960: returns the byte at offset 0x20 of the object. */
struct Object_004e2960 {
    char pad_00[32];
    unsigned char value;
    unsigned char fn_004e2960();
};

unsigned char Object_004e2960::fn_004e2960()
{
    return value;
}
