/* 0044ff60: constructor: runs the base constructor 00450c40 on the argument and installs vtable 0x5b3cb8. */
struct Object_0044ff60 {
    void *vtable;
    void base_00450c40(unsigned long arg);
    Object_0044ff60 *construct(unsigned long arg);
};

__declspec(naked) void Object_0044ff60::base_00450c40(unsigned long arg)
{
    __asm mov eax, 0x00450c40
    __asm jmp eax
}

Object_0044ff60 *Object_0044ff60::construct(unsigned long arg)
{
    base_00450c40(arg);
    vtable = (void *)0x5b3cb8;
    return this;
}
