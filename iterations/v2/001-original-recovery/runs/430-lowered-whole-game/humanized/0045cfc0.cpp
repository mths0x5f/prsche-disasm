/* 0045cfc0: Calls the member at 0x0045a350 on the object at +0x44 with the dword at +0x50. */
struct Object_0045cfc0 {
    unsigned char unknown_00[0x44];
    struct Object_0045cfc0 *target;
    unsigned long unknown_48[2];
    unsigned long field_50;
    unsigned long run_0045cfc0();
    unsigned long call_0045a350(unsigned long value);
};

__declspec(naked) unsigned long Object_0045cfc0::call_0045a350(unsigned long value)
{
    __asm mov eax, 0x0045a350
    __asm jmp eax
}

unsigned long Object_0045cfc0::run_0045cfc0()
{
    unsigned long value = field_50;

    return target->call_0045a350(value);
}
