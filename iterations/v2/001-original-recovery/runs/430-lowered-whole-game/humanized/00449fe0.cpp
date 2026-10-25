/* 00449fe0: constructor: runs 0053f320(5, arg) on this and installs vtable 0x5b3bf0. */
struct Object_00449fe0 {
    void *vtable;
    void base_0053f320(long code, unsigned long arg);
    Object_00449fe0 *construct(unsigned long arg);
};

__declspec(naked) void Object_00449fe0::base_0053f320(long code, unsigned long arg)
{
    __asm mov eax, 0x0053f320
    __asm jmp eax
}

Object_00449fe0 *Object_00449fe0::construct(unsigned long arg)
{
    base_0053f320(5, arg);
    vtable = (void *)0x5b3bf0;
    return this;
}
