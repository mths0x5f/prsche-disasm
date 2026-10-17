# v2 / 001 — plano de recuperação do código-fonte

Ponto de controle (checkpoint) 2026-10-17, Run261: **1122 candidate function VAs + 15 support objects**,
1137 membros de arquivo / 1 290 344 bytes. Link real: **417 names / 579 diagnostics**;
sem EXE/DLL. Dois nomes antigos fechados, revelado free_00531f90 canônico.
1133 snapshots de símbolos reutilizados, 4 novos COFFs lidos, 7461 pins PASS, 0 compilações;
um archive/link, 8.811s. Produção verificada Run173: 476 full + 6 partial, sem alterações.

Run257/258: conversão estática x86→C++ de CALL/RET/pilha verificada em 3 cadeias originais:
6 corpos / 104 bytes / 34 instruções, 36 864 comparações nativas e 4 verificações negativas PASS.
Run260: 257 traduz sintaticamente 25 de 85 corpos da fila anterior (em 246: 0).
Este é um experimento de backend isolado; não adiciona novas funções de jogo aceitas.
Run259: 2 corpos canônicos / 2 bindings passaram por auditoria independente, integrados no 261.
005925d0 permanece diferido (deferred): o consumidor real realiza MOVSX AL em vez da extensão de zero original.

Trabalho atual: locale_resume — Run262, cantos de CPU nativa (aritmética sintética,
transferências de subregistradores / pilha / indiretas); scalar_storage_250 — Run263 preflight,
reconexão do heap free_00531f90 canônico. Coordenador — aceitação e commit.
Próximo passo concreto: concluir o 262; confirmar o escopo do 263 pelos consumidores originais,
depois compilar apenas o novo pacote conectado. CPU completa / carregador / importações / inicialização do jogo abertos.
Verificações: runs/258 README, audit-v2-canonical-reuse-259.py,
census-v2-x86-cpp-260.py --validate-existing; comando de união — runs/261/command.json.

Ponto de controle anterior:

Checkpoint 2026-10-16 Run249: 1120 VAs de funções distintas + 13 support objects = 1133 archive
members / 1286822B. Link real 418 names / 602 diagnostics, sem EXE/DLL (-24 names vs 243).
Fronteira vinculada 87 missing FUN / 35 canonical outside / 283 data / 13 other contracts.
26 dependências fechadas, 2 novos contratos canônicos de estado TLS/FILE expostos.
1125 snapshots de símbolos reutilizados, 8 novos COFFs lidos, 7292 pins PASS; 0 union compiles / one archive-link 10.974s.
247: 3 corpos canônicos C++ reutilizados mecanicamente + 3 exact bindings, 4056 native cases,
103 original oracle bytes / 52 CALLs / 293 pins PASS; full provider composition still open.
250/254: 23 writable original DWORDs, 219 MEM4/HIGHLOW refs e native bits / cross writes PASS.
248 navigation overclaims corrigidos em 251; 9 células triadas explicitamente adiadas, sem alocação adivinhada.
246 piloto isolado x86-to-C++: 3 corpos existentes / 76B / 28 instruções, 375808 comparações de registradores / CFZFSFOF /
ESP relativo / memória PASS; um lote 4TU MP6, 0 novas funções aceitas / nenhuma alteração de produção.
252 censo de cobertura: 0/85 corpos restantes suportados integralmente; 80 precisam de CALL, 3 casos de tail JMP selecionados.
256 fila automática atualizada: 418 link names -> 416 tarefas, 20 linhas brutas resolvidas excluídas.
Produção 173 inalterada: 476 full + 6 partial / game-link 267 names 303 refs.
253 piloto tail JMP / MissingEntryVM concluído: 30B originais / 6 instruções, 18432 comparações de cutpoint nativas PASS /
49 pins / 8 guards; JSON de três alvos real retém a procedência do piloto de VM isolado.
Sem funções aceitas / implementações de callee / bindings de FUN nativas ou alimentação da fila principal.
Nenhuma atribuição ativa de agente no checkpoint. Próximo: teste de backend com CALL / stack / RET originais com
tratamento explícito de return PC / alvos desconhecidos, ou provedor canônico conectado da fila 256.
CPU completa / carregador de memória / importações / execução do jogo permanecem não implementados.
Comandos detalhados: runs/249-canonical-and-storage-union e READMEs 246/256; backlog permanece aberto.

Ponto de controle histórico 216:

Checkpoint 2026-10-15, Run216: **1108 diferentes candidate VAs nativos** (+14 em relação a 206),
959 ordinary + 149 leaf, 0 sobreposições. Archive real 1256244B; 443 nomes brutos / 827 refs,
432 nomes não resolvidos reais / 624 diagnósticos, sem EXE/DLL.
Nomes de funções 133→126: 89 corpos ausentes, 36 canônicos fora da união, 1 incompatibilidade de contrato
de compiled-VA 00590290 (símbolo existente de 0 argumentos vs 2 slots de pilha do chamador não utilizados comprovados); nenhum alias adivinhado.
Dados 273→299; 7 contratos CRT impressos. 216 reutilizou 1107 snapshots de símbolos / 531 pins de plataforma,
releu 1 novo objeto, 0 compilações, 6804 pins antes/depois PASS; coletor 7.473s.
214 restaurou a saída DWORD real após GetCurrentPosition, aritmética modular de 32 bits e IDIV com sinal;
42 instruções PE, 36864 comparações asm de cauda de inteiros nativas + 3 casos de proteção de callback PASS.
207/208/210/211/212 auditorias delimitadas PASS; 213 fila de navegação de reutilização 00537b40.
Produção 173 inalterada: 476 full + 6 partial e 267 nomes game-link / 303 refs.
Todos os pacotes 207–216 concluídos; nenhuma atribuição ativa / expectativas de aprovação.
Próximo passo delimitado: binding de símbolo cdecl bruto comprovado de 00590290; depois os chamadores de 00537b40
e 89 funções ausentes / 299 proprietários de dados / aliases / inicializadores. WORD privado 006b48da:2 deve compartilhar base+2.
Provedor completo / falhas / registradores / fidelidade do jogo permanecem em aberto; contagens não representam o restante total do jogo.

