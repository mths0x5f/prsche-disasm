
undefined4 * __thiscall
FUN_004930f0(undefined4 *receiver_bits,undefined4 *stack_4_bits,undefined4 stack_8_bits)

{
  undefined4 *puVar1;
  
  puVar1 = (undefined4 *)*receiver_bits;
  *receiver_bits = *puVar1;
  *stack_4_bits = puVar1;
  return stack_4_bits;
}

