# Run 430 — o Porsche.exe inteiro rebaixado para C++ num único EXE

Branch pessoal `feat/lowered-whole-game`. Objetivo: o caminho rápido "rebaixar tudo,
fechar a build, humanizar depois". Todas as funções do catálogo passam pelo
`x86-cpp-backend-fpu.py` e são linkadas num EXE que as executa sobre a imagem original.

Isto **não** é recuperação nem prova de semântica. É uma base executável. Depois, cada
função rebaixada é trocada, uma a uma, por uma versão humanizada, com comparação
diferencial contra a rebaixada ou contra o original.

## Como funciona

- `scripts/research/build-v2-lowered-exe-430.py` gera o C++ em
  `D:\projetos\porsche-src` (fora do repositório; muda com `PORSCHE430_GEN`) e compila
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

## Resultado (2026-10-19)

- Todas as 5.772 funções do catálogo foram rebaixadas. Somam-se 2.694 pedaços sintéticos
  achados por relocação; 216 deles são dados e foram descartados. No total são 8.250 corpos,
  9.343 entradas e ~435 mil instruções. Compilação e link sem erros; `PorscheLowered.exe`
  tem ~19 MB.
- Primeira execução, a partir de uma cópia do jogo em `local/run-430` (`local/game` é só
  leitura): o EXE rebaixado passa pela CRT e pelo WinMain, lê o registro e mostra
  **a mesma** MessageBox do original: "Error:" / "Run 3D Setup before running the game.". As
  duas ficam no laço de mensagens, com ~40 mil chamadas nativas em 25 s. A chave
  `HKCU|HKLM\Software\Electronic Arts\Need for Speed - Porsche Unleashed` não existe nesta
  máquina; quem a grava é o `config.exe` (3D Setup).

### Atualização: menu principal