Ponto de controle histórico 206:

Checkpoint 2026-10-15, runs 202–206: **1094 diferentes candidate VAs nativos**
(945 ordinary + 149 leaf), +22 em relação a 199; sem sobreposições de VA. Run206: archive real
1238938B; 423 nomes brutos / 800 refs, 413 nomes não resolvidos reais / 600 diagnósticos, sem EXE/DLL.
21 funções anteriores fechadas, 9 novas dependências de funções identificadas: fronteira 145→133
(36 proprietários canônicos fora da união + 97 ausentes); dados 241→273, 7 contratos CRT impressos abertos.
202: 00485100 — 9 gravações raw32 originais / 8 visualizações de bits, 97 instruções PE e 1024 casos de bits nativos PASS;
corpo completo / x87 / equivalência de registradores do chamador permanecem no backlog. COFF inseguro de 200 excluído.
203: 21/25 COFFs novos de um único lote /MP6, 0 avisos; 4 falhas de chamada por ponteiro abertas.
Saída/tempo do compilador observados foram perdidos em falha de metadados e permanecem nulos; fechamentos
de COFF / source / include e diagnósticos verificados separadamente, lote nativo não repetido.
204: pacotes ordinary+leaf repetíveis, pins exatos / cache e proteções de sobreposição; 206 reutilizou
1072 snapshots de símbolos e 531 pins de plataforma, leu 22 novos objetos, 0 compilações.
205: inventário histórico de avisos/regex — navegação, não aceitação semântica.
Produção 173 sem alterações: 476 full + 6 partial, game-link 267 símbolos / 303 refs.
Pacotes concluídos, sem atribuições ativas. README raiz alinhado com o estado v2 atual.
Próximo passo: quatro consumidores de chamada por ponteiro de 203 (00540480/005404e0/00554530/0058f1f0)
conforme CALL/HighIR original; em seguida 97 funções ausentes e 273 proprietários/inicializadores de dados sem stubs.
Comando de união e restrições: runs/206-frontier-and-float-union/README.md da iteração ativa.
Verificações ignoradas: docs/recovery-validation-backlog.md. Corpus completo / oráculos não foram repetidos.

Ponto de controle histórico (substituído pelo resultado do 206):

Checkpoint 2026-10-15 193–199: **1072 diferentes candidate VAs nativos** = 924 ordinary + 148 leaf,
18 novos em relação a a17f569; em 28 corpos leaf os bytes de máquina coincidem com o original.
196: um lote 19-TU /MP6 de 4.373s, 16 novos / 130 reutilizados. 197: 2 COFF, repetição apenas da
004930f0 alterada; seus 15 bytes coincidiram completamente. Ghidra/armazenamento bruto e tipos inferidos separados.
199: archive real de 1072 membros com 1212002B e link diagnóstico sem compilação;
403 nomes brutos / 780 referências de objetos, 393 nomes não resolvidos reais / 581 diagnósticos.
145 FUN: 36 proprietários canônicos fora da união / 109 ausentes; 241 dados e 7 contratos CRT impressos abertos.
198 CLI reutilizável: múltiplos pacotes disjuntos, cache de SHA/símbolo exato, rejeição de sobreposição de VA.
193: 2 correções de ABI de callee restauraram entradas CALL perdidas; 373 instruções PASS.
194: 12 aliases / 21 instruções originais, 8 links diretos token-RAM (7 float4 + gravação raw32);
3 discrepâncias de direção FSTP e casos não resolvidos de armazenamento/strings mantidos explicitamente.
Todo o projeto Ghidra original de 79 arquivos / 572766909B inalterado; exportação/cópias apenas para leitura.
Produção 173: 476 full + 6 partial, antigo game-link 267 símbolos / 303 refs; sem EXE de jogo.
Todos os pacotes 193–199 concluídos, sem atribuições ativas / expectativas de aprovação restantes.
No checkpoint 199 planejava-se o 200: visões externas delimitadas por consumidor para 7 aliases float4 comprovados,
apenas TUs alteradas de 189/184 e COFF em cache; não adivinhar proprietários/inicializadores de armazenamento.
Depois, escalar o exportador token-RAM para classes confirmadas de aliases _DAT/string.
Potenciais 757 corpos de lacuna _DAT — escopo de investigação, não correções aceitas.
Encaminhar escalonamentos do Ghidra ao coordenador imediatamente; não repetir corpus completo / oráculos,
manter verificações ignoradas em docs/recovery-validation-backlog.md.

Verificações de checkpoint a partir da raiz (sem recompilação/exportação):

```powershell
py -3 scripts/research/audit-v2-abi-193.py
py -3 iterations/v2/001-original-recovery/runs/194-global-aliases/verify-capture.py
py -3 iterations/v2/001-original-recovery/runs/196-thiscall-leaf-delta/audit.py
py -3 scripts/research/audit-v2-abi-leaves-197.py
py -3 iterations/v2/001-original-recovery/runs/198-native-union/audit.py
```

Comando CLI exato do archive/link final de 1072 objetos e o SHA do seu resultado:
`runs/199-native-abi-union/README.md` e `validation.json`; repetição requer nova saída/run.

