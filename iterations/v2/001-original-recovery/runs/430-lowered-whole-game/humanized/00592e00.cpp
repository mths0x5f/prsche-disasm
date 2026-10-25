/* 00592e00: Sets the attribute byte of the monochrome debug display (a global). */
#define mono_attribute_005e25e8 (*(unsigned char *)0x005e25e8)

void __cdecl mono_set_attribute_00592e00(unsigned char attribute)
{
    mono_attribute_005e25e8 = attribute;
}
