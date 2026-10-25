/* 00422de0: Clears the global dword at 0x0060c9a0. */
#define global_0060c9a0 (*(unsigned long *)0x0060c9a0)

void __cdecl clear_global_60c9a0_00422de0(void)
{
    global_0060c9a0 = 0;
}
