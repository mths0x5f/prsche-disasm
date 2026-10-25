/* 004e3650: Returns whether the global dword at 0x00657e54 is zero (AL only). */
#define global_00657e54 (*(unsigned long *)0x00657e54)

unsigned char __cdecl global_is_zero_657e54_004e3650(void)
{
    return global_00657e54 == 0;
}
