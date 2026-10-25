/* 005654d0: Counts one more input binding change (a global counter). */
#define input_binding_changes_006a5c2c (*(long *)0x006a5c2c)

void __cdecl window_input_binding_changed_005654d0(void)
{
    ++input_binding_changes_006a5c2c;
}
