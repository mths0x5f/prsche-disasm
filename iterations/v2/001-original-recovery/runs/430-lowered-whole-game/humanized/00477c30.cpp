/* 00477c30: Returns the pointer at +0x30 plus index*64. */
struct Object_00477c30 {
    unsigned char unknown_00[48];
    unsigned long base;
    unsigned long entry_00477c30(unsigned long index);
};

unsigned long Object_00477c30::entry_00477c30(unsigned long index)
{
    return (index << 6) + base;
}
