/* 005a3be5: _malloc, calls __nh_malloc(size, global 0x6afec8). */
#define callee_005a3bf7_005a3be5 ((unsigned long (__cdecl *)(unsigned long, unsigned long))0x005a3bf7)
#define g_006afec8_005a3be5 (*(unsigned long *)0x006afec8)

unsigned long _malloc_005a3be5(unsigned long size)
{
    return callee_005a3bf7_005a3be5(size, g_006afec8_005a3be5);
}
