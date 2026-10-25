/* 004e35d0: whether the value 0053c3d0 reports is below 0x2100000. */
#define query_0053c3d0 ((long (__cdecl *)(void))0x0053c3d0)

bool __cdecl below_limit_004e35d0(void)
{
    return query_0053c3d0() < 0x2100000;
}
