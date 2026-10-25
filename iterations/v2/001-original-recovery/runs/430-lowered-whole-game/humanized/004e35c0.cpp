/* 004e35c0: Returns whether the global dword at 0x005d9d38 is zero. */
#define global_005d9d38 (*(unsigned long *)0x005d9d38)

unsigned long __cdecl global_is_zero_5d9d38_004e35c0(void)
{
    return global_005d9d38 == 0;
}
