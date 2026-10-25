/* 0045dd00: Calls 0x0045dbd0 with (its argument, 1). */
#define callee_0045dbd0 ((unsigned long (__cdecl *)(unsigned long, unsigned long))0x0045dbd0)

unsigned long __cdecl call_45dbd0_0045dd00(unsigned long value)
{
    return callee_0045dbd0(value, 1);
}
