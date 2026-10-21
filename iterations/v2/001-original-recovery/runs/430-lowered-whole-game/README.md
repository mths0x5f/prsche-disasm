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

#### Precedência de nomes

O nome que a própria EA escreveu é a verdade final. Isso vale para os objetos de debug do
`gimme.dll` (`gimme-bytes`, `gimme-vtable`) e para o prefixo da mensagem da própria função
(`self-message`); nenhuma outra fonte o substitui. Abaixo deles vêm os nomes das recuperações
manuais aceitas (`recovered`), que viram `aliases` quando encontram um nome da EA. Por último
vem a linhagem do NFS4 (`nfs4-strings`), que só nomeia funções ainda sem nome. A regra está em
`EA_EVIDENCE` no script de atribuição; ao ser explicitada, em 2026-10-21, nenhum nome mudou.

#### Nomes das recuperações aceitas (`recovered`)

É a evidência de nome mais forte. As funções que o projeto já recuperou à mão, aceitas no grafo
do jogo e verificadas diferencialmente contra o original, emprestam o nome à árvore rebaixada
(`fe_input_getstate_00532e10`, `audio_channel_stop_00565d60`,
`application_main_function_00413ea0`…).
- **Fontes:** os grafos `429-unified-game-integration/build-004.json` (nosso, unificado),
  `332-resource-chain-game-integration/build-001.json` (upstream, Runs 325–333),
  `346-diagnostic-leaves/build-001.json` (upstream, Runs 334–346) e
  `324-input-modes-game-integration/build-001.json` (upstream, PR22 aceito).
- **O que conta:** só definições com corpo (`nome_XXXXXXXX(...) {`), num endereço catalogado.
  Os adaptadores `*_links.cpp` / `*bridge*` ficam de fora: eles só dão um apelido do
  consumidor ao mesmo endereço.
- **Resultado:** 497 nomes (484 antes do Run 332, 492 antes do 346). Os 26 endereços com mais de uma definição dona e nomes diferentes
  (`0053c290`, `0059d8e0`…) ficam sem nome.

#### Nomes originais pelas próprias mensagens (`self-message`)

A biblioteca "real" da EA começa as mensagens de diagnóstico com o nome da própria função
(`STREAM_get - invalid stream handle`, `FILE_loadat - ...`). Um prefixo usado por uma única
função, que não usa nenhum outro prefixo, é o nome original dela. Saíram 60 nomes, todos
coerentes com os arquivos já comprovados:
- os `STREAM_*` em `\real\cmn\stream.c`;
- `FILE_size` e `FILE_loadat` em `hlsfile.c`;
- `FILESYS_*` e `FILE_queueop` em `nfile.c`;
- os `FONT_*` em `font*.c`;
- `showmad` em `FEIntro.cpp`.

As etiquetas genéricas (`ERROR`, `Error`, `DTEX`, `WARNING`) foram descartadas. Esse nome tem
precedência sobre o nome descritivo das recuperações manuais, que fica em `aliases` (por
exemplo, `FILE_size` / `resource_leaf_callback_00561be0`). A função da corrida intermitente,
`0056c540`, é a `STREAM_get`.

O High Stakes de PC confirma a origem dessas mensagens. O `NFSHS.EXE` sem SafeDisc que o
usuário tem (comprimido com Petite; lido da memória depois de se descomprimir, nada copiado
para o repositório) foi compilado com **Watcom C/C++**, e por isso nenhum código casa por
bytes com o Porsche (MSVC). Mesmo assim, ele traz as mesmas mensagens `STREAM_*`/`showmad`,
o que mostra que `stream.c` é a mesma fonte nos dois jogos. Traz também 17 caminhos próprios
(`\nfs4\game\sim.c`, `copter.c`, `\nfs4\frontend\Thrashed.c`…), mas não traz símbolos.

#### Linhagem NFS4 (protótipo do High Stakes de PS1)

O protótipo `Need For Speed 4 v9.0.iso` (do usuário; fica fora do repositório) traz
`NFS4.EXE`, o mapa do linker `NFS4.MAP` e os símbolos Psy-Q `NFS4.SYM`:
- 2.581 funções com nome e arquivo;
- 153 arquivos-fonte em `c:\nfs4\game\{common,psx}`, `c:\nfs4\frontend\{common,psx}` e
  `c:\lib\psx`.

