/* 00536cc0: calls 0053e5c0 with the object word at +4, the constant 0xc and the argument. */
struct Object_00536cc0 {
    unsigned long unknown_00;
    unsigned long handle;
    unsigned long call(unsigned long arg);
};
#define call_0053e5c0_from_00536cc0 ((unsigned long (__cdecl *)(unsigned long, unsigned long, unsigned long))0x0053e5c0)

unsigned long Object_00536cc0::call(unsigned long arg)
{
    return call_0053e5c0_from_00536cc0(handle, 0xc, arg);
}