2026-10-14: compilação em primeiro lugar 192/190: 1054 VAs distintos de Porsche.exe forneceram
COFF x86 reais: 924 do corpus geral + 130 folhas thiscall, 0 sobreposições. Em 27 corpos leaf
os bytes de máquina coincidem com o original. Estes são candidatos, não aceitação de EXE do jogo / fidelidade;
a linha de base de produção 476 full + 6 partial e game-link 173 com 267 símbolos / 303 refs permanecem inalterados.
184: 3312 TUs reutilizadas; 2460 alteradas cobriram 37 cl em lote + 12 pilotos / 153 falhas anteriores,
sintaxe 733→923, erros de globais ausentes 25306→16818, 0 perda / 0 fallback ambíguo.
188: 733 objetos reutilizados / 190 novos, 3 lotes /MP6 em 43.416s, 0 erros de codegen;
384 nomes indefinidos / 747 refs do subconjunto automático. 187: 127 COFF / 32 falhas, apenas __fltused 8 refs.
186: 1258/1301 extensões RET inferidas correspondem; 42 incompatibilidades / 1 sem RET, argumentos de chamada ausentes permanecem abertos.
189 concluído: 99 reescritas exatas / 39 TUs, 1920 verificações nativas; aprovação de sintaxe 923→924.
192: 923 COFF reutilizados / 1 novo 00553a70, 2.732s / 0 erros de codegen; 190 130 leaf COFF / 29 falhas.
Reutilização idêntica em bytes e evidências originais de ABI/dados são mantidas. Sem EXE por enquanto.

Decisão do usuário 2026-10-08: manter a v1 como está, obter o corpus descompilado/desmontado
completo e restaurar o original compilável. Proprietário — coordenador. Prioridade: inicialização C/C++ → linkagem → execução real.
Pacote aceito atual — 173: 476 full + 6 partial registrados; 173 enviado (pushed) 6952020.
Compilação geral MSVC Win32: 157 projetos / 292 TUs exclusivas; 137 alvos de comparação/alias,
9 fixações de SO nativas e 3 de link. Todas as 12 verificações nativas/link passaram.
15 relatórios original-x86 recentes / 24560 comparações, incluindo 8791 repetições de produção,
mais 4 casos compostos comprovados por componentes. Game-link 267 símbolos / 303 refs, 0 erros de compilador / outros diagnósticos; sem EXE.
Índice manual 40 / 36627 entradas. Aceitas 46 novas: 167 output 16, 168 transport 8, 170 parse 10, 171 constructors 12.
00580ad0 preserva o proprietário canônico de io_find; 168 compila/chama diretamente como regressão.
167 ambas as compilações 4991 casos nativos originais reais; 170 ambas 3800 casos nativos + Unicorn;
estado completo de arena/return/ABI/x87, impressões digitais semânticas de observador/produção são iguais.
37208 eventos intermediários de output + 16216 de analisador; discrepâncias do Unicorn de 1356 FPU / 390 memória NaN / 432 estágio NaN
preservadas explicitamente; hardware original real tem autoridade, flags não são mascarados.
168 385 casos, 171 2441 casos. Construtores incluem vptrs nativos intermediários/finais;
proprietários de RTTI / provedor real / efeitos de worker ainda abertos. Vtables originais brutas não estão conectadas nos armazenamentos de produção.
11 testes de cache/atualização PASS; atualização automática preserva modo de nome de arquivo/compilação/trace-off de produção,
e o modo ambíguo/ausente não é substituído por compilação instrumentada. Relatórios de prova SHA 121 / 701 hashes únicos PASS.

Prioridade 2026-10-12: a meta da primeira execução não deve esperar pela aceitação profunda de cada
uma de milhares de funções. Restaurar o grafo compilável completo mecanicamente a partir de instruções/ramificações originais
e ABIs exatas; corrigir bloqueadores reais de compilador/link.
Não considerar candidatos de compilação não verificados como verificados e não apresentá-los como um jogo pronto.
Primeira execução do candidato — experimento isolado em local/experiments com comparação com o original;
nenhuma implementação adivinhada / stubs na produção, recursos originais somente leitura.
Verificações semânticas são preservadas no backlog e executadas em lotes; fidelidade total
é obrigatória para a aceitação final. O caminho C/C++ autorizado é mantido.

