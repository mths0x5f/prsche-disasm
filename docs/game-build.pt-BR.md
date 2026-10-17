# Compilação Original do Jogo

## Fatos Verificados

- Fonte: diretório instalado indicado pelo usuário. Apenas lemos dele.
- `local/game` — cópia de origem verificada; 1742 arquivos, 599 126 359 bytes.
- Lista completa, tamanhos e SHA-256: [game-manifest.json](game-manifest.json).
- `version.txt` contém `3.5`.
- `nfs5.exe`: FileVersion `2019.06.21.027`, descrição `Need For Speed: Porsche Unleashed Patch`.
- `dinput.dll`: Ultimate ASI Loader; `SilentPatchNFS90s.asi`: versão `1.0.1.0`.
- nfs5.ini especifica `ThrashDriver=opengl1`, `Language=english`.
- Principais EXE/DLL — PE32 x86; inventário de importações: [pe-inventory.json](pe-inventory.json).
- `GameData/CarModel/356a.crp`, `.tpg`, `.clr`, `356aD.fsh`, `356aL.fsh` estão disponíveis.

## Reprodução

```powershell
py scripts/prepare-game.py --source 'C:\Program Files (x86)\by Decepticon\Need for Speed - Porsche Unleashed'
py scripts/inventory-pe.py
```

O prepare-game recusa-se a sobrescrever uma cópia existente. O manifesto reflete
o estado dos arquivos no momento da cópia. A composição da instalação pode mudar se ela
for executada separadamente pelo usuário; isso não altera o exemplar já salvo.

## Não Determinado

A ausência de modificações nos recursos do jogo não foi comprovada. O número 3.5 não identifica
todos os patches. A lista de importações estáticas não é igual à lista de DLLs realmente carregadas;
módulos dinâmicos são registrados separadamente na inicialização da cópia experimental.
