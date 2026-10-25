/* 0044a130: constructor: runs 0053f320(-1, arg) on this and installs vtable 0x5b3c6c. */
struct Object_0044a130 {
    void *vtable;
    void base_0053f320(long code, unsigned long arg);
    Object_0044a130 *construct(unsigned long arg);
};

__declspec(naked) void Object_0044a130::base_0053f320(long code, unsigned long arg)
{
    __asm mov eax, 0x0053f320
    __asm jmp eax
}

Object_0044a130 *Object_0044a130::construct(unsigned long arg)
{
    base_0053f320(-1, arg);
    vtable = (void *)0x5b3c6c;
    return this;
}
