/* 0052dc20: forwards two arguments to a method of the global component at 0069caf8. */
struct Component_0052dc20 {
    unsigned long unknown_00;
    unsigned long call_0052e010(unsigned long a, unsigned long b);
};
#define component_0069caf8 (*(Component_0052dc20 **)0x0069caf8)

__declspec(naked) unsigned long Component_0052dc20::call_0052e010(unsigned long a, unsigned long b)
{
    __asm mov eax, 0x0052e010
    __asm jmp eax
}

unsigned long __cdecl forward_0052dc20(unsigned long a, unsigned long b)
{
    return component_0069caf8->call_0052e010(a, b);
}
