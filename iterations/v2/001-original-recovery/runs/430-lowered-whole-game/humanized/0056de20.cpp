/* 0056de20: calls 0056daf0(a, b, 1.0f, 1.0f, c) (the floats are passed as raw bits). */
#define call_0056daf0 ((unsigned long (__cdecl *)(unsigned long, unsigned long, unsigned long, unsigned long, unsigned long))0x0056daf0)

unsigned long __cdecl call_0056de20(unsigned long a, unsigned long b, unsigned long c)
{
    return call_0056daf0(a, b, 0x3f800000, 0x3f800000, c);
}
