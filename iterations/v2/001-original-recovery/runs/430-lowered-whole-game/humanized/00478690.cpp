/* 00478690: Returns the pointer at +0x14 plus 0x10, or 0 when it is null. */
struct Object_00478690 {
    unsigned char unknown_00[20];
    char * block;
    char *inner_00478690();
};

char *Object_00478690::inner_00478690()
{
    if (block == 0)
        return 0;
    return block + 0x10;
}