Transmissão 2026-10-14: 189/190/192 concluídos, sem atribuições ativas.
Root — checkpoint final; pacotes não constituem o encerramento da v2/001 ou um jogo pronto.
192 924 COFF + 190 130 leaf COFF disjuntos = 1054 VAs exclusivos do Porsche.exe.
189 99 reescritas exatas de fatias / 39 TUs; 1920 verificações nativas de bytes, 5733 inalteradas,
12 cache de piloto + 27 verificações em um único lote MP6 de 5.806s; sintaxe 923→924, 0 perdas.
192 923 objetos reutilizados + 1 novo 00553a70, 1 lote 2.732s, 0 erros de codegen.
190 127 leaf COFF reutilizados + 3 novos, 130 leaf COFF / 29 falhas, 27 corpos originais idênticos em bytes.
188 construtor de lote pronto e reutilizado; cache inclui fontes/cabeçalhos/compilador/flags
e verificação do fechamento completo de dependências. Fase geral 173 de produção com 476 full + 6 partial inalterada.
184 923 aprovações de sintaxe (+190), 8488 diagnósticos de globais ausentes eliminados; 4604 layouts verificados,
837 conflitos / 681 nomes inválidos / 2 MXCSR e aliases impressos permanecem explícitos.
186 prova de ABI nativa /Od, /O2: 165 chamadas / 403 condições cada; RET de thiscall 1258 correspondências / 42 incompatibilidades / 1 sem RET.
Perda de argumentos impressos de callee/caller não é corrigida por reescrita genérica de classes.
Root verificou Ghidra 12.1.3 instalado PrintC::opCall (printc.cc 610–655): directcalls
imprime todas as entradas de IR, skip=-1; alternar hide_thisparam não restaurará o receptor perdido.
Próximo passo concreto: piloto de correção de ABI orientado por CALL/RET original em experimento de análise
SEPARADO para 00489370→00489530 e 00483290→00482f70, comparar entradas emitidas
com registradores/pilha originais. Não modificar projeto/corpus indexado congelado.
Bloco grande independente — proveniência de alias/largura de acesso global impresso por consumidores originais
para 1431 corpos com lacuna de nome; não escolher tipo/armazenamento arbitrário para 837 conflitos.
Estas tarefas ainda não foram atribuídas. Após o piloto confirmado — apenas lotes de TUs alteradas,
depois o construtor 188 com o cache anterior do 192; não repetir toda a suíte nativa/oráculo/corpus.
172/174/175 pronta a fila 176; 131 áudio / 00525ec0 isolado. Armazenamento/aliases globais compartilhados,
ABI de chamador completo / inicialização / SO / loop de jogo permanecem abertos. Nenhum EXE completo.
Novas saídas explicitamente em LF antes do SHA; bytes congelados dos relatórios brutos do Ghidra/186/187 são preservados exatamente.
Após a linha de base C/C++ verificada — esquema arquitetural e Rust nativo/web.

## Objetivo e prontidão 001

Todos os binários em `local/game` possuem SHA, arquitetura e um diretório separado de corpus.
Todas as instruções e funções descobertas pelo Ghidra foram exportadas. Cada função
passa por uma tentativa de descompilação com resultado/erro. Bytes executáveis não analisados
e links não resolvidos são contabilizados explicitamente. O resultado é reproduzível
a partir de entradas imutáveis. O número de funções recuperadas/correspondentes não se confunde
com o número de funções exportadas automaticamente.

## Próximas etapas da v2

1. Corpus completo, dados, dependências e lista de lacunas.
2. Definição da família/versão do compilador, CRT, flags, layout e ABI;
   o primeiro fonte comum compila com correspondência de código de máquina.
3. Recuperação de declarações, dados globais, classes/vtables e módulos
   no grafo completo do programa. O código-fonte manual permanece vinculado ao SHA/VA.
4. Compilação Windows/x86 nativa completa com carreira, física, IA,
   economia, danos, interface do usuário e som originais. Verificação cruzada de funções/dados/módulos,
   pilotagem e progressão reais. Lógica indefinida não é substituída por stub.
5. Após a análise/recuperação completa do código, construir um esquema geral de funcionamento
   do jogo em `docs/architecture/`: inicialização/encerramento, loop principal, módulos/grafo de chamadas,
   threads/callbacks, dados/recursos e conexões de todos os subsistemas do jogo.
   Os esquemas se vinculam a arquivos C/C++ e módulo/SHA/VA originais; o desconhecido fica separado.
   Critério: rastreabilidade de inicialização→menu→corrida→resultado/salvamento→saída.
   Tarefa detalhada — seção do PLAN geral "Esquema de funcionamento do jogo após a recuperação do código".
6. Após a baseline C/C++ verificada e o esquema de arquitetura, reescrever o jogo
   em Rust para nativo/web (decisão do usuário 2026-10-10). O esquema revela
   previamente as fronteiras dos módulos, propriedade/ciclo de vida dos dados e troca entre subsistemas;
   a migração preserva a semântica do jogo e é verificada nos mesmos oráculos originais.

## Confirmado

- Ponto de controle v1 `dc6b9d8`, enviado (pushed); 012 não finalizada.
- Índice anterior: 26 caminhos, 25 hashes únicos; 24 PEs únicos,
  36 510 funções, 2 825 280 instruções. Um NE não coberto pela análise de PE.
- Ghidra 12.1.3 contém NeLoader; sua importação separada é viável.
- Porsche.exe SHA ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39,
  PE linker 6.0, string do runtime do Visual C++ no VA 0x5c1e5c.
- SpaceRangersHD_decomp documenta Delphi recuperado + verificação de SHA de EXE completo;
  este é um exemplo de metodologia, não a transferência de seu compilador para o Porsche.

## Hipóteses e desconhecido

Origem da era MSVC é provável; compilador exato, CRT e parâmetros são desconhecidos.
A autoanálise do Ghidra não garante completude de fronteiras, alvos indiretos ou tipos.
O pseudo-C não compila automaticamente. Módulos de publicação / patches / instaladores
são considerados integralmente, mas sua necessidade para a baseline do jogo ainda está sendo apurada.

## Realizado no Run 002

Run 001: corpus completo de 24 PE + 1 NE, 36 587 funções / 2 827 310 instruções;
36 583 pseudo-C, 4 falhas/timeouts, 5639 funções com avisos,
3 199 385 bytes executáveis não classificados. Porsche.exe: 5772/5772 pseudo-C.

Escolha do usuário: diretamente C/C++, a primeira execução do jogo pode ocorrer mais tarde.
Criados source/include, source/recovered/<module>, catálogo de endereços completo de
25 módulos / 36 587 funções e compilação separada de porsche_original.lib/probe.
O salto 0x4b6710..0x4b67a4 foi recuperado com quatro argumentos stdcall;
175 casos de C++/x86 coincidiram. O desconhecido 0x4b6a50 é uma fronteira de gravação apenas
no probe de teste. 1 função manual verificada, 0 correspondências de bytes/módulos.
Inicialização (Startup): quatro estágios, 3093 funções estaticamente alcançáveis; alvos
indiretos e omissões estão abertos. Relatório completo: runs/002-cpp-startup.

