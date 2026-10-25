/* 005611e0: sum of 005611d0(arg) and 00589790(). */
#define call_005611d0_from_005611e0 ((unsigned long (__cdecl *)(unsigned long))0x005611d0)
#define call_00589790_from_005611e0 ((unsigned long (__cdecl *)(void))0x00589790)

unsigned long __cdecl sum_005611e0(unsigned long a)
{
    unsigned long first = call_005611d0_from_005611e0(a);
    unsigned long second = call_00589790_from_005611e0();
    return second + first;
}
