
void __thiscall FUN_00489370(int param_1,undefined4 param_2)

{
  uint stack_4_bits;
  
  stack_4_bits = 0;
  if (*(int *)(param_1 + 0x18) != 0) {
    do {
      FUN_00489530(param_1,stack_4_bits,param_2);
      stack_4_bits = stack_4_bits + 1;
    } while (stack_4_bits < *(uint *)(param_1 + 0x18));
  }
  return;
}

