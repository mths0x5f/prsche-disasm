# Run 430 — o Porsche.exe inteiro rebaixado para C++ num único EXE

Branch pessoal `feat/lowered-whole-game`. Objetivo: o caminho rápido "rebaixar tudo,
fechar a build, humanizar depois". Todas as funções do catálogo passam pelo
`x86-cpp-backend-fpu.py` e são linkadas num EXE que as executa sobre a imagem original.

Isto **não** é recuperação nem prova de semântica. É uma base executável. Depois, cada
função rebaixada é trocada, uma a uma, por uma versão humanizada, com comparação
diferencial contra a rebaixada ou contra o original.

## Como funciona

- `scripts/research/build-v2-lowered-exe-430.py` gera o C++ em
  `local/experiments/v2-lowered-exe-430/gen` (fora do repositório) e compila
  `PorscheLowered.exe`. A build é incremental: só recompila TUs alterados.
- Regras de rebaixamento somadas às do backend:
  - operandos `fs:` somam a base do TEB, pois o backend congelado tratava `fs` como plano;
  - um `jmp` indireto por tabela vira `switch` sobre os alvos da tabela, lidos do PE;
  - funções com vários intervalos têm um corpo por intervalo;
  - todo alvo direto de `jmp`/`jcc`/`call` vindo de fora do intervalo vira uma entrada no
    meio do corpo (`switch(s.pc)` no início). Exemplo: `strcpy` `005aa4e0` salta para dentro
    de `strcat`;
  - cair no fim de um intervalo continua no endereço seguinte (despacho de cauda);
  - o DF é modelado na única sequência `std; repne scasb; cld` (`005a2885`).
- Aproximações aceitas nesta branch (a upstream as recusa):
  - `fsqrt` usa `sqrt` em binary64;
  - `fld`/`fstp` de 80 bits convertem de/para double;
  - prefetch vira no-op;
  - 3DNow!, `fnsave`/`frstor`/`fnstenv`/`fldenv` e `rcpss` param o processo com erro fatal
    se forem executados. O resto do corpo continua rebaixado (em CPU sem 3DNow! esses
    caminhos não deveriam rodar).
- `runtime_430.cpp`:
  - o próprio EXE tem base `0x00400000`. O `reserve_430.asm` (seção `.text$a`, a primeira
    da imagem) reserva `0x00401000..0x006e3000`, e na partida o runtime copia por cima as
    seções do `Porsche.exe` original. Sem isso, a pilha, os heaps e os arquivos mapeados
    ocupam essa faixa antes do `main`. O cabeçalho do host fica; só o diretório de recursos
    passa a apontar para o `.rsrc` original;
  - o código original vira dados (RW, sem execução), porque as tabelas de salto são lidas
    de lá;
  - o código rebaixado roda na pilha real da thread e o runtime numa pilha lateral, para
    que os limites de pilha do TEB e a cadeia `fs:[0]` continuem sendo os do jogo;
  - uma chamada para fora da imagem vira chamada nativa feita na pilha do jogo (ponte de ida);
  - quando código nativo entra na imagem (WndProc, threads, callbacks), a falha de DEP é
    capturada por um VEH e desviada para o corpo rebaixado (ponte de volta);
  - shims: `GetModuleHandleA(NULL)` → `0x00400000`, `GetModuleFileNameA` → caminho do original.

## Limites conhecidos

- O x87 é modelado em binary64, não em 80 bits.
- Valores float devolvidos por funções nativas em `st0` não são transferidos.
- Não há suporte a desenrolar SEH nem a `longjmp` que atravesse a recursão do host.
- Os helpers `rep movs/stos` ignoram o DF (no binário só aparece o `std` acima).

## Resultado

Ver `summary.json`.
