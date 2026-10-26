/* 00534550: calls 00534480 with the constant 0. */
#define callee_00534480 ((unsigned long (__cdecl *)(unsigned long))0x534480)

unsigned long __cdecl fn_00534550(void)
{
    return callee_00534480(0);
}
