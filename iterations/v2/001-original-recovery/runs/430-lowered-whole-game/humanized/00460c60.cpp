/* 00460c60: Forwards its argument to the member at 0x00460b50 on the same object. */
struct Object_00460c60 {
    unsigned long unknown_00;
    unsigned long forward_460b50_00460c60(unsigned long value);
    unsigned long call_00460b50(unsigned long value);
};

__declspec(naked) unsigned long Object_00460c60::call_00460b50(unsigned long value)
{
    __asm mov eax, 0x00460b50
    __asm jmp eax
}

unsigned long Object_00460c60::forward_460b50_00460c60(unsigned long value)
{
    return call_00460b50(value);
}
