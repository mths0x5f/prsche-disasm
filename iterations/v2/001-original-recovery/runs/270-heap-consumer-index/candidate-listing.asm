; CANDIDATE 005697d0 navigation only, no function entry accepted
005697d0  6a40  PUSH 0x40
005697d2  6a00  PUSH 0
005697d4  68204f6b00  PUSH 0x6b4f20
005697d9  e8b22afdff  CALL 0x53c290
005697de  83c40c  ADD esp, 0xc
005697e1  b801000000  MOV eax, 1
005697e6  c3  RET 

; CANDIDATE 00569a40 navigation only, no function entry accepted
00569a40  8b442404  MOV eax, dword ptr [esp + 4]
00569a44  56  PUSH esi
00569a45  83e00f  AND eax, 0xf
00569a48  8b0c85204f6b00  MOV ecx, dword ptr [eax*4 + 0x6b4f20]
00569a4f  8b7108  MOV esi, dword ptr [ecx + 8]
00569a52  85f6  TEST esi, esi
00569a54  7413  JE 0x569a69
00569a56  8d5610  LEA edx, [esi + 0x10]
00569a59  52  PUSH edx
00569a5a  e83185fcff  CALL 0x531f90
00569a5f  8b7608  MOV esi, dword ptr [esi + 8]
00569a62  83c404  ADD esp, 4
00569a65  85f6  TEST esi, esi
00569a67  75ed  JNE 0x569a56
00569a69  5e  POP esi
00569a6a  c3  RET 

; CANDIDATE 00569b10 navigation only, no function entry accepted
00569b10  8b0d60eb5d00  MOV ecx, dword ptr [0x5deb60]
00569b16  33c0  XOR eax, eax
00569b18  83e10f  AND ecx, 0xf
00569b1b  8b148d204f6b00  MOV edx, dword ptr [ecx*4 + 0x6b4f20]
00569b22  8b4a20  MOV ecx, dword ptr [edx + 0x20]
00569b25  6681395342  CMP word ptr [ecx], 0x4253
00569b2a  740f  JE 0x569b3b
00569b2c  8b5104  MOV edx, dword ptr [ecx + 4]
00569b2f  8b4910  MOV ecx, dword ptr [ecx + 0x10]
00569b32  03c2  ADD eax, edx
00569b34  6681395342  CMP word ptr [ecx], 0x4253
00569b39  75f1  JNE 0x569b2c
00569b3b  c3  RET 

