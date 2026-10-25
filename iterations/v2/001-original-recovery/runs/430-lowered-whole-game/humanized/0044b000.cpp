/* 0044b000: calls 0044d320 on (this + 0xc) with its two arguments. */
struct Object_0044b000 {
    unsigned long fn_0044d320(unsigned long a, unsigned long b);
    unsigned long forward(unsigned long a, unsigned long b);
};

__declspec(naked) unsigned long Object_0044b000::fn_0044d320(unsigned long a, unsigned long b)
{
    __asm mov eax, 0x0044d320
    __asm jmp eax
}

unsigned long Object_0044b000::forward(unsigned long a, unsigned long b)
{
    return ((Object_0044b000 *)((char *)this + 0xc))->fn_0044d320(a, b);
}
