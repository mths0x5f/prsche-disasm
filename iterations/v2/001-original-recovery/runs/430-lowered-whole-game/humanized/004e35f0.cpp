/* 004e35f0: Returns whether the global dword at 0x00657e3c is zero (AL only). */
#define global_00657e3c (*(unsigned long *)0x00657e3c)

unsigned char __cdecl global_is_zero_657e3c_004e35f0(void)
{
    return global_00657e3c == 0;
}