## Realizado no Run 003

Encontrado fe.txt real (13 805 bytes), exportadas
48 definições / 144 valores / 7 ações (com terminadores), 53 nomes de carros,
42 palavras globais originais. O produtor/arquivo/argumentos/despachante em C++ foi incluído
na biblioteca; todos os 236 casos coincidiram com o x86 original. Comparados fluxo,
comprimentos de registro, campos globais, buffers, callbacks e ordem de chamadas de arquivo/heap.
O fe.txt real produz 23 registros / 47 palavras com terminador (188 bytes), os argumentos
sobre ele — 25 registros / 51 palavras. Ramos indexados/string/vetor/ação
foram verificados com tabelas separadas apenas na memória da bancada de teste; tabelas originais
na biblioteca não foram substituídas. O tratamento não padrão de # e o ramo de arquivo vazio
foram preservados de acordo com as instruções do original.

Consulta ao índice: FE_Data_Stream/fe.txt → callers/callees 0x4b6660/0x4b5ee0/
0x4b60d0 → atribuição/token/valor/ação 0x4b5470/0x4b51e0/0x4b5250/0x4b5430
→ despacho/comprimento de registro 0x4b4b80/0x4b4cd0. SHA do Porsche.exe especificado acima.
Tabelas tipadas: 0x5d1e40/0x5d63a0/0x5cc5c8/0x5d61e8.
Evidências e comandos: runs/003-fe-stream/README.md, verification.json,
tables.json, source-functions.jsonl, source-calls.jsonl.

Total de 10 funções manuais verificadas, 0 correspondências de bytes/módulos inteiros.
Callees desconhecidos de arquivo/heap/callback permanecem como extern na biblioteca. Suas
substituições de gravação encontram-se apenas em fe_stream_probe; a comparação original da CRT
foi executada no locale C, a bancada nativa verifica a igualdade de strings ASCII.
Isso não constitui a recuperação dos efeitos de callbacks, VFS, alocador ou troca de locale.
A execução real do jogo e a aceitação visual permanecem em aberto.

## Realizado no Run 004

Recuperadas 11 funções da heap proprietária: 0x5697f0 init,
0x531ca0 alocação, 0x531f90 free, 0x569640 resize;
auxiliares 0x531c60/0x5320b0/0x556620/0x556650/0x56e2c0/0x5323e0/0x5b0000.
Consulta ao índice: alocação/free/resize de FE → callers/callees → referências
da tabela 0x6b4f20 → construtor 0x5697f0 e invólucro de inicialização 0x5aef80.
VAs/intervalos/chamadas, globais e toolchain originais preservados em runs/004-original-heap.

Todos os 551 casos coincidiram com o x86 de origem: arena completa após cada etapa,
incluindo cabeçalhos físicos, listas livres, payload, sufixo/nome/proteção,
retornos e chamadas externas. O flag 0x10 seleciona a extremidade superior, 0x20 — o maior
bloco adequado; o limite de divisão é estritamente >0x40. O redimensionamento (resize) preserva o ponteiro,
podendo limitar o crescimento ao espaço vizinho disponível; -1 solicita o máximo.
Cabeçalho de 16 bytes / bloco de controle de 64 bytes confirmados por comparação nativa/x86.
005deb10 é originalmente igual a 1, os demais flags de cópia são iguais a 0 — verificados com base nos dados do PE.

Corrigida a ABI de free (retorno 1); 236 regressões de FE repetidas na nova pasta
runs/004-original-heap/fe-regression, o registro aponta para novos SHAs.
Run 001–003 preservados como históricos. Total de 21 funções manuais verificadas.
Na biblioteca, o alocador/free/resize de FE agora resolvem em heap.cpp;
a regressão de FE ainda utiliza sua própria heap gravadora. Execução conjunta de FE/heap/IO
ainda não verificada. Formatação/preenchimento da CRT, travas de SO, alvos de cópia SIMD
e callback de falha de alocação verificados em fronteiras de gravação, não recuperados.

## Realizado no Run 005

29 novas funções C++ de requisições de arquivos/fila/status/conclusão/leitura em blocos
e listas de operações comparadas com x86 em 89 casos conjuntos de FE/heap/IO.
551 regressões de heap e 236 de FE preservadas em novas subpastas do Run005.
Verificados grupo de bytes, rotação serial, ordenação com chaves iguais, busca/remoção,
EOF/leitura incompleta/recusa, primário/alternativo e fe.txt real (23 registros/188 bytes).
Estado completo de heap/dispositivo/operação/lista/buffer/nome/fluxo/globais e chamadas coincidiram.

3 callbacks omitidos 0x533cd0/0x567bf0/0x5684c0 adicionados ao índice suplementar
de SHA/corpo: 36 587 automáticos + 3 manuais. Total de 50 funções manuais
verificadas, 0 correspondências de bytes/módulos. ABI de bool open é comparada por AL, read/close
por EAX. Fonte/VA/chamadas/layout/globais/toolchain e limites de verificação —
runs/005-original-files/README.md e verification.json.

FE vinculado à heap real e ao frontend de IO em probe conjunto. O worker executa
a conclusão imediatamente apenas na fixação (fixture): o agendador original ainda não foi recuperado.
Invólucros de disco/arquivo/VirtualAlloc, SO/CRT/SIMD e efeitos de callbacks de FE são externos.
Opcodes de arquivo e estados fatal/concorrente/locale/nome-nulo-em-tempo-de-execução não foram aceitos.
Runs antigas 001–004 preservadas; o registro indica os SHAs atualizados do Run005.

