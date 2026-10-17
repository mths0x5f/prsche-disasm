# v2 / 001 — recuperação do código-fonte original

Ponto de controle (checkpoint) atual — [Run261](runs/261-canonical-reuse-union/README.md): 1122 candidate
function VAs + 15 support objects, restam 417 link names, EXE/DLL ausente.
[Run258](runs/258-x86-call-chain/README.md): 3 cadeias originais de CALL / 36 864 comparações nativas PASS.
Tarefas ativas e restrições exatas — [PLAN.md](PLAN.md).

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

Checkpoints históricos:

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

Checkpoints históricos:

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

Checkpoints históricos:

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

Resultado atual — [Run173](runs/173-float-transport-integration/README.md): **476 funções C++ verificadas** e 6 consumidores parciais registrados.
Compilação geral MSVC Win32: 157 projetos / 292 TUs exclusivas; 137 alvos de comparação/alias, 9 fixações nativas de SO e 3 de link.
15 relatórios original-x86 recentes / 24560 comparações, incluindo 8791 repetições em produção sem observadores, mais 4 casos compostos; todas as 12 verificações nativas/link passaram.
Aceitas 46 novas funções: saída/análise float original, transporte de rede inferior e construtores de rede.
00580ad0 verificada novamente via io_find canônico; segundo algoritmo e contagem dupla eliminados.
Game-link: 0 erros de compilação / 267 símbolos não resolvidos / 303 referências / 0 outros diagnósticos; sem EXE de jogo.
Esta é a fronteira atual de dependências, não o restante completo. Proprietários de RTTI e 004d3420 completo ainda estão abertos.
Prioridade 2026-10-12: grafo C/C++ completo compilável → primeira execução experimental; verificações profundas em lotes via backlog.
Funções verificadas e candidatos de compilação restaurados mecanicamente são contabilizados separadamente; sem stubs e algoritmos adivinhados no jogo.
Auditoria de SHA em lote/cache; inventário medido de 9,3→2,4s refere-se ao 156, não a toda a recuperação.
Rota: baseline C/C++ completo e verificado → esquema da arquitetura do jogo → Rust native/web.
Execução completa do jogo, timer em tempo real / WM_CLOSE e aceitação visual permanecem em aberto.

Iniciado em 2026-10-08 por decisão do usuário. O desenvolvimento anterior está preservado
no commit `dc6b9d8`; 012 incompleta, a continuidade de sua integração foi interrompida.
001–011 não são modificados. Dados do jogo compartilhados: `local/game`, somente leitura.

[Run 001](runs/001-full-corpus/README.md): todos os 25 módulos foram exportados,
36 587 funções tentadas pelo descompilador; 36 583 resultados em pseudo-C e
4 falhas/timeouts foram preservados. Porsche.exe principal — 5772/5772 sem falhas/timeout.
Este é o corpus automático completo de código descoberto. Fontes compiláveis manuais
surgiram no Run 002–003; ainda não há EXE v2 do jogo.

O objetivo da v2 é recuperar o jogo integralmente a partir dos binários, obter código-fonte
compilável e comportamento original, e então portar as dependências de plataforma.
O primeiro resultado executável deve ser o original Windows/x86 a partir do
código restaurado. Rust/wgpu da versão anterior não definem a nova arquitetura.