; CANDIDATE 0056a1f0 navigation only, no function entry accepted
0056a1f0  81ec20030000  SUB esp, 0x320
0056a1f6  b8204b6b00  MOV eax, 0x6b4b20
0056a1fb  8d4c2421  LEA ecx, [esp + 0x21]
0056a1ff  53  PUSH ebx
0056a200  55  PUSH ebp
0056a201  56  PUSH esi
0056a202  57  PUSH edi
0056a203  8b30  MOV esi, dword ptr [eax]
0056a205  83c004  ADD eax, 4
0056a208  8bd6  MOV edx, esi
0056a20a  83c103  ADD ecx, 3
0056a20d  c1ea10  SHR edx, 0x10
0056a210  8851fc  MOV byte ptr [ecx - 4], dl
0056a213  8bd6  MOV edx, esi
0056a215  c1ea08  SHR edx, 8
0056a218  8851fd  MOV byte ptr [ecx - 3], dl
0056a21b  8a50fc  MOV dl, byte ptr [eax - 4]
0056a21e  8851fe  MOV byte ptr [ecx - 2], dl
0056a221  3d204f6b00  CMP eax, 0x6b4f20
0056a226  7cdb  JL 0x56a203
0056a228  33f6  XOR esi, esi
0056a22a  8d6c2431  LEA ebp, [esp + 0x31]
0056a22e  89742410  MOV dword ptr [esp + 0x10], esi
0056a232  896c2418  MOV dword ptr [esp + 0x18], ebp
0056a236  33c0  XOR eax, eax
0056a238  33c9  XOR ecx, ecx
0056a23a  8a45ff  MOV al, byte ptr [ebp - 1]
0056a23d  8a4d00  MOV cl, byte ptr [ebp]
0056a240  89442424  MOV dword ptr [esp + 0x24], eax
0056a244  8b842434030000  MOV eax, dword ptr [esp + 0x334]
0056a24b  33d2  XOR edx, edx
0056a24d  894c241c  MOV dword ptr [esp + 0x1c], ecx
0056a251  8a5501  MOV dl, byte ptr [ebp + 1]
0056a254  33c9  XOR ecx, ecx
0056a256  89542420  MOV dword ptr [esp + 0x20], edx
0056a25a  894c2414  MOV dword ptr [esp + 0x14], ecx
0056a25e  8d5803  LEA ebx, [eax + 3]
0056a261  33d2  XOR edx, edx
0056a263  8a13  MOV dl, byte ptr [ebx]
0056a265  8bfa  MOV edi, edx
0056a267  85ff  TEST edi, edi
0056a269  7507  JNE 0x56a272
0056a26b  8bc6  MOV eax, esi
0056a26d  e9c9000000  JMP 0x56a33b
0056a272  b9ff000000  MOV ecx, 0xff
0056a277  33c0  XOR eax, eax
0056a279  8a43ff  MOV al, byte ptr [ebx - 1]
0056a27c  2bcf  SUB ecx, edi
0056a27e  8bf1  MOV esi, ecx
0056a280  8be8  MOV ebp, eax
0056a282  0faf742424  IMUL esi, dword ptr [esp + 0x24]
0056a287  33c0  XOR eax, eax
0056a289  33d2  XOR edx, edx
0056a28b  8a43fd  MOV al, byte ptr [ebx - 3]
0056a28e  8a53fe  MOV dl, byte ptr [ebx - 2]
0056a291  89442428  MOV dword ptr [esp + 0x28], eax
0056a295  b881808080  MOV eax, 0x80808081
0056a29a  8954242c  MOV dword ptr [esp + 0x2c], edx
0056a29e  f7ee  IMUL esi
0056a2a0  03d6  ADD edx, esi
0056a2a2  c1fa07  SAR edx, 7
0056a2a5  8bc2  MOV eax, edx
0056a2a7  c1e81f  SHR eax, 0x1f
0056a2aa  03d0  ADD edx, eax
0056a2ac  8d042a  LEA eax, [edx + ebp]
0056a2af  bdff000000  MOV ebp, 0xff
0056a2b4  3dff000000  CMP eax, 0xff
0056a2b9  7f02  JG 0x56a2bd
0056a2bb  8be8  MOV ebp, eax
0056a2bd  8bf1  MOV esi, ecx
0056a2bf  b881808080  MOV eax, 0x80808081
0056a2c4  0faf74241c  IMUL esi, dword ptr [esp + 0x1c]
0056a2c9  f7ee  IMUL esi
0056a2cb  03d6  ADD edx, esi
0056a2cd  beff000000  MOV esi, 0xff
0056a2d2  c1fa07  SAR edx, 7
0056a2d5  8bc2  MOV eax, edx
0056a2d7  c1e81f  SHR eax, 0x1f
0056a2da  03d0  ADD edx, eax
0056a2dc  8b44242c  MOV eax, dword ptr [esp + 0x2c]
0056a2e0  03d0  ADD edx, eax
0056a2e2  81faff000000  CMP edx, 0xff
0056a2e8  7f02  JG 0x56a2ec
0056a2ea  8bf2  MOV esi, edx
0056a2ec  0faf4c2420  IMUL ecx, dword ptr [esp + 0x20]
0056a2f1  b881808080  MOV eax, 0x80808081
0056a2f6  f7e9  IMUL ecx
0056a2f8  03d1  ADD edx, ecx
0056a2fa  8b442428  MOV eax, dword ptr [esp + 0x28]
0056a2fe  c1fa07  SAR edx, 7
0056a301  8bca  MOV ecx, edx
0056a303  c1e91f  SHR ecx, 0x1f
0056a306  03d1  ADD edx, ecx
0056a308  03d0  ADD edx, eax
0056a30a  81faff000000  CMP edx, 0xff
0056a310  7e05  JLE 0x56a317
0056a312  baff000000  MOV edx, 0xff
0056a317  c1e708  SHL edi, 8
0056a31a  0bfd  OR edi, ebp
0056a31c  c1e708  SHL edi, 8
0056a31f  0bfe  OR edi, esi
0056a321  c1e708  SHL edi, 8
0056a324  0bfa  OR edi, edx
0056a326  57  PUSH edi
0056a327  e8a4dbfcff  CALL 0x537ed0
0056a32c  8b742414  MOV esi, dword ptr [esp + 0x14]
0056a330  8b4c2418  MOV ecx, dword ptr [esp + 0x18]
0056a334  8b6c241c  MOV ebp, dword ptr [esp + 0x1c]
0056a338  83c404  ADD esp, 4
0056a33b  8bbc2438030000  MOV edi, dword ptr [esp + 0x338]
0056a342  8bd1  MOV edx, ecx
0056a344  c1e208  SHL edx, 8
0056a347  0bd6  OR edx, esi
0056a349  41  INC ecx
0056a34a  83c304  ADD ebx, 4
0056a34d  83f910  CMP ecx, 0x10
0056a350  88043a  MOV byte ptr [edx + edi], al
0056a353  894c2414  MOV dword ptr [esp + 0x14], ecx
0056a357  0f8c04ffffff  JL 0x56a261
0056a35d  46  INC esi
0056a35e  83c503  ADD ebp, 3
0056a361  81fe00010000  CMP esi, 0x100
0056a367  89742410  MOV dword ptr [esp + 0x10], esi
0056a36b  896c2418  MOV dword ptr [esp + 0x18], ebp
0056a36f  0f8cc1feffff  JL 0x56a236
0056a375  5f  POP edi
0056a376  5e  POP esi
0056a377  5d  POP ebp
0056a378  5b  POP ebx
0056a379  81c420030000  ADD esp, 0x320
0056a37f  c3  RET 
