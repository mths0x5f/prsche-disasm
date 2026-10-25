/* 005a3dba: calls 005ab7dc(0x10000, 0x30000). */
#define callee_005ab7dc_005a3dba ((unsigned long (__cdecl *)(unsigned long, unsigned long))0x005ab7dc)

unsigned long forward_005a3dba(void)
{
    return callee_005ab7dc_005a3dba(0x10000, 0x30000);
}
