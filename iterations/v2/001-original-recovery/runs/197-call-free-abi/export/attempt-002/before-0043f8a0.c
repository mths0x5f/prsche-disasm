
void __thiscall FUN_0043f8a0(int *param_1,int *param_2)

{
  int iVar1;
  int iVar2;
  
  iVar1 = *param_1;
  iVar2 = *(int *)(iVar1 + 0xc);
  if (iVar2 == 0) {
    iVar2 = *(int *)(iVar1 + 4);
    if (iVar1 == *(int *)(iVar2 + 0xc)) {
      do {
        *param_1 = iVar2;
        iVar2 = *(int *)(iVar2 + 4);
      } while (*param_1 == *(int *)(iVar2 + 0xc));
    }
    if (*(int *)(*param_1 + 0xc) != iVar2) {
      *param_1 = iVar2;
    }
  }
  else {
    *param_1 = iVar2;
    if (*(int *)(iVar2 + 8) != 0) {
      do {
        iVar2 = *(int *)(*param_1 + 8);
        *param_1 = iVar2;
      } while (*(int *)(iVar2 + 8) != 0);
      *param_2 = iVar1;
      return;
    }
  }
  *param_2 = iVar1;
  return;
}

