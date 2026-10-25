/* 00452100: whether the two dwords at +4 and +8 are both zero. */
struct Object_00452100 {
    unsigned long unknown_00;
    unsigned long first;
    unsigned long second;
    bool both_zero();
};

bool Object_00452100::both_zero()
{
    return first == 0 && second == 0;
}