## Realizado no Run 006

6 novas funções de invólucros de página / construtores de lista / chave padrão / inicialização de dispositivo
comparadas em 474 casos com x86. 89 casos conjuntos de FE/heap/IO repetidos
com invólucros de página reais; alocação de gravação agora em importações Win32.
Arredondamento de página com sinal com LEA/IDIV/IMUL e VirtualFree em EAX preservados.
Total de 56 funções verificadas. Relatórios isolados de heap/FE do Run005 estão atualizados
por SHA; runs antigas inalteradas. Relatório geral — runs/006-file-device.

Worker 0x568530..0x5688cc (925 bytes) e chave padrão 0x580670..0x580674
adicionados ao índice suplementar de SHA/corpo. Catálogo: 36 587 automáticos + 5.
Worker ainda não recuperado, fora da contagem de 56; SO/thread/evento/trava/diagnóstico
e disco bruto/arquivo permanecem como limites. O início de thread na fixação fornece apenas
o registro inicial initialized=1; a execução do loop do worker e a concorrência não foram aceitas.

## Realizado no Run007 — worker e conclusão

Consulta ao índice: `00568530`, tabela `005688d0`, consumidores `005806e0/005808f0`.
SHA/11 alvos/bytes — runs/007-file-worker/dispatch.json. O coordenador é proprietário de
file_worker.cpp, io_worker_lists.cpp, ABI, integração e aceitação.
worker_probe (worker, gpt-6-sol, medium) — probe nativo e verificador x86.
Recuperados ramos C++ 0..10, cancelamento, portão de grupo, conclusão e callback.
69 casos diferenciais passaram, incluindo a arena completa e estados intermediários.
3 novas funções aceitas, total de 59. Todas as seis bancadas de teste MSVC Win32 compilam.
SO/backend/evento/trava ainda são fronteiras de gravação; concorrência não comprovada.

## Realizado no Run008

Espera de operação 0x567f70 comparada em 87 casos de unidade. O files_probe conjunto executa
worker/espera/busca/status reais em vez de simulação de conclusão; 89 casos conjuntos
coincidiram em toda a arena e instantâneos de eventos intermediários. O fe.txt real produz
23 registros / 188 bytes (afirmação). Total de 60 funções, sete bancadas compiláveis.
Registro de 29 funções de arquivo migrado para o relatório conjunto atual do Run008.
Runs antigas preservadas. SO/backend/thread/pump/CRT/SIMD/callbacks de FE ainda são fronteiras.

## Realizado no Run009

15 invólucros de eventos/sleep 0x55f740/0x55fb20..0x55fce0 comparados em 249 casos.
3751 endereços IAT corrigidos com preservação de 4217 registros de caminho/dll/símbolo/ordem.
Assinaturas de retorno u32/HANDLE originais recuperadas, probes de gravação corrigidos.
Regressões de dispositivo/worker/espera/conjuntas de 474/69/87/89 passaram; registro aponta novos
relatórios do Run009. fe.txt real com 23 registros/188 bytes. Total de 75 funções e oito
bancadas de teste. Comparação de eventos por enquanto unitária; no conjunto de invólucros de evento ainda são fronteiras.
Atribuições de worker_probe/import_index concluídas, sem tarefas pendentes.

## Realizado no Run010

10 funções de thread e 94 comparações de estado completo com x86 original aceitas.
Invólucros de eventos em FE/heap/IO conjuntos executam em C++; 89 casos passaram.
Total de 85 funções verificadas, nove bancadas; trampolim suplementar totaliza
o catálogo em 36593 registros. Relatórios antigos não foram alterados. README e relatórios do Run010
preservam SHA, endereços, retornos observados e restrições de handshake/concorrência.

## Passo atual e transmissão

Coordenador — integração e aceitação; worker_probe e import_index concluíram o Run010.
Conforme solicitado pelo usuário, a análise é paralela. disk_backend (formatos, perfil
forte fixo) possui exclusivamente file_disk.hpp/cpp, disk_probe, verificador e Run011:
0x591ce0/0x591df0/0x592140/0x592290; open 0x5919a0 com semântica confirmada.
fe_callbacks (worker, gpt-6-sol medium) — apenas novos callback header/source/probe,
verificador e Run012: 0x4119e0/0x411a80/0x411b40. Ambos retomados após cota;
seus arquivos incompletos foram excluídos do checkpoint aceito do Run010.
Próximo passo do coordenador: commit/push Run010, conectar alvos isolados,
corrigir ABI de retorno geral de callbacks de FE e repetir provas de FE/conjuntas afetadas.
Após aceitação de disco/callback — encerramento de threads 0x55f1c0 / registro de saída,
execução conjunta de consumidores de thread, arquivo e inicialização 0x4b6a50.
Callees desconhecidos — fronteiras de gravação explícitas; concorrência de SO e execução do jogo
não foram aceitas. Escritor de taxa de timer 0x5deb48 e compilador/CRT/flags permanecem abertos.

Comandos atuais:

    powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-v2.ps1
    py -3 scripts/research/verify-v2-file-threads.py
    py -3 scripts/research/verify-v2-file-events.py
    py -3 scripts/research/verify-v2-file-device.py
    py -3 scripts/research/verify-v2-file-worker.py
    py -3 scripts/research/verify-v2-file-wait.py
    py -3 scripts/research/verify-v2-files.py
    py -3 scripts/research/test_index_binaries.py
    py -3 scripts/research/inventory-v2.py --require-listing --require-decompile-attempts
    py -3 scripts/research/structure-v2.py
    py -3 scripts/research/trace-v2-startup.py
    py -3 scripts/research/inventory-v2.py --require-listing --require-decompile-attempts --write-verification

