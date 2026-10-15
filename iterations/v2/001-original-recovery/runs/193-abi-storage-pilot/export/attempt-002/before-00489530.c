
void __thiscall FUN_00489530(int *param_1,int param_2)

{
  float fVar1;
  float fVar2;
  float fVar3;
  int iVar4;
  undefined *puVar5;
  float *pfVar6;
  undefined4 *puVar7;
  int iVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  uint uVar11;
  undefined4 *puVar12;
  undefined4 extraout_ECX;
  int iVar13;
  int unaff_EBX;
  int unaff_EBP;
  undefined4 unaff_retaddr;
  undefined1 *puVar14;
  undefined4 uVar15;
  int **ppiVar16;
  int *piStack_148;
  undefined4 uStack_144;
  undefined1 *puStack_140;
  undefined1 *puStack_13c;
  int local_128;
  undefined1 auStack_120 [8];
  uint local_118;
  undefined1 local_111;
  undefined1 local_110 [8];
  int aiStack_108 [2];
  undefined1 local_100 [120];
  undefined1 auStack_88 [136];
  
  if (*(char *)((int)param_1 + 5) == '\0') {
    puStack_13c = &local_111;
    local_118 = *(uint *)(param_1[7] + param_2 * 8) & 0x4187fe;
    puStack_140 = (undefined1 *)0x4896f7;
    FUN_00505810();
    puStack_13c = local_100;
    puStack_140 = (undefined1 *)param_2;
    uStack_144 = (undefined1 *)0x489704;
    (**(code **)(*param_1 + 8))();
    uStack_144 = auStack_88;
    piStack_148 = aiStack_108;
    uVar10 = FUN_005a0480(8);
    uStack_144 = &stack0xfffffed0;
    puVar14 = auStack_88;
    piStack_148 = (int *)0x0;
    uVar15 = 1;
    uVar9 = FUN_0047bdc0(8,aiStack_108);
    FUN_00489930(param_2,unaff_retaddr,uVar9,uVar10,puVar14,uVar15);
    puVar5 = PTR_PTR_005e4fe8;
    for (iVar13 = unaff_EBP; PTR_PTR_005e4fe8 = puVar5, iVar13 != unaff_EBX; iVar13 = iVar13 + 4) {
      uStack_144 = (undefined1 *)param_2;
      piStack_148 = param_1;
      puVar7 = (undefined4 *)FUN_00489830();
      piStack_148 = (int *)*puVar7;
      ppiVar16 = &piStack_148;
      uStack_144 = (undefined1 *)CONCAT31(uStack_144._1_3_,*(undefined1 *)(puVar7 + 1));
      uStack_144 = (undefined1 *)CONCAT22(*(undefined2 *)((int)puVar7 + 6),(undefined2)uStack_144);
      FUN_0050e140(auStack_120);
      FUN_00489850(ppiVar16);
      puVar5 = PTR_PTR_005e4fe8;
    }
    iVar13 = local_128 - unaff_EBP >> 2;
    if (iVar13 == 0) {
      return;
    }
    uVar11 = iVar13 * 4;
    if (uVar11 < 0x101) {
      uStack_144 = *(undefined1 **)(puVar5 + 0x28);
      piStack_148 = (int *)0x4897dd;
      FUN_005322b0();
      uVar11 = uVar11 - 1 >> 3;
      *(undefined4 *)(unaff_EBP + 4) = *(undefined4 *)(puVar5 + uVar11 * 4 + 0x34);
      *(int *)(puVar5 + uVar11 * 4 + 0x34) = unaff_EBP;
      piStack_148 = *(int **)(puVar5 + 0x28);
      FUN_005322c0();
      return;
    }
    piStack_148 = (int *)0x4897c5;
    FUN_0059ecd0();
    return;
  }
  puStack_140 = local_110;
  puStack_13c = (undefined1 *)param_2;
  uStack_144 = (undefined1 *)0x48955b;
  pfVar6 = (float *)(**(code **)(*param_1 + 0xc))();
  fVar1 = *pfVar6;
  fVar2 = pfVar6[1];
  fVar3 = pfVar6[2];
  iVar13 = param_1[8];
  if (iVar13 == 0) {
    iVar13 = param_1[6];
    uStack_144 = (undefined1 *)(iVar13 << 4);
    piStack_148 = (int *)0x48958b;
    puVar7 = (undefined4 *)FUN_0059eff0();
    if (puVar7 == (undefined4 *)0x0) {
      puVar7 = (undefined4 *)0x0;
    }
    else {
      puVar12 = puVar7;
      if (-1 < iVar13 + -1) {
        do {
          *puVar12 = 0;
          iVar13 = iVar13 + -1;
          puVar12 = puVar12 + 4;
        } while (iVar13 != 0);
        param_1[8] = (int)puVar7;
        goto LAB_004895eb;
      }
    }
    param_1[8] = (int)puVar7;
  }
  else {
    iVar4 = param_2 * 0x10 + iVar13;
    if (((*(float *)(param_2 * 0x10 + 4 + iVar13) == fVar1) && (*(float *)(iVar4 + 8) == fVar2)) &&
       (*(float *)(iVar4 + 0xc) == fVar3)) {
      return;
    }
  }
LAB_004895eb:
  uStack_144 = &stack0xfffffed0;
  piStack_148 = (int *)0x4895fe;
  iVar13 = FUN_0047bc20();
  if (iVar13 == 0) {
    uStack_144 = &stack0xfffffed0;
    piStack_148 = (int *)0x489610;
    iVar13 = FUN_0047bc20();
  }
  iVar8 = param_2 * 0x10;
  iVar4 = *(int *)(param_1[8] + iVar8);
  *(int *)(param_1[8] + iVar8) = iVar13;
  pfVar6 = (float *)(param_1[8] + 4 + iVar8);
  *pfVar6 = fVar1;
  pfVar6[1] = fVar2;
  pfVar6[2] = fVar3;
  if (iVar4 != iVar13) {
    uStack_144 = (undefined1 *)param_2;
    piStack_148 = param_1;
    puVar7 = (undefined4 *)FUN_00489830();
    piStack_148 = (int *)*puVar7;
    uStack_144 = (undefined1 *)CONCAT31(uStack_144._1_3_,*(undefined1 *)(puVar7 + 1));
    uStack_144 = (undefined1 *)CONCAT22(*(undefined2 *)((int)puVar7 + 6),(undefined2)uStack_144);
    uVar9 = FUN_00489810(auStack_120,param_2);
    uVar10 = extraout_ECX;
    FUN_0050e140(uVar9);
    FUN_00489850(uVar10);
    if (iVar4 != 0) {
      uStack_144 = (undefined1 *)param_2;
      piStack_148 = param_1;
      puVar7 = (undefined4 *)FUN_00489830();
      piStack_148 = (int *)*puVar7;
      uStack_144 = (undefined1 *)CONCAT31(uStack_144._1_3_,*(undefined1 *)(puVar7 + 1));
      uStack_144 = (undefined1 *)CONCAT22(*(undefined2 *)((int)puVar7 + 6),(undefined2)uStack_144);
      uStack_144 = (undefined1 *)FUN_0047c570();
      piStack_148 = (int *)0x4896bd;
      FUN_0047c6f0();
      return;
    }
  }
  return;
}

