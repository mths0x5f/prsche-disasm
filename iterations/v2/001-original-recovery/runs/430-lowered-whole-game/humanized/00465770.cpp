/* 00465770: reads the signed 16-bit field of entry n of the 268-byte table at 00627f3c. */
struct Entry_00465770 {
    short value;
    unsigned char unknown_02[266];
};
#define table_00627f3c ((Entry_00465770 *)0x00627f3c)

long __cdecl entry_value_00465770(long index)
{
    return table_00627f3c[index].value;
}