Histórico de runs não se altera. Provas isoladas de SHA de heap/FE do Run005 estão atualizadas.
CRT/loop-principal/renderizador/áudio/entrada, compilador/flags, quatro erros de descompilação e
bytes não classificados estão abertos. MSVC 19.44.35229 — ferramenta moderna medida,
não o compilador original comprovado. local/game somente para leitura.
EXE de jogo e aceitação visual ausentes; a iteração não está encerrada.

2026-10-09: Checkpoint Run010 6839d44 enviado (pushed). Ambos os agentes retomados após cota;
11 alvos conectados. ABI de retorno de callback de FE corrigida para u32 EAX=0 pelo Run012;
provas afetadas são repetidas em pastas de regressão frescas do Run012.

Run013: fe_callbacks (worker, gpt-6-sol medium) — novos header/source/probe de input_state,
verificador e run; 532e10/56fce0/56fd00/56fd30, vtables de DirectInput controladas.
Run014: heap_locks (worker, gpt-6-sol medium) — novos header/source/probe de trava,
verificador e run; 5321f0/532250/5322b0/5322c0/5322d0, pool exato e chamadas Win32.
O coordenador é proprietário dos arquivos comuns, checkpoints e próxima vinculação conjunta de disco.

## Realizado no Run011/012 — 2026-10-09

4 consumidores de disco comparados em 31 casos, 3 callbacks de FE em 1320.
Consumidores mais próximos confirmados pelo índice; Button4119e0 suplementado manualmente
por body SHA/97bytes/dois RET, catálogo 36594 (7 suplementares).
ABI de u32 do callback de FE alterada em header/table/exporter/probes. Todas as provas
afetadas repetidas em novas pastas de regressão do Run012; registro atualizado.
Total de 92 funções verificadas, 11 bancadas de teste compiláveis. I/O de SO / concorrência / getstate
permanecem como limites explícitos. Sem EXE de jogo e aceitação visual.
Backend de disco Run011 aceito; próximo disk_backend Run016 — apenas novos
arquivos de abertura física e fixações x86. Run013 input e Run014 locks ativos.
Coordenador: checkpoint Run011/012, compilação de novos alvos, vinculação conjunta disco/callback
no Run015. Fontes inacabadas de agentes excluídas do manifesto de corpus.

## Aceito no Run013/014/015

100 funções C++ totalmente verificadas e 1 parcial 532e10. 1026 input / 31 locks /
89 disco conjunto / 1320 casos de callback passaram; 14 alvos MSVC compilados.
Modos de entrada do Run017 e evidências de bootstrap de trava do Run018 aceitos, não provas executáveis.
Atribuições após a retomada: input_check (worker, gpt-6-sol medium) — Run019
apenas novos arquivos de input_buffer / verificador / run, consumidores 56fdb0/56fff0.
heap_locks (worker, gpt-6-sol medium) — Run020 novos bootstrap_probe / verificador / run,
conjunto 55f320→lockpool/pages/Win32. fe_callbacks (worker, gpt-6-sol medium)
reatribuído para o Run016 novos arquivos de disk_open / verificador / run em substituição ao
disk_backend ausente. O antigo input_state pertence ao Run013 aceito; não alterar mais
até uma nova migração atribuída. Coordenador: integração, compilações e checkpoints.
Próximo passo: commit/push 100, depois alvos dos 016/019/020 prontos, provas x86,
encerramento de threads/saída e inicialização 4b6a50. Sem aproximações de jogabilidade; apenas o original.

## Run016/019/020 e prioridade da primeira execução

103 funções completas, 2 parciais. 1672 abertura física / 37 propriedade de entrada / 27 bootstrap conjunto
de comparações nativas-originais passaram. 17 alvos Win32 compilam. Grafo conjunto
55f320→55f3b0→5321f0/532250→56e5f0 utiliza código-fonte real, confirma
ordem do flag BSS e interrupção de init aninhada; contenção de SO ainda não aceita.
Relatórios novos de input 1026 / callback 1320 do Run020 gravados com os SHAs de compilação atuais.
A pedido de aceleração, selecionamos o próximo código pelo caminho de inicialização 4b6a50, e não pela contagem
de pequenas funções. No total 3 slots de worker + coordenador, compilações comuns sequenciais.
Atribuições atuais (worker, gpt-6-sol medium): heap_locks→Run022 apenas novos
2 consumidores de startup_services 4a5410/4a5c30; input_check→Run023 novos resource_paths
59d650; fe_callbacks→Run024 novos render_startup 467470. Consumidores C++ comparados
pelo asm original; seus callees desconhecidos permanecem como fronteiras tipadas.
Run016/019/020 aceitos, atribuições anteriores cumpridas. Root: checkpoint 103,
depois bindings Win32 / estado de inicialização compartilhado e consumidor comum de inicialização 4b6a50.
A primeira janela/menu do jogo exige bindings reais de construtor / renderizador / FE;
os probes aceitos não são declarados como execução do jogo. Campos/aliases de inicialização devem
coincidir com os consumidores originais, sem criar duplicatas independentes de globais.

## Run030 — integração do pacote de inicialização, 2026-10-09

Aceitos Run022–027: 12 novas funções completas e um prefixo de exibição; total de 115 full,
3 partial. Consultas ao índice, SHA/endereços e fronteiras — no README de cada run.
23 probes MSVC Win32 compilados pelo comando geral; novas fixações comparadas com x86.
Regressões frescas de input / callback / diskopen / inputbuffer encontram-se no Run030.
Atribuições anteriores Run020/013/014 são históricas, não atribuições ativas.

