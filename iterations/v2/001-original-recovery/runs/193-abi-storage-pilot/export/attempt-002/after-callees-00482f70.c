
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 __thiscall
FUN_00482f70(int receiver_bits,int stack_4_bits,float *stack_8_bits,undefined4 stack_c_bits)

{
  int iVar1;
  float *pfVar2;
  int iVar3;
  uint uVar4;
  
  uVar4 = 0;
  if (*(int *)(receiver_bits + 0x18) != 0) {
    iVar3 = 0;
    do {
      iVar1 = iVar3 + *(int *)(receiver_bits + 0x40);
      if (*(char *)(iVar3 + 0x34 + *(int *)(receiver_bits + 0x40)) != '\0') {
        if ((_DAT_005b47d8 < *(float *)(iVar1 + 4)) && (_DAT_005b47d8 < *(float *)(iVar1 + 4))) {
          *(float *)(iVar1 + 4) = *(float *)(iVar1 + 4) - _DAT_005b2764;
        }
        pfVar2 = (float *)(iVar3 + 4 + *(int *)(receiver_bits + 0x40));
        if (*(float *)(iVar3 + 4 + *(int *)(receiver_bits + 0x40)) <= _DAT_005b47d8) {
          *pfVar2 = *pfVar2 + _DAT_005b2764;
        }
      }
      uVar4 = uVar4 + 1;
      iVar3 = iVar3 + 0x38;
    } while (uVar4 < *(uint *)(receiver_bits + 0x18));
  }
  uVar4 = 0;
  if (*(int *)(receiver_bits + 0x18) != 0) {
    iVar3 = 0;
    do {
      iVar1 = iVar3 + *(int *)(receiver_bits + 0x40);
      if ((((*(float *)(iVar3 + *(int *)(receiver_bits + 0x40)) == *stack_8_bits) &&
           (*(float *)(iVar1 + 8) == stack_8_bits[2])) && (*(int *)(iVar1 + 0x30) == stack_4_bits))
         && (((*(char *)(iVar1 + 0x34) != '\0' && (_DAT_005b47d8 < *(float *)(iVar1 + 4))) &&
             (_DAT_005b47d8 < *(float *)(iVar1 + 4))))) {
        *(float *)(iVar1 + 4) = *(float *)(iVar1 + 4) - _DAT_005b2764;
      }
      uVar4 = uVar4 + 1;
      iVar3 = iVar3 + 0x38;
    } while (uVar4 < *(uint *)(receiver_bits + 0x18));
    return 0;
  }
  return 0;
}

