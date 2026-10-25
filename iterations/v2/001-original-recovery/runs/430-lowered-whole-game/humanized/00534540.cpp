/* 00534540: Calls 0x00534480 with the constant 0x5de680. */
#define callee_00534480 ((unsigned long (__cdecl *)(unsigned long))0x00534480)

unsigned long __cdecl call_534480_00534540(void)
{
    return callee_00534480(0x5de680);
}
