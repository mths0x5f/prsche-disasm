/* 004e07a0: Passes the global dword at 0x005d9b48 to the function at 0x0059ec40. */
#define callee_0059ec40 ((unsigned long (__cdecl *)(unsigned long))0x0059ec40)
#define global_005d9b48 (*(unsigned long *)0x005d9b48)

unsigned long __cdecl forward_global_5d9b48_004e07a0(void)
{
    return callee_0059ec40(global_005d9b48);
}
