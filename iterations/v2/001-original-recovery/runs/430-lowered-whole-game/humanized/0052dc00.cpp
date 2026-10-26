/* 0052dc00: initialises one global component, then tail-calls the finish routine of another. */
struct Component_0052dc00 {
    unsigned long unknown_00;
    void init_0052df20();
    void finish_0052dfa0();
};
#define first_component_0069cafc (*(Component_0052dc00 **)0x0069cafc)
#define second_component_0069caf8 (*(Component_0052dc00 **)0x0069caf8)

__declspec(naked) void Component_0052dc00::init_0052df20()
{
    __asm mov eax, 0x0052df20
    __asm jmp eax
}
__declspec(naked) void Component_0052dc00::finish_0052dfa0()
{
    __asm mov eax, 0x0052dfa0
    __asm jmp eax
}

void __cdecl setup_components_0052dc00(void)
{
    first_component_0069cafc->init_0052df20();
    second_component_0069caf8->finish_0052dfa0();
}
