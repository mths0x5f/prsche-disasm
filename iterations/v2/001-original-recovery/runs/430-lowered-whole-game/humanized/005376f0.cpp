/* 005376f0: Calls the member at 0x00540660 on the object in global 0x0069e0d4, passing its own this as the argument. */
struct Target_005376f0 {
    unsigned long unknown_00;
    unsigned long call_00540660(unsigned long value);
};

struct Caller_005376f0 {
    unsigned long unknown_00;
    unsigned long run_005376f0();
};

#define target_0069e0d4 (*(Target_005376f0 **)0x0069e0d4)

__declspec(naked) unsigned long Target_005376f0::call_00540660(unsigned long value)
{
    __asm mov eax, 0x00540660
    __asm jmp eax
}

unsigned long Caller_005376f0::run_005376f0()
{
    return target_0069e0d4->call_00540660((unsigned long)this);
}
