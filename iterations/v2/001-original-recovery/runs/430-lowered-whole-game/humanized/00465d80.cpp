/* 00465d80: picks one of two global values depending on the state of the current object. */
#define current_00465d80 (*(unsigned char **)0x00628c70)
#define value_a_00465d80 (*(long *)0x00606858)
#define value_b_00465d80 (*(long *)0x0065741c)

long __cdecl pick_value_00465d80(void)
{
    unsigned char *o = current_00465d80;
    if (o != 0 && *(long *)(o + 8) != 0 && o[0xbf] == 0 && o[0xbd] != 0)
        return value_a_00465d80;
    return value_b_00465d80;
}
