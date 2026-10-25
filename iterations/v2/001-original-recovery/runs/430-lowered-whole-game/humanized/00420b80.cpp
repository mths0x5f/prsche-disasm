/* 00420b80: Returns the two dwords at 0x0060c880 as EDX:EAX. */
#define pair_0060c880 (*(unsigned __int64 *)0x0060c880)

unsigned __int64 __cdecl read_pair_60c880_00420b80(void)
{
    return pair_0060c880;
}
