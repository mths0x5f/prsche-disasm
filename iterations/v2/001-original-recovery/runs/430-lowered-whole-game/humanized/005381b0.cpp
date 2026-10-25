/* 005381b0: swaps the global 0069e0d0 with the argument, sets 005dea78 to -1 and returns the old value. */
#define current_0069e0d0 (*(unsigned long *)0x0069e0d0)
#define marker_005dea78 (*(unsigned long *)0x005dea78)

unsigned long __cdecl swap_current_005381b0(unsigned long value)
{
    unsigned long old = current_0069e0d0;
    current_0069e0d0 = value;
    marker_005dea78 = 0xffffffff;
    return old;
}
