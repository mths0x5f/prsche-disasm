/* 0056dac0: stdcall: calls 00531ca0(0, arg, global 005deb60). */
#define stream_005deb60 (*(unsigned long *)0x005deb60)
#define call_00531ca0_from_0056dac0 ((unsigned long (__cdecl *)(unsigned long, unsigned long, unsigned long))0x00531ca0)

unsigned long __stdcall call_with_stream_0056dac0(unsigned long a)
{
    return call_00531ca0_from_0056dac0(0, a, stream_005deb60);
}
