/* 00536460: Passes the dword at +0x8 to the function at 0x00555630. */
#define callee_00555630 ((unsigned long (__cdecl *)(unsigned long))0x00555630)

struct Object_00536460 {
    unsigned char unknown_00[8];
    unsigned long field_8;
    unsigned long forward_field_8_00536460();
};

unsigned long Object_00536460::forward_field_8_00536460()
{
    return callee_00555630(field_8);
}
