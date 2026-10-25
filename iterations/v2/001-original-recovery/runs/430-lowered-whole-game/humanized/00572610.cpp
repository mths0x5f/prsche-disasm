/* 00572610: calls 00531ca0(0x5c081c, arg, global 005deb60). */
#define stream_005deb60 (*(unsigned long *)0x005deb60)
#define call_00531ca0_from_00572610 ((unsigned long (__cdecl *)(unsigned long, unsigned long, unsigned long))0x00531ca0)

unsigned long __cdecl call_with_name_00572610(unsigned long a)
{
    return call_00531ca0_from_00572610(0x5c081c, a, stream_005deb60);
}