- O `config.exe` do repack é do nGlide, não do jogo. O setup do jogo é o `3DSetup.exe`. O
  repack guarda os drivers do Thrash em subpastas (`drivers\dx7\dx7z.dll`); na cópia
  `local/run-430` o `dx7z.dll` e o `thrash.ini` foram copiados para `drivers\`.
- O EXE é linkado com `/SUBSYSTEM:CONSOLE,5.01 /MANIFEST:NO`, como um executável de 2000.
  Mesmo assim, o `RegOpenKeyExA(HKLM\SOFTWARE\Electronic Arts\..., KEY_ALL_ACCESS)` ainda
  devolve 5 (acesso negado) no rebaixado. O jogo segue com os valores já gravados.
- O original e o rebaixado chegam ao **mesmo menu principal**. O rebaixado é mais lento:
  aos 12 s ainda está em "LOADING".
- Ferramentas do runtime:
  - `PORSCHE430_TRACE=<n>` e `PORSCHE430_TRACE_FILTER=a;b;c` registram chamadas de import
    (nome, endereço de retorno, 4 argumentos, retorno), uma linha por chamada;
  - `PORSCHE430_NATIVE=1` roda o código **original** na mesma imagem e no mesmo host, com
    a IAT passando por trampolins de log. É a referência para comparar linha a linha;
  - `PORSCHE430_WATCHDOG=1` mostra o `pc` a cada 3 s.
- Comparação de `LoadLibrary`/`GetProcAddress` entre o modo nativo e o rebaixado: as
  43 primeiras chamadas são idênticas (nome, origem, argumentos). Na 43ª,
  `gimme.dll!ConvertFile`, o original no host às vezes cai dentro do `gimme.dll`, e o
  rebaixado também caiu uma vez no mesmo lugar. Como acontece nos dois modos, é ambiente
  (layout de memória do host), não rebaixamento.

### Atualização: desempenho (2026-10-20)

Medido com a cópia `local/run-430`, onde o `gimme.dll` foi renomeado para `gimme.dll.bak`
(a correção clássica da era XP: o jogo pula a conversão do retrato, e o `ConvertFile` deixa
de cair de forma intermitente).

| Medida | Original (modo nativo) | Rebaixado antes | Rebaixado agora |
|---|---|---|---|
| Até o menu (`LoadLibrary("gimme.dll")`) | ~11–12 s | 15,3 s | ~13 s |
| CPU no menu (20–30 s, % de um núcleo) | 42% | 71–82% | 45% |

O que mudou:
- **Inline e flags.** Os helpers da máquina são `__forceinline` e compilados com `/O2`; com
  `/O1` eles não entravam inline e custavam ~37% do tempo. `div`/`idiv` usam 32 bits quando
  EDX só estende EAX, sem chamar a divisão de 64 bits da CRT.
- **Flags mortos.** Uma escrita de flags sobrescrita por outra escrita completa
  (`add/sub/cmp/test/and/or/xor/neg`) antes de qualquer leitura vira uma forma `nf`, que só
  calcula o valor. São 31.720 instruções. Só atravessa instruções que comprovadamente não
  tocam em EFLAGS.
- **Callbacks sem exceção.** O Thrash (`dx7z.dll`) chama o callback de estado `00575a20`
  ~20 mil vezes por segundo. Cada chamada era uma falha de DEP tratada pelo VEH, ~16% da
  thread principal no menu. Agora, nas APIs conhecidas que recebem callback
  (`_THRASH_setstate@8`, arg. 2; `timeSetEvent`, arg. 3), o ponteiro é trocado por um stub
  executável `push va; jmp reverse_asm`.
- **Nomes de import.** A busca virou uma tabela hash, e o resultado do filtro de trace
  fica em cache.
- **Ferramentas.** `PORSCHE430_PROFILE=<s>` (com `PORSCHE430_PROFILE_DELAY` e
  `PORSCHE430_PROFILE_OUT`) amostra o EIP da thread principal a 1 kHz e conta as entradas
  da ponte de volta. Para simbolizar:
  `py -3 scripts/research/profile-v2-lowered-exe-430.py <arquivo>`.
- **Equivalência mantida.** Com o filtro
  `LoadLibrary;GetProcAddress;CreateFileA;RegOpen;RegQuery;FindFirst`, as 1.796 primeiras
  chamadas são idênticas às do original no modo nativo; só os handles diferem.
- **Calibração de CPU.** `005560b0` conta quantas `idiv` cabem num intervalo fixo do
  relógio `[006b7c7c]` e domina a partida (24%). Ela dura o mesmo tempo nas duas versões,
  mas o rebaixado faz menos iterações. Falta verificar se o jogo usa o resultado para
  escolher detalhes.

### Atualização: estrutura de pastas do código original (2026-10-20)

O C++ rebaixado agora sai em `D:\projetos\porsche-src\src\` com a árvore de fontes do próprio jogo (opção B). O
binário traz 48 caminhos de arquivos-fonte (`__FILE__` de asserts e mensagens), por exemplo:
- `\real\pc\startup.c`, `\real\pc\nfile.c`;
- `\real\patch3\pc\input.c`, `\real\cmn\stream.c`;
- `d:\Nfs\Nfs5\Frontend\common\Src\FEIntro.cpp`;
- `d:\Nfs\Nfs5\game\Common\Render\RCustomLayers.cpp`;
- `d:\Nfs\Support\Utility\UMemory.cpp`.

`scripts/research/attribute-v2-source-files-430.py` atribui as funções com níveis de
evidência:

| Evidência | Funções | Regra |
|---|---|---|
| `path` | 79 | a função cita o caminho de um `.c`/`.cpp` (um `.h` só indica código inlinado) |
| `between` | 38 | fica no `.text` entre duas funções `path` do mesmo arquivo, sem outro arquivo no meio |
| `class-file` | 12 | todos os nomes RTTI da função são da mesma classe ou namespace, e ele coincide com o nome de um arquivo conhecido (`RCustomLayers::*` → `RCustomLayers.cpp`) |
| `class` | 1.752 | só a classe RTTI é conhecida; o arquivo não |

Nomes de função:
- **RTTI** (366 classes, 360 vtables):
  - `Classe__Sub__virtual_NN_<va>` para métodos virtuais, `NN` sendo a posição na vtable;
  - `Classe__ctor_or_dtor_<va>` para funções que gravam o ponteiro da vtable no objeto.
  O binário não guarda o nome do método, só da classe.
- `shared_<va>`: corpo fundido pelo linker (ICF) e usado por várias classes, como
  `xor eax,eax; ret`.
- `FUN_<va>` (catálogo) e `PTR_<va>` (código achado só por ponteiro) para o resto.

Layout:
- arquivo conhecido → caminho original, sem drive e com extensão `.cpp`
  (`real/pc/nfile.cpp`, `Nfs/Nfs5/game/Common/Render/RCustomLayers.cpp`);
- só classe → `_sem_arquivo/classes/<Classe>.cpp`;
- compartilhadas → `_sem_arquivo/classes/_compartilhadas.cpp`;
- resto → `_sem_arquivo/codigo/<va inicial>_<va final>.cpp`, em blocos contíguos do `.text`.

Cada arquivo diz na primeira linha de onde veio, e `attribution.json` guarda a evidência de
cada função. Ao todo são 442 arquivos.

#### Evidência do `gimme.dll`

O `gimme.dll` (ferramenta "FaceInRace", SHA `3a43b0f6…`, igual no repack e na instalação
completa) foi linkado com buffers que sobraram de **arquivos-objeto do NFS5 com debug
CodeView**. A extração é feita por `scripts/research/extract-v2-gimme-debug-430.py`; a saída
completa fica em `gimme-evidence.json` (local) e o resumo em `gimme-evidence-summary.json`.
- **10 objetos**, com o nome que o compilador gravou:
  - Release: `WMap.obj`, `WFarGroundBundle.obj`, `RShadowManager.obj`, `FEdaCar.obj`,
    `FECarListTypes.obj`;
  - Debug: `FEdaChronicle.obj`, `FEChroniclePictureControl.obj`, `FEdaDisplay.obj`,
    `WWorldHandle.obj`, `WAnimatableHandle.obj`.
- **133 caminhos reais** em `D:\dev\NFS5\...`, `D:\dev\library\...` e `D:\dev\support\...`,
  sendo 12 `.cpp` e 121 headers.
- **62 funções nomeadas** com parâmetros e locais (todas dos objetos Debug), **3.046 nomes
  de tipo** e 56 corpos de função.

Uso na atribuição:
- **`gimme-bytes`.** Corpos casados com o `Porsche.exe` de forma única, com os dwords
  relocados mascarados: `WMap::Find` em `0047bad0` e `0047bc20`, ambos em `WMap.cpp`.
- **`gimme-vtable`.** O slot k da vtable embutida dá nome ao slot k da mesma classe, ou de
  suas derivadas (hierarquia RTTI), no jogo. Só vale se os bytes que o nome decorado diz que
  o método `__thiscall` remove da pilha forem iguais a todo `ret N` da função. Passaram
  `WArticleBundle::SubReLoad` (`00477d10`) e `FEdaCar::Initialize` (`004f1ea0`). As classes
  `W*Bundle` têm 11 slots no jogo contra 10 no gimme (a interface mudou entre as builds),
  então os demais slots foram rejeitados pela checagem.
- **`class-file`.** Os `.cpp` reais do gimme entram como âncoras; 29 funções no total, entre
  elas as de `FEdaCar.cpp`, `FEdaChronicle.cpp` e `FECarSetupCallbackList.cpp`.
- **Raiz única.** O jogo foi compilado em `d:\Nfs\` e o gimme em `D:\dev\`. A árvore
  unifica as duas em `Nfs5/...`, `Support/...` e `real/...`.

Limites:
- só ~2% das funções têm arquivo de origem comprovado;
- a fronteira entre arquivos sem âncora não é conhecida e não é inventada.

## Próximos passos

1. Verificar o uso do resultado da calibração de CPU (`005560b0`) e medir a corrida
2. Ir além do menu (corrida) comparando traces nativo × rebaixado e corrigindo cada
   divergência ou parada fatal (`[430] ...` no stderr).
3. Investigar o crash do `gimme.dll!ConvertFile` no host (provável dependência de layout
   de heap ou pilha).
4. Com o jogo rodando, começar a humanizar: trocar `translated_XXXXXXXX` por funções
   legíveis, uma por vez, comparando estado/memória com a versão rebaixada (os 482 corpos
   já recuperados na main entram primeiro).

Comandos:

```
py -3 scripts/research/build-v2-lowered-exe-430.py          # gera + compila (incremental)
cd local/run-430 && ../experiments/v2-lowered-exe-430/PorscheLowered.exe Porsche.exe
```
