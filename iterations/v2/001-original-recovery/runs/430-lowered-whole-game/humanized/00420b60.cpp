/* 00420b60: Returns the two dwords at 0x0060c830 as EDX:EAX. */
#define pair_0060c830 (*(unsigned __int64 *)0x0060c830)

unsigned __int64 __cdecl read_pair_60c830_00420b60(void)
{
    return pair_0060c830;
}
