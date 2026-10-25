/* 00468e30: forwards one of two (float, float) pairs, chosen by the flag, to the member of the object at offset 4. */
struct Target_00468e30 {
    unsigned long set_00466eb0(float a, float b);
};
struct Owner_00468e30 {
    unsigned long unknown_00;
    Target_00468e30 *target;
    unsigned long apply_00468e30(unsigned char flag);
};

__declspec(naked) unsigned long Target_00468e30::set_00466eb0(float a, float b)
{
    __asm mov eax, 0x00466eb0
    __asm jmp eax
}

unsigned long Owner_00468e30::apply_00468e30(unsigned char flag)
{
    if (flag)
        return target->set_00466eb0(0.15f, 0.85f);
    return target->set_00466eb0(0.0f, 1.0f);
}
