/* 00453c60: constructor: runs 0053f320(3, arg) on this and installs vtable 0x5b3dac. */
struct Object_00453c60 {
    void *vtable;
    void base_0053f320(long code, unsigned long arg);
    Object_00453c60 *construct(unsigned long arg);
};

__declspec(naked) void Object_00453c60::base_0053f320(long code, unsigned long arg)
{
    __asm mov eax, 0x0053f320
    __asm jmp eax
}

Object_00453c60 *Object_00453c60::construct(unsigned long arg)
{
    base_0053f320(3, arg);
    vtable = (void *)0x5b3dac;
    return this;
}
