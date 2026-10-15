
void __thiscall FUN_00489370(int param_1,undefined4 param_2)

{
  uint uVar1;
  
  uVar1 = 0;
  if (*(int *)(param_1 + 0x18) != 0) {
    do {
      FUN_00489530(uVar1,param_2);
      uVar1 = uVar1 + 1;
    } while (uVar1 < *(uint *)(param_1 + 0x18));
  }
  return;
}

