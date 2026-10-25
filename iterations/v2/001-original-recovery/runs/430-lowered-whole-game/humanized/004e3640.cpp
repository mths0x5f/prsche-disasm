/* 004e3640: Returns whether the global dword at 0x00657e50 is zero (AL only). */
#define global_00657e50 (*(unsigned long *)0x00657e50)

unsigned char __cdecl global_is_zero_657e50_004e3640(void)
{
    return global_00657e50 == 0;
}
