/* 00535ff0: Passes the dword at +0x8 to the function at 0x00554e30. */
#define callee_00554e30 ((unsigned long (__cdecl *)(unsigned long))0x00554e30)

struct Object_00535ff0 {
    unsigned char unknown_00[8];
    unsigned long field_8;
    unsigned long forward_field_8_00535ff0();
};

unsigned long Object_00535ff0::forward_field_8_00535ff0()
{
    return callee_00554e30(field_8);
}
