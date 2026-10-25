/* 005adaae: Adds two words for the float formatter; stores the sum and returns 1 on carry. */
long __cdecl float_add_carry_005adaae(unsigned long a, unsigned long b, unsigned long *sum)
{
    unsigned long s = a + b;
    long carry = 0;

    if (s < a || s < b)
        carry = 1;
    *sum = s;
    return carry;
}
