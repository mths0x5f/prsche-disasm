/* 004e3660: Returns whether the global dword at 0x00657e58 is zero (AL only). */
#define global_00657e58 (*(unsigned long *)0x00657e58)

unsigned char __cdecl global_is_zero_657e58_004e3660(void)
{
    return global_00657e58 == 0;
}
