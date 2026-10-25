/* 004e3620: Returns whether the global dword at 0x00657e48 is zero (AL only). */
#define global_00657e48 (*(unsigned long *)0x00657e48)

unsigned char __cdecl global_is_zero_657e48_004e3620(void)
{
    return global_00657e48 == 0;
}