Exemplo de processo — [SpaceRangersHD_decomp](https://github.com/pakompom/SpaceRangersHD_decomp):
código-fonte recuperado, conjunto fixo de ferramentas de compilação,
verificação de funções e EXE final. Seu autor relata correspondência completa de
SHA do Rangers.exe; para Porsche essa correspondência ainda não foi alcançada.
O método e as sutilezas do conjunto de ferramentas são descritos em
[development.md](https://github.com/pakompom/SpaceRangersHD_decomp/blob/main/docs/development.md).

Localização:

- `iterations/v2/001-original-recovery`: plano, manifesto de entrada, código-fonte
  manual `source/`, verificações e próprios `runs/`, começando em 001.
- `research/v2/binaries`: listagem completa de cada módulo, pseudo-C automático,
  resultados de todas as funções e regiões explicitamente não reconhecidas.
- `local/builds/v2/001-original-recovery`: biblioteca C++ x86 separada e
  sondas de verificação em console; EXE do jogo ainda ausente.
- `local/experiments/v2-*`: experimentos modificáveis e bases adicionais do Ghidra.

O índice existente cobre 24 PEs exclusivos. Na v2 também são considerados
o NE de 16 bits `clcd16.dll`, aliases, drivers, instaladores e patches; sua relação
com a compilação do jogo é estabelecida separadamente. Nenhum módulo desconhecido desaparece
do relatório. Cobertura/hashes: [reference/binaries.json](reference/binaries.json).

Os estágios de recuperação se diferenciam: exportação completa do código encontrado,
descompilação automática, fonte compilável manual, função correspondente,
módulo correspondente. O `decompiled.c` automático contém hipóteses do Ghidra sobre
tipos/assinaturas e não é um projeto C/C++ pronto. Bytes não reconhecidos,
chamadas indiretas, erros/timeouts permanecem em uma lista mensurável de trabalho.

O Porsche.exe possui a versão 6.0 do vinculador PE (PE linker version 6.0); a string `Microsoft Visual C++ Runtime
Library` localiza-se no VA 0x5c1e5c. Estas são evidências para testar a cadeia de ferramentas
(toolchain) da era MSVC, e não prova do compilador/flags/bibliotecas exatos.
Verificar compilações de teste reais e código de máquina antes de escolher o conjunto de ferramentas.

Primeiro compilamos e verificamos a linha de base Windows/x86. O objetivo de correspondência total
não é alcançado através de pós-processamento do EXE, cópia de funções originais para
o resultado ou stubs de lógica de jogo desconhecida. Quando os componentes do jogo
forem recuperados, uma etapa separada adaptará gráficos, som, entrada e SO para native/web.
Fontes anteriores verificadas e bancadas de replay são usadas como evidências;
implementações arcade não são migradas automaticamente.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/research/export-v2.ps1 -Mode listing
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/research/export-v2.ps1 -Mode listing -ImportNE
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/research/export-v2.ps1 -Mode decompile
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/research/export-v2.ps1 -Mode decompile -NE
py -3 scripts/research/inventory-v2.py --require-listing --require-decompile-attempts
py -3 scripts/research/inventory-v2.py --require-listing --require-decompile-attempts --write-verification
```

O NE encontra-se em um projeto separado; a listagem repetida utiliza `-NE` em vez de
`-ImportNE`. Primeiro critério de aceitação do 001: todos os SHAs de entrada contabilizados,
todo o código descoberto exportado, cada função encontrada tentada pelo
descompilador, erros/regiões indefinidas listados. Isso ainda não é uma reconstrução
completa do jogo.

Run 002: o usuário optou diretamente por C/C++, sem compilação intermediária em assembly.
Criada a [árvore de fontes](source/README.md) com catálogo de endereços
de todas as funções e módulos C++ manuais. O salto 0x4b6710 compila e coincidiu
com x86 em 175 casos; o callee 0x4b6a50 é apenas registrado na bancada, não restaurado.
O MSVC 19.44.35229 moderno compila Win32/x86; a versão original exata
não foi confirmada. [Relatório](runs/002-cpp-startup/README.md),
[grafo de inicialização](reference/startup.json). 1 função manual verificada,
0 correspondências de bytes/módulos inteiros. Ainda sem execução do jogo.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-v2.ps1
py -3 scripts/research/verify-v2-startup.py
py -3 scripts/research/structure-v2.py
py -3 scripts/research/trace-v2-startup.py
```

[Run 003](runs/003-fe-stream/README.md): recuperado um trecho integral
fe.txt/linha de comando → fluxo FE → execução de registros: nove novas funções C++,
tabelas de comandos/valores/ações e palavras globais originais. 236 comparações
native/x86 passaram, fe.txt real produz 23 registros / 188 bytes. No total, dez
funções manuais verificadas; contagem de correspondências de bytes e módulos inteiros — zero.
Callees de IO/heap/callback ainda não recuperados: são substituídos por registro apenas na
bancada. Registro geral — source/recovered/functions.json.

```powershell
py -3 scripts/research/export-v2-fe-tables.py
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-v2.ps1
py -3 scripts/research/verify-v2-fe-stream.py
py -3 scripts/research/inventory-v2.py --require-listing --require-decompile-attempts
py -3 scripts/research/structure-v2.py
py -3 scripts/research/inventory-v2.py --require-listing --require-decompile-attempts --write-verification --verification-output iterations/v2/001-original-recovery/runs/003-fe-stream/corpus-verification.json
```

[Run 004](runs/004-original-heap/README.md): recuperadas 11 funções da heap proprietária:
criação, alocação a partir de duas extremidades, seleção do maior bloco adequado,
free com mesclagem, resize sem movimentar ponteiro e auxiliares. Todos os 551 casos
coincidiram com o x86 original em toda a arena após cada operação. ABI de free
refinada (retorno 1), 236 regressões de FE repetidas na nova run; relatórios antigos preservados.
No total, 21 funções manuais verificadas, 0 correspondências de bytes/módulos inteiros.
Copiadores otimizados/SO/CRT continuam sendo dependências externas.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-v2.ps1
py -3 scripts/research/verify-v2-heap.py
py -3 scripts/research/verify-v2-fe-stream.py --report-dir iterations/v2/001-original-recovery/runs/004-original-heap/fe-regression
```

[Run 005](runs/005-original-files/README.md): recuperadas 29 funções
de filas de arquivos, conclusão/status, leitura em blocos e listas. Todas as 89
verificações conjuntas FE/heap/IO com x86 passaram, incluindo fe.txt real;
551 regressões de heap e 236 de FE preservadas na nova run. No total, 50 funções
manuais verificadas. Índice SHA adicional contém 3 callbacks omitidos:
catálogo de 36 587 automáticos + 3 suplementares = 36 590 registros.
Disco/thread/VirtualAlloc/SO/CRT permanecem fronteiras externas; sem EXE do jogo.

[Run 006](runs/006-file-device/README.md): mais 6 funções de invólucros de página (page wrappers),
construtores de listas / chave padrão / inicialização de dispositivo verificados em 474 casos com x86.
89 verificações conjuntas repetidas com page wrappers reais; no total 56 funções.
Catálogo de 36 587 automáticos + 5 suplementares = 36 592 registros.
Worker 0x568530 indexado, mas ainda não recuperado.

Próximo pacote — worker/controle/conclusão, thread/espera/eventos e despacho de disco/arquivo,
depois vinculação com a inicialização em 0x4b6a50.
Endereços exatos e o primeiro passo — [no plano](PLAN.md).
