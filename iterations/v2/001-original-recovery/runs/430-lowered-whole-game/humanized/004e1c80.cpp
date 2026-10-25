/* 004e1c80: Clears the global dword at 0x00690720. */
#define global_00690720 (*(unsigned long *)0x00690720)

void __cdecl clear_global_690720_004e1c80(void)
{
    global_00690720 = 0;
}
