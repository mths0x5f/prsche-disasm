
int * __thiscall FUN_0043f8a0(int *receiver_bits,int *stack_4_bits,undefined4 stack_8_bits)

{
  int iVar1;
  int iVar2;
  
  iVar1 = *receiver_bits;
  iVar2 = *(int *)(iVar1 + 0xc);
  if (iVar2 == 0) {
    iVar2 = *(int *)(iVar1 + 4);
    if (iVar1 == *(int *)(iVar2 + 0xc)) {
      do {
        *receiver_bits = iVar2;
        iVar2 = *(int *)(iVar2 + 4);
      } while (*receiver_bits == *(int *)(iVar2 + 0xc));
    }
    if (*(int *)(*receiver_bits + 0xc) != iVar2) {
      *receiver_bits = iVar2;
    }
  }
  else {
    *receiver_bits = iVar2;
    if (*(int *)(iVar2 + 8) != 0) {
      do {
        iVar2 = *(int *)(*receiver_bits + 8);
        *receiver_bits = iVar2;
      } while (*(int *)(iVar2 + 8) != 0);
      *stack_4_bits = iVar1;
      return stack_4_bits;
    }
  }
  *stack_4_bits = iVar1;
  return stack_4_bits;
}

