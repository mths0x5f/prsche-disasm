/* 00538d80: runs 00539eb0 on the sub-object at +0x5c, then on the object itself. */
struct Object_00538d80 {
    unsigned long fn_00539eb0();
    unsigned long run();
};

__declspec(naked) unsigned long Object_00538d80::fn_00539eb0()
{
    __asm mov eax, 0x00539eb0
    __asm jmp eax
}

unsigned long Object_00538d80::run()
{
    ((Object_00538d80 *)((char *)this + 0x5c))->fn_00539eb0();
    return fn_00539eb0();
}
