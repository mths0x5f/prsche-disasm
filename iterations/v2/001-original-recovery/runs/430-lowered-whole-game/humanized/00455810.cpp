/* 00455810: Forwards its argument to the member at 0x0043fa80 on the same object. */
struct Object_00455810 {
    unsigned long unknown_00;
    unsigned long forward_43fa80_00455810(unsigned long value);
    unsigned long call_0043fa80(unsigned long value);
};

__declspec(naked) unsigned long Object_00455810::call_0043fa80(unsigned long value)
{
    __asm mov eax, 0x0043fa80
    __asm jmp eax
}

unsigned long Object_00455810::forward_43fa80_00455810(unsigned long value)
{
    return call_0043fa80(value);
}
