/* 004e3610: Returns whether the global dword at 0x00657e44 is zero (AL only). */
#define global_00657e44 (*(unsigned long *)0x00657e44)

unsigned char __cdecl global_is_zero_657e44_004e3610(void)
{
    return global_00657e44 == 0;
}
