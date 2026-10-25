/* 0053e5b0: Clears the global dword at 0x0069eba8. */
#define global_0069eba8 (*(unsigned long *)0x0069eba8)

void __cdecl clear_global_69eba8_0053e5b0(void)
{
    global_0069eba8 = 0;
}