Proprietários: startup_heap — alocador Run031 e inicialização de heap Run033;
display_ctor — THRASH Run028 e construtor de display Run032;
window_runtime — Run029 RegisterClass 53ac20 / configuração / chamador 53b8d0.
Coordenador — linkagem geral / bindings Win32, atualização do registro e checkpoint.

Verificações: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-v2.ps1`
e `py -3 scripts/research/inventory-v2.py --require-listing --require-decompile-attempts --write-verification`.
Todos os comandos de prova / diretórios novos — Run030/README. Em seguida integração de 028/029/031
e o caminho real de inicialização/janela. Fixação de unidade de CreateWindow ainda não é uma janela real.

## Run036 — bancada de janela nativa, 2026-10-09

Ponto de controle Run030 1e8d25c enviado (pushed). Aceitos 028/029/031/033/034: total de 129 full,
3 partial. Índice suplementar 9 funções; novas 53a7f0/53aba0 vinculadas a SHA/RET.
Compilação geral de 28 probes de comparação + native_window_smoke passa com sucesso. Relatórios novos de input,
callback, diskopen, inputbuffer, paths, renderer — sob 036; histórico inalterado.
Execução real do EXE Win32: HWND/cliente 640×480, registrado WndProc recuperado,
39 mensagens padrão, destruição correta, exit 0. Entradas/restrições exatas e hashes —
036/native-window-result.json. Esta é uma fixação de plataforma, não aceitação do jogo original.

Após o esgotamento dos agentes anteriores, foram designados workers gpt-6-luna/high:
window_worker_recovery — correção de estado compartilhado 035, depois tabela de manipuladores 038;
display_recovery — construtor completo 4677e0, mutável 032;
heap_init_recovery — alocador/heap conjunta da aplicação real 040 (evidência 037 pronta,
ainda não aceita). Coordenador — linkagem comum, bindings Win32 reais, inicialização principal.
Restante arquitetural: armazenamento único / aliases de configuração da janela original; unidades
de fonte com os mesmos VAs não devem ter cópias independentes de variáveis globais. Chamadas desconhecidas
não são vinculadas como no-op silencioso. Antes do EXE completo, recuperar 4b6a50 e os callees necessários.

Verificações: scripts/build-v2.ps1; inventory-v2.py com require-listing,
require-decompile-attempts, write-verification; comandos de prova 028/029/031/033/034;
036 native_window_smoke executado separadamente na realidade. Próximo checkpoint — aceitos
035/032/038/040 e cadeia de inicialização original estendida, sem declarações de jogo pronto.

## Run041 — compilação geral de inicialização, 2026-10-09

Aceitos 032/035/037/038/039/040/042/043/044. 150 full, 4 partial; 20 corpos
suplementares e 36607 funções indexadas. Consultas ao índice / SHA / VA / layout — README dos pacotes;
relatório aceito / restrições / comandos exatos — runs/041-startup-chain/README.md.
37 probes + native_window_smoke compilam. 4848 comparações, 6 asserções de alias,
HWND 640x480 real / WndProc recuperado / 39 mensagens / fechamento limpo passaram. Run037 parcial,
qsort 005a112b original permanece como fronteira tipada, não std::sort. Histórico de runs preservado.

Próximo passo concreto: checkpoint 041; aceitar 045 mensagens, 046 configuração do DirectInput,
047 inicialização de FE; concluir 048 posicionamento da janela, 049 ativação da renderização, 050 instância.
Em seguida, vincular os VAs dos callbacks originais a ponteiros C++ nativos e adaptadores de SO/CRT,
recuperar o main 004b6a50 restante e verificar a cadeia de inicialização real. Ausência
de no-op silencioso é obrigatória; provas de fixture não substituem aceitação visual/de jogo.

## Próxima integração após b16d4f0

Run041 aceito e enviado como b16d4f0. Novos pacotes isolados 045–054/056 prontos,
mas ainda não fazem parte do CMake/registro comum. Root prepara 061-startup-platform-integration.
Run055: biblioteca separada source/platform/win32_core.cpp e smoke de SO real;
Run057: init/start/trampolim/cancelamento de registro/encerramento reais de threads originais no Windows,
ambos os caminhos no-arg/worker-arg passaram. Resultados/hashes nativos preservados em 055/057/native-result.json.
Restam duas fronteiras explícitas de fixtures de CRT (preenchimento e registro de saída), o jogo não foi iniciado.

Na aceitação, o 053 foi corrigido: o loop de callback deve recarregar a base 006c1534 após o callback,
e não colocá-la em cache; aritmética unsigned32 evita UB de ponteiro C++ antes do início (pointer-before-begin). Novo
caso de callback mutável passou; agora 8 casos. No 048 foi corrigido erro de leitura de pilha:
consideração de dois PUSH revelou um RECT inicializado; 66 casos incluem asserções de ESP em tempo real.
045 rota de mouse 5728b0 e 056 rota de renderizador acessam o mesmo consumidor; 060 adiciona
implementação/adaptadores unificados. 046 557380 já recuperado no 037, 050 557370 embutido (inlined),
047 fragmento principal não é uma função autônoma: não contabilizá-los como novas funções completas.

Próximo passo do root: revisão dos pacotes prontos e aliases canônicos; novos alvos comuns,
recompilação, relatórios diferenciais 061 frescos e 6 regressões dependentes de CMake; índice
suplementar dos corpos de callback ausentes; atualização de registro/planos e commit/push intermediário.
058 main deixa a limpeza de 6573e8/3e24 como fronteira explícita até o armazenamento geral de FE: proibido
memset no endereço de um global individual. 059 fecha os callbacks restantes antes da inicialização
real da janela (window_init). Nem correspondência de bytes, nem executável completo do jogo foram aceitos até o momento.