As fontes indicam que a versão de PS1 do NFS4 e o Porsche de PC são da EA Canada, e a
estrutura `game\common` / `game\psx` / `frontend\common` aparece nos dois. Como o código
MIPS não casa com x86 por bytes, a transferência é indireta
(`scripts/research/nfs4-lineage-430.py`, resumo em `nfs4-evidence-summary.json`):
1. **`nfs4-strings`.** Uma string usada por uma única função do NFS4 e por uma única função
   do Porsche forma um par. O par é aceito com ≥2 strings exclusivas, ou com 1 distintiva
   (`%`, `.`, `\`, espaço ou ≥12 caracteres). Saíram 13 nomes, entre eles:
   - `AIInit_LoadConfigs` (`%strafcfg.dat`);
   - `AIPerson_Startup` (`%sprsonal.bin`, `%sscripts.bin`);
   - `Night_InitNightDriving`, `TrackSpec_Read` (`%sTr%02d.bin`);
   - `AudioMus_SysStartUp` (`Music Buffer`, `%szzz%s.viv`);
   - `CopSpeak_StartUp`, `PAD_update`.
2. **Dados globais.** Zero pares, tanto byte a byte quanto convertendo ponto fixo 16.16 para
   `float`. É um resultado negativo registrado; as tabelas de ajuste parecem ter ido para
   arquivos `.bin`.
3. **`nfs4-heranca`, só inferência.** Uma classe RTTI cujo nome é abreviado por um arquivo do
   NFS4, sempre cortando em fronteira de palavra (`AIHigh_Human` → `AIH_HUM.CPP`,
   `FEDialogButton` → `FEDIALOG.CPP`), dá o nome provável do arquivo para 29 classes (125
   funções). O arquivo vai para `_inferido_nfs4/<pasta do NFS4>/`, porque a pasta no NFS5 é
   desconhecida, e nunca substitui um arquivo comprovado.

Limites:
- só ~2% das funções têm arquivo de origem comprovado;
- a fronteira entre arquivos sem âncora não é conhecida e não é inventada.

Validação após os nomes `recovered` (2026-10-20): link sem erros (115 fontes recompiladas) e
traces nativo × rebaixado iguais nas 865 chamadas comparáveis (só mudam os handles). Numa de
quatro execuções o rebaixado parou aos ~14 s, durante o vídeo `ch6.mad`, com
`fault while running pc=0056c597` (em `0056c540`, `\real\cmn\stream.c`), com duas threads
executando código rebaixado. As outras três passaram 30 s sem falha. A renomeação não muda a
semântica, então isso é uma corrida intermitente, ainda não investigada (próximo passo 5).

### Até a corrida (2026-10-20)

Com perfil "claude" criado à mão em `local/run-430/SaveData`, o rebaixado vai do menu até a
corrida pelo mesmo caminho do original: **continue → single player → quick race → RACE**
(356 A Conversível, Côte d'Azur, 4 oponentes). Ele roda 50 s depois de clicar em RACE e mostra
a corrida aos 31 s (HUD, mapa, retrovisor, IA à frente), sem nenhuma parada `[430]`. O menu é
guiado por mouse; teclado não funciona nele (testado), nem na caixa de nome. O roteiro de
cliques fica no scratchpad da sessão (`drive430.ps1`).

Três correções levaram até aí:
1. **Ordem de memória entre threads.** `read257`/`write257` passaram a usar `volatile`. Com
   ponteiros comuns, o `/O2` podia reordenar ou juntar acessos à memória do jogo, enquanto o
   código original depende da ordem do x86. A falha intermitente era isso: `STREAM_get`
   (`0056c540`), na thread do vídeo, lia a contagem da tap (`[eax+8]`) e depois a cabeça
   (`[eax+0xc]`) fora da trava e encontrava `-1` (`ebx=ffffffff`, leitura em `0x3`).
   Depois da correção, 6 de 6 execuções de 30 s passaram (antes, 1 de 4 falhava). Como a falha
   é intermitente, isso é indício, não prova.
2. **`lock inc/dec` atômicos** (`SEMANTIC_PATCHES`). São as únicas 6 instruções com `lock`, o
   contador de leitores do locale do CRT (`006c02e8`, em `005ae3c0`/`005ae490`). Agora usam
   `_InterlockedExchangeAdd`, com as mesmas flags.
3. **Código fora do catálogo alcançado só por `call`/`jmp` direto.** A largada da corrida
   parava em `no lowered body pc=00419c50`: a região `004184e2..00419d4f` não está no catálogo,
   e `00419c50` só é chamada de `00418629`, que também fica fora. `closed_entries` fecha
   transitivamente os alvos rel32 fora do catálogo e cria peças sintéticas para eles: são
   5.608 alvos diretos, 2.840 peças sintéticas e 8.401 corpos rebaixados (antes, 8.284). O
   catálogo versionado (`research/v2/binaries/...`) continua com essa lacuna; corrigi-la é
   trabalho do índice.

## Próximos passos

1. Verificar o uso do resultado da calibração de CPU (`005560b0`) e medir a corrida
2. Ir além do menu (corrida) comparando traces nativo × rebaixado e corrigindo cada
   divergência ou parada fatal (`[430] ...` no stderr).
3. Investigar o crash do `gimme.dll!ConvertFile` no host (provável dependência de layout
   de heap ou pilha).
4. Com o jogo rodando, começar a humanizar: trocar `translated_XXXXXXXX` por funções
   legíveis, uma por vez, comparando estado/memória com a versão rebaixada (os 482 corpos
   já recuperados na main entram primeiro).
5. Corrida intermitente em `0056c540` = `STREAM_get` (`stream.c`, thread de streaming do vídeo): verificar
   se o runtime protege o estado compartilhado entre threads (fila de streaming, área
   reservada) e reproduzir com várias execuções seguidas.

Comandos:

```
py -3 scripts/research/build-v2-lowered-exe-430.py          # gera + compila (incremental)
cd local/run-430 && ../experiments/v2-lowered-exe-430/PorscheLowered.exe Porsche.exe
```
