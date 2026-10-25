/* 004e3630: Returns whether the global dword at 0x00657e4c is zero (AL only). */
#define global_00657e4c (*(unsigned long *)0x00657e4c)

unsigned char __cdecl global_is_zero_657e4c_004e3630(void)
{
    return global_00657e4c == 0;
}
