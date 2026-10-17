# Estado do Projeto

Ponto de controle (checkpoint) 2026-10-17, Run274: **1125 candidate function VAs + 19 support objects**,
1144 membros de arquivo / 1 299 024 bytes. Link real **414 names / 566 diagnostics**, sem EXE/DLL.
Vinculados heap free canônico + binding bruto + travas Win32 reais + um proprietário de tabela compartilhada de 64 B.
1125 game candidate VAs não incluem 2 adaptadores de plataforma modernos (support). Produção verificada
Run173: 476 full + 6 partial sem alterações. 7626 pins PASS / 1142 símbolos em cache / 2 novos COFFs,
0 compilações / um archive-link 8.827s. Código-fonte / arquivo / diagnósticos reais — runs/274.

266: 10 chamadores COFF reais de free bruto / RET0 cdecl DWORD completo, EAX 1 / identidade nativa PASS.
268: 2 adaptadores Win32 existentes, 64 ciclos reais de trava recursiva / 256 chamadas, 204 pins / 8 guardas PASS.
267/270/271: 56 746 HIGHLOW / 30 refs + 4 intervalos de candidatos 510 B / 167 instruções recuperados;
novo índice de navegação 15 pins / 7 guardas PASS, entrada/vivacidade não comprovadas, índices antigos intocados.
272: apenas ARMAZENAMENTO (STORAGE-only) 64 B / declaração canônica exata + visão indexada de 16 slots bruta compartilham uma base;
3 locais DIR32 brutos reais delimitados AND 0f / MEM4, zero / gravações cruzadas / cópia de bits / auditoria nativa PASS.
Comprovação de pegada de dados independente de vivacidade de função candidata não comprovada; essas funções
não estão implementadas/aceitas. Precedente 006b4b20..006b4f1f ponteiro final / layout relativo permanece em ESPERA (HOLD).
275: 414 nomes reais -> 412 tarefas de pesquisa, 24 linhas resolvidas excluídas; 159 pins / 6 guardas PASS.
Cadeias CALL originais 258: 36 864 casos nativos; CPU sintética 262: 15 744 casos PASS;
260 sintaxe 25/85, não é aceitação semântica. Retenções de 595d0 MOVSX / layout 5a4c05 continuam.

Pacotes 257–275 concluídos, sem atribuições ativas. Próximo pacote conectado delimitado:
files.cpp aceito operation_queue 00568200 + operation_allocate 005682a0 (ranks 2/3 em 275),
pré-validação da ABI do consumidor original antes da reutilização de fragmento exato. Quatro chamadores compartilhados 568ae0/b10/b50/b90
também usam o handle_device inseguro de char 595d0; recuperar contrato de consumidor em EAX completo em vez de
alias por adivinhação. Agrupar fixtures/provedores nativos em lote em um compile/link, manter estado explícito de FILE/dispositivo/fila.
Próximo no backend em paralelo: MOVSX/OR/condições conforme 260; apenas semântica de instrução comprovada nativamente.
CPU completa / carregador / importações / bootstrap / falhas / concorrência / lançamento do jogo e backlog abertos.
Comandos: audit-v2-native-platform-268.py, index-v2-heap-candidates-271.py --validate,
audit-v2-shared-heap-table-272.py; união real — runs/274/command.json (coletor 268).

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

Resultado atual — [Run173](iterations/v2/001-original-recovery/runs/173-float-transport-integration/README.md): **476 funções C++ verificadas** e 6 consumidores parciais registrados.
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

2026-10-14: 173 publicado 6952020. 177 corpo C++ direto 004d3420 compila
com costuras externas abertas; 178 concluído 707/5772 aprovação de sintaxe C++.
179 exporta declarações/tipos completos; 180 corrige auxiliares de p-code de inteiros exatos;
181 constrói COFFs reais a partir de candidatos. Estes são experimentos isolados,
a contagem de funções aceitas e o game-link de produção permanecem 173; sem EXE de jogo.
Verificações em lotes, não repetir a baseline 178 inalterada.

2026-10-08: ativa [v2/001-original-recovery](iterations/v2/001-original-recovery/README.pt-BR.md).
v1 preservada e enviada: dc6b9d8; 012 incompleta e sua integração foi interrompida.
Listagens completas de 24 PE + 1 NE exportadas: 36 587 funções, 2 827 310 instruções.
Fronteiras de código/dados/preenchimento não reconhecidos contabilizadas (3 199 385 bytes);
estes não são fontes prontos. Todas as funções tentadas pelo descompilador: 36 583 pseudo-C,
4 falhas/timeouts, 5639 funções com avisos. Porsche.exe principal:
5772/5772 pseudo-C, sem falhas/timeouts. A verificação do inventário completo passou.
Diretamente C/C++ por escolha do usuário: catálogo de endereços de todo o corpus,
porsche_original.lib e bancadas de console separadas (Windows x86).
Run 002: inicialização 0x4b6710 verificada em 175 casos. Run 003: 9 funções de leitura
de fe.txt/argumentos, criação e aplicação de fluxo FE verificadas em 236 casos.
Foram comparados registros, campos globais, callbacks e a ordem de chamadas de arquivo/heap;
serviços externos — limites de gravação da bancada, chamadas ainda não recuperadas.
fe.txt real produz 23 registros / 188 bytes. Run 004: 11 novas funções C++
de inicialização/alocação/liberação/redimensionamento da heap e auxiliares; 551 casos coincidiram com x86 em toda a arena
após cada operação. 236 regressões repetidas de FE passaram; free retorna 1.
Run 005: 29 funções de fila de arquivos/conclusão/leitura em blocos e listas;
89 comparações conjuntas FE/heap/IO com x86 passaram. 551 regressões de heap e 236 de FE
repetidas na nova run. Total de 50 funções manuais verificadas; a biblioteca
contém o frontend real de FE/heap/IO. Disco/threads/VirtualAlloc/SO/CRT/SIMD
ainda externos; na bancada a conclusão é imediata, não é o agendador original.
Três callbacks omitidos adicionados ao índice protegido por SHA: catálogo de 36 590 registros,
sendo 36 587 automáticos. 0 correspondências de bytes/módulos; sem EXE v2 do jogo.
MSVC 19.44.35229 disponível; compilador/CRT/flags originais exatos não confirmados.
Worker/threads/espera/eventos e backend de disco/arquivo em aberto; após eles, comparação
conjunta com o agendador original e inicialização 0x4b6a50.
Run 006: 6 novas funções C++ de inicialização de página/lista/dispositivo, 474 comparações com x86
e 89 regressões conjuntas passaram. Invólucros de página reais incluídos em FE/heap/IO;
APIs Win32 continuam como fronteiras de gravação. Total de 56 funções verificadas,
catálogo de 36 592 registros (5 suplementares). Worker 0x568530 indexado,
seu loop/threads/espera/eventos/disco ainda em aberto. Em seguida tabela de saltos/despacho do worker.
Relatório: runs/006-file-device dentro de v2/001. Aceitação visual aberta.
Caminhos: iterations/v2/001-original-recovery, research/v2/binaries,
local/builds/v2/001-original-recovery. Executor — coordenador.

2026-10-08: o usuário solicitou commitar o estado atual e migrar
para uma v2 separada com recuperação total dos binários. 012 permanece inacabada.
Run 020: 47 loops originais de quatro rodas / 188 estados coincidiram com Rust.
221 testes (3 ignorados), fmt/clippy/wasm32/nativo/web e 3 Quick Race passaram.
Execução geral no navegador do Run 020 não concluída; adaptador de força/binding abertos.
Run 019 enviado (pushed): 13b70f1. Alterações de jogabilidade adicionais na 012 foram interrompidas.

Run 019, 2026-10-06: árvore geral de polígonos+EDG e suporte de rodas funcionam no jogo.
3 árvores / 27 consultas EDG, 8 seleções de carroceria, 45 respostas dependentes de cena,
5 casos de altura / 29 de estado de material coincidiram com x86. 220 testes (3 ignorados),
fmt/clippy/wasm32, nativo/web, 3 Quick Race e 21 verificações no navegador passaram.
APIs de carroceria/roda ainda não substituem o adaptador de força. Restante: campos originais,
0x499a70 completo / cadência, special/carro-carro, UI/missão/aceitação visual.
012 aberta, sem executores ativos; o coordenador concluiu o código parcial
após o limite do worker. Execução: local/builds/012-campaign-fidelity/Launch-desktop.cmd.

Run 018 dentro da 012, 2026-10-06: suportes tipo 1 recuperados conectados
ao carregamento real de pistas e às quatro rodas. Filtro Ordinary Base, carregador retido de
flag 1, mt/vt/df/pr, árvore, dois caches e consulta de plano funcionam na corrida;
eliminação de seleção de RD* e Skidpad mt53/54. Em 15 pistas, 237 395 polígonos.
9 casos de carregador / 10 de proprietário coincidiram com x86; 215 testes em Rust passaram (3 ignorados),
fmt/clippy workspace -D warnings, wasm32 e release nativo+web passaram.
Quick Race Skidpad/Alps/Canyon: caches reais de quatro rodas, carga, movimento,
altura verificados; 21 verificações gerais de navegador passaram. Relatório/comandos/quadros:
runs/018-original-support-runtime. Execução: local/builds/012-campaign-fidelity/Launch-desktop.cmd.
Forças de suspensão e resposta do corpo permanecem no adaptador anterior; kernel de contato preparado
não conectado. Tipo 2/caixa/cilindro na árvore geral, ordinal Base mutável e
estado/forças completos de roda originais permanecem inacabados; 012 aberta.
Atribuições de executores concluídas. Próximo passo concreto do coordenador:
cena mista → estado original 0x499a70 / consumidores de altura alternativa/força →
geometria 0x495020 e resposta 0x494000. Comparação da pilotagem real com o original é obrigatória.

Run 017 dentro da 012, 2026-10-05: inserção/divisão original de tipo 1 e consulta
de suporte em cache unidas em módulo Rust separado. 38 casos de callback / 304 de predicado,
36 árvores completas e 72 consultas completas coincidiram com x86 original. Código original de
alocador/vetores executado na arena especificada; travas Win32 — thread único.
20 testes em Rust, fmt/clippy -D warnings e wasm32 passaram. Fonte/comandos —
runs/017-original-support-insertion. Runtime fa56d05, 012 aberta.
Encontrado produtor special: animdefs.txt → 0x47eba0 → 0x628ba0; 0x47ed90 em
tag Base não nula desconhecida retorna o primeiro ENDW/kBox, e não null.
Em seguida coordenador: carregador completo de polígonos 0x475543..0x47591e, busca/analisador
de special original e produtor ordinal Base, depois estado/cadência do veículo.
Objetivo de conexão na 012 — primeira pista com suportes e contato originais.

Run 016 dentro da 012, 2026-10-05: leitores Base/pr e construtor filho da árvore
migrados de consumidores originais para módulos Rust separados. 317 casos de payload primitivo /
2536 saídas auxiliares, 60 Base e 256 casos de filho comparados com x86.
Rust verificou independentemente 15 pistas: 74 300 pr / 16 591 Base. 16 testes, fmt/clippy -D warnings
e verificação wasm32 passaram; fonte/comandos — runs/016-original-support-assembly.
Executor de inserção interrompido por limite; exportação de fonte preservada, construtor
filho concluído pelo coordenador. Nenhuma atribuição ativa. Compilação fa56d05,
012 aberta; novos módulos por enquanto fora do loop do jogo. Em seguida coordenador:
0x484320 + callbacks vtable+4/+8 de tipo 1 → repetição de inserção; depois carregador completo
(produtor ordinal / special / alternativo / degenerescência) e conexão com estado/cadência do carro.

Run 015 dentro da 012, 2026-10-05: flags de material = payload mt+0 comprovados;
208 casos de material x86 e 10 casos de plano/lacuna verificados, migrados para pure Rust.
Rust verificou independentemente 15 pistas / 3651 entradas mt; 11 testes, fmt/clippy
e verificação wasm32 passaram. Fonte/comandos — runs/015-original-support-loader.
Executores concluíram o trabalho. Runtime por enquanto o anterior (fa56d05), 012 aberta.
Em seguida coordenador: seleção Base/pr/vt em 0x4750b0, inserção 0x484ae0/483bd0,
depois cena → estado do veículo e cadência original; não conectar aproximações.

Run 014 dentro da 012, 2026-10-05: limites espaciais / travessia / cache originais
migrados para pure Rust. 572 resultados coincidiram com a execução do x86 original;
sete testes em Rust, fmt/clippy e verificação wasm32 passaram. Fonte/fixações — Run 014.
Caminho proprietário → flags de material estabelecido; deslocamento mt bruto ainda desconhecido.
Runtime não conectado, compilação fa56d05.
Próximo passo: vinculação de flags brutos, carregador de plano/divisão, construção de árvore
e ligação com o estado do veículo. Executores concluíram o trabalho.

2026-10-05, Run 013 dentro da 012: predicados originais de polígonos de suporte e seleção em
folha pronta migrados para Rust. 36+10 resultados comparados com o x86 original;
10 casos de divisão quadrática (quad-split) também executados. Três testes em Rust (incluindo 468 contatos),
fmt/clippy e verificação wasm32 passaram. Seleção/carregamento de folha de cena ainda não conectados.
Rastreada a origem de timer 128 / contadores derivados de 64Hz; cadência de integração permanece aberta.
[Run 013](iterations/012-campaign-fidelity/runs/013-original-support-query/README.md).

2026-10-05, Run 012: reação original de contato preparado migrada
para módulo Rust separado; 468 estados coincidiram com a execução do x86 original.
Recuperados o ramo de rotação, seu campo Y e a geometria de pontos/normal. 103 testes
de nfs-assets, fmt/clippy e verificação wasm32 passaram. Ainda não conectado ao loop do jogo:
necessários a consulta completa da cena e a cadência do integrador original. Compilação permanece fa56d05.
[Relatório e comandos](iterations/012-campaign-fidelity/runs/012-original-contact-kernel/README.md).

2026-10-04, Run 011: o usuário optou pela restauração do original em vez
da aproximação por implementações semelhantes em todos os subsistemas, inclusive no código existente.
Sweep preservado separadamente e removido do runtime; não entrou no release.
Última compilação/commit do jogo — fa56d05. 012 aberta: física/UI/missões
ainda exigem consumidores originais e aceitação. 013 (danos + mercado de usados)
ainda é apenas um plano. Regras consolidadas em AGENTS.md e .cursor/rules.

2026-10-05: comprovada a cadeia EDG → consulta espacial → 0x494000.
64 casos diferenciais do trecho de reação passaram em instruções x86 originais
no Unicorn; geometria definida por fixação, callback angular desativado. Resultados:
[análise da reação](iterations/012-campaign-fidelity/research/original-collision/response.md).
Código do jogo não foi alterado; em seguida reação angular e contrato completo de contato.

2026-10-04: o usuário confirmou a conclusão da primeira missão da Factory, mas
"Continuar" reabre o resultado repetidamente. Run 010 corrige o ciclo de vida do JS;
regressão de UI e cinco testes em Rust da Factory passaram. Windows/WASM compilados.
Chromium: Continuar → lista → 1m01 → início real, salvamento após recarregamento,
falha/repetição sem loop, 0 erros de JS. Linha de chegada definida por fixação de teste;
conclusão da 1m01 não é declarada. Corrigido seu SIM: boxster.sim (ausente) → boxster25.sim.


Atualizado em 2026-10-03. Ativa **012-campaign-fidelity** a partir da 011 concluída.
Plano atual: [iterations/012-campaign-fidelity/PLAN.md](iterations/012-campaign-fidelity/PLAN.md).

## Ativa 012: correção da conformidade com o original
Run 008: pivôs de roda / raios / grupos de malha reais do CRP conectados à física
e ao renderizador. Funcionam rotação/esterçamento de rodas, curso de suspensão do jogador, contato da carroceria
com a pista e colisões jogador/IA/IA. CPU: 184 passaram; Windows/WASM compilados.
Chromium: 21/21 verificações gerais, pivôs de roda/animação e colisão em Quick Race
passaram; ambas as corridas da 0M01 — 5/6 pontos sem capotar, depois timeout. Commit 9efb71c.
Run 009: índice versionado do original pronto em `research/binary-index/`:
25 caminhos PE / 24 binários únicos, 36 510 funções e 1 274 749 referências.
Biblioteca NE clcd16.dll explicitamente não coberta; completude de semântica e chamadas indiretas não são reivindicadas.
Regra de consulta ao índice antes da implementação fixada em AGENTS.md e .cursor/rules.
Ponto de controle intermediário publicado anteriormente: cb07500.
Ponto de controle publicado anteriormente a pedido do usuário:
[Run 007](iterations/012-campaign-fidelity/runs/007-publish-checkpoint/README.md).
Quick Race, SIM original, gatilhos/setas SCN e correções de superfície compilados;
conclusão completa da 0M01 e física original NÃO foram aceitas. Próximo resultado —
uma missão do início ao quadro final correto com commits curtos.

Ponto de controle atual 2026-09-29: corrigidos o sinal invertido da barra estabilizadora e a geometria
do raio da suspensão; 172 testes em Rust passaram, 3 testes de GPU ignorados, Clippy/fmt limpos,
Windows/WASM compilados. A corrida completa attempt-5 continua capotando após o
2º ponto; não há colisão da carroceria com o solo. Encontrada interpretação não confirmada
de SIM 0x10c/0x110 como bitola: o runtime do Boxster recebe 1 m forçado.
Próxima prioridade — consumidores de EXE e fonte da geometria das rodas, depois repetição
da missão e fluxo de resultado/penalidade. Detalhes e todas as tentativas — no Run 006 abaixo.

Pontos de controle anteriores Run 006:
Run 006: corrigida a queda após o primeiro ponto — conectados todos os setores originais
Skidpad mt53/mt54 em vez de apenas MESH04; excluído o edifício homônimo.
169 testes em Rust passaram, 3 testes de GPU ignorados; Clippy/fmt limpos, Windows/WASM compilados.
A repetição real passou por 4/6 pontos sem queda e sem erros de JS, sofrendo timeout na
curva; o perfil não foi alterado. Conclusão completa ainda não confirmada.
A seguir — telemetria da curva (controle/física), depois fluxo de resultado/penalidade.
Attempt-3: carroceria capota (up.y chega a -1). Descoberto e corrigido sinal invertido
das forças da barra estabilizadora; teste antes da correção reproduz momento que acentua a inclinação lateral.
Verificação da correção em corrida completa ainda em andamento.
2026-09-29: attempt-4 continua capotando. Corrigida a causa seguinte:
distância incorreta ao solo e contato falso de rodas capotadas. Novo raycast
de suspensão é verificado em triângulos finais, inclinação e limites de células de grade.
[Run 006](iterations/012-campaign-fidelity/runs/006-mission-playthrough/README.md).

Run 005 verificado em 2026-09-28: runtime utiliza predicado shape1 recuperado —
diagonais da carroceria, faixa de altura, restrições de direção/velocidade originais, término baseado em tipo.
169 testes em Rust passaram, 3 testes de GPU ignorados; Clippy/fmt/UI limpos; Windows/WASM compilados;
Chromium 21 verificações, 0 erros / falhas conhecidas. Ativação do primeiro ponto pela carroceria,
contagem de portões e reinício verificados com entrada real W/R; quadro após o ponto inspecionado.
Dimensões obtidas do modelo visível, pose/velocidade do sim; limites selecionados /
origem da carroceria / correção de contato originais exatos ainda não comprovados. Conclusão completa da 0M01,
penalidades/resultados e UI 1:1 em aberto. Sem atribuições ativas, agentes pararam por cota.
[Run 005](iterations/012-campaign-fidelity/runs/005-trigger-contract/README.md).

Run 004: referências acionáveis de animdefs.txt e referências ordenadas de SCN conectadas ao runtime.
Pela cadeia de reset recuperada, Start seleciona Arrow 1, a passagem pelo primeiro trigger
alterna para Arrow 2, a repetição retorna para Arrow 1. L A permanece oculta; quadro inicial
inspecionado, obstrução de câmera eliminada. 166 testes em Rust passaram, 3 testes de GPU ignorados;
Clippy/fmt/UI limpos, Windows/WASM compilados; Chromium 21 verificações, 0 erros / falhas conhecidas.
Condições originais de aprovação, spawn/câmera e UI 1:1 ainda não comprovados.
[Run 004](iterations/012-campaign-fidelity/runs/004-scenario-arrows/README.md).
Sem atribuições para agentes. Os registros seguintes são o histórico de verificações de runs anteriores.

Run 003: corrigida alternância numérica de sinal de ômega por frenagem em physics/tire.rs.
Antes da correção, 2/4 repetições de cenário não retornavam de R; depois — 8/8 passaram.
Conectada escala SCN v4: 162 testes em Rust passaram, 3 testes de GPU ignorados; Clippy/fmt/UI limpos,
Windows/WASM compilados. Chromium: 20 verificações passaram, 0 erros, 0 falhas conhecidas.
Quadro da 0M01 inspecionado: L A / ARW1 continua obstruindo a câmera. Recuperada cadeia de
animdefs.txt triggerable → ocultação inicial → seleção vinculada a trigger; no runtime ela
ainda não está conectada, a primeira ativação exige reversão adicional. Sem atribuições para agentes.
[Run 003](iterations/012-campaign-fidelity/runs/003-factory-diagnostics/README.md).
Run 001/002 abaixo mantêm pontos de controle históricos, incluindo falha já corrigida.

- Observações do usuário: interface estranha, visual misturado de carreiras, Factory Driver /
  início de missões incorretos, carros decolando, ausência de marcha à ré após frear em S.
- Checkpoint 2026-09-26: T01–T04 parcialmente concluídos, iteração permanece aberta.
  Corrigidos primeiro contato, piso fictício, braços de eixos e S freio→parada→marcha à ré (W simétrico).
  Calibração em SIM reais: 356 — 54.7 m, Boxster — 43.3 m de 100 km/h, sem capotamento.
  Para a 0M01 adicionados SCN Start, suporte MESH04 e waypoint 1–5→End; volta geral LSP não concede mais
  vitória na Factory, cenários não suportados não recebem recompensa. Regras por enquanto reconstruídas.
- 151 testes em Rust passaram, 3 testes de GPU ignorados; testes Clippy/fmt/UI limpos. Release Windows/WASM compilados.
  Chromium: 14 verificações automáticas, 0 erros, incluindo volante e retenção de S/W; veja
  [Run 001](iterations/012-campaign-fidelity/runs/001-fidelity-repair/README.md).
- Aceitação visual NÃO foi atingida: no quadro da 0M01 a câmera está obstruída pela geometria. Deslocamento exato de spawn,
  regras do original, UI 1:1 (salas/fontes/camadas) e corrida real ainda não confirmados.
  Na continuação do Run 002 foi adicionado o carregamento de SIM no web runtime, verificação de arquivos corrompidos
  e corrigida a referência do Boxster para `boxster25` conforme nfs5.car. CLI nativo por enquanto usa tabelas.
- Run 002: adicionado Quick Race com seleção de pista/carro, 1/3/5 voltas e 0/3 IA,
  sem recompensas de carreira. Windows/WASM compilados, 157 testes em Rust passaram, 3 testes de GPU ignorados;
  Clippy/UI limpos. Chromium final: 19 verificações passaram, 0 erros de JS e 1 falha conhecida
  (R→frente instável do Boxster na 0M01). Quick Race S/W passa; verificador geral não está verde.
- Corrigidos o sinal de curva da IA cinemática e o lookahead de sprint. Auditoria de 15 pistas agora
  mede o progresso ao longo do trajeto: antes verificava-se distância >50 m do trajeto, de modo que o
  pass anterior não comprovava o seguimento da rota. Auditoria corrigida passou. Tabelas AIS/AI,
  linha de chegada de sprint e formação original de participantes da campanha continuam abertos.
- UI separa as carreiras e segue parcialmente LAY 640x480. Extração de 119 PNGs reproduzível via
  `scripts/extract-fe-ui.ps1` em `local/derived/fe-ui`. Repetição de
  [Computer Use](docs/computer-use-recovery.pt-BR.md): `sky.list_apps()` → `spawn EPERM`.
  Sem atribuições para agentes; resultados e comandos — [Run 002](iterations/012-campaign-fidelity/runs/002-runtime-sim/README.md).
- Snapshots 001–011 inalterados. Relatórios anteriores abaixo são histórico de testes, não prova
  de total fidelidade com o original; conformidade da 011 contestada pelas observações do usuário.
- Áudio/cockpit adiados até correções de carreiras e controle.

Porte completo com ambas as carreiras: [roadmap](docs/roadmap.pt-BR.md).

## Iteração concluída: 011-factory-driver
- [Run 001](iterations/011-factory-driver/runs/001-factory-driver/README.md):
  - T01: engenharia reversa binária de todas as 34 missões de `nfs5.fac` e base de idioma `festrings.csv`.
  - T02: motor de desafios `factory_driver.rs` em `crates/nfs-game`: detectores de manobras `StuntDetector` (slide 180°, spin 360°, reverse J-turn, penalidades de slalom, controle de danos à carroceria).
  - T03: sistema de evolução de carreira do piloto (Applicant -> Junior Test Driver -> Test Driver -> Senior Test Driver -> Chief Test Driver -> Master Ace) e carros de recompensa ('78 911 Turbo 3.3, '73 Carrera RS 2.7, '99 911 GT3 Factory Edition).
  - T04: janela modal `#factoryMissionsModal` com filtros de níveis de dificuldade Tier 1–3, falas do instrutor-chefe Rolf, status e melhores tempos.
  - T05: eliminação de defeitos de campanha e autenticidade de interface:
    - Shell de jogo autêntico de Need for Speed: Porsche Unleashed (2000) baseado nos layouts `bottombar.lay`, `singleplayer.lay`, `factorydriver.lay`: shell em tela cheia, cabeçalho de marca superior PORSCHE, barra de status com saldo CR e patente, coluna esquerda de botões rubi em pílula `.nfs-pill-btn`, painel inferior com botão ESC e botão oval iluminado RACE (`racebutton.fsh`).
    - Tela autêntica de briefing de missões (`missionbrief.lay`): foto real de Rolf (`people_rolp.png`), plantas técnicas das tarefas (`map_*.png`, 34 esquemas) com disposição de cones e setas.
    - Painel redondo de instrumentos autêntico da Porsche na corrida (`hud.fsh`): tacômetro analógico com redline (6.5–8k) e ponteiro, velocímetro digital âmbar (km/h) e indicador de marcha.
    - Eliminação do erro de compra de carros (`missing or invalid 'version'`).
    - Carregamento de modelos 3D reais da Porsche (`.crp`/`.fsh`) e parâmetros de simulação nas tarefas do modo história em vez de stub em caixa.
    - Correção da escala 1:1 (x5.0) e rotação de 180° do modelo para frente no sentido da pista.
    - Correção da pista Canyon e do assentamento do carro no solo a partir da largada do Evolution.
  - T06: 142 testes em Rust passaram por todo o workspace, Clippy `-D warnings` limpo, Rustfmt limpo, Playwright Chromium E2E (12/12 verificações, 0 erros), compilação release nativa e WASM.
- Tarefas T01–T06 concluídas, tag `iteration-011`.

## Iteração concluída: 010-evolution-career
- [Run 001](iterations/010-evolution-career/runs/001-evolution-career/README.md):
  - T01: engenharia reversa binária de torneios (`nfs5.trn`), peças de reposição (`nfs5.prt`), preços e desgaste.
  - T02: motor de torneios Evolution com eras (Classic, Golden, Modern), sistema de pontuação (10-6-4-3-2-1), progressão de etapas e premiações.
  - T03: concessionária de carros novos e mercado de usados (B/U) com quilometragem dinâmica e valor residual.
  - T04: catálogo de peças e tuning, impacto na física, desgaste de componentes e procedimento de reparo.
  - T05: teste de estresse completo da física em todas as 15 pistas: 0 ocorrências de tunelamento em velocidades de até 252 km/h, verificação do asfalto e retenção.
  - T06: integração de UI, 138 testes em Rust passaram, clippy `-D warnings` limpo, fmt limpo, Playwright Chromium E2E (0 erros), compilação nativa e WASM.
- Tarefas T01–T06 concluídas. Scripts documentados em `docs/scripts.pt-BR.md`.

## Resultado verificado

### 009-game-shell
- [Run 001](iterations/009-game-shell/runs/001-controls-regression/README.md):
  - T00: correção da inversão de direção na física 6 DOF (`vehicle.rs`), ângulo negativo para curva à direita das rodas no sentido -Z.
  - Bancada de regressão: reprodução do bug antes da correção, 21 testes de `porsche-viewer` verdes, verificações de entrada web, teste Playwright de sinal de proa.
- [Run 002](iterations/009-game-shell/runs/002-game-shell/README.md):
  - T01: crate independente `crates/nfs-game`, máquina de telas arquitetural `Screen`, tratamento idempotente de resultados e proteção contra condições de corrida no carregamento.
  - T02: perfil de jogador `PlayerProfile` (11 000 CR, garagem, patentes), salvamento atômico `.tmp` -> renomeação no disco, `localStorage` e importação/exportação JSON na Web.
  - T03: pesquisa binária de `nfs5.trn` e `nfs5.fac`, analisadores de torneios e missões em `nfs-formats/src/career.rs`, relatório [`research/first-events-evidence.md`](iterations/009-game-shell/research/first-events-evidence.md).
  - T04: execução de ponta a ponta dos primeiros eventos de carreira: Evolution 356 Challenge (Canyon, Monaco 1; taxa de inscrição 2 000 CR, prêmio 4 500 CR) e Factory Driver 0M01 (Skidpad, Boxster, limite 32.0 s).
  - T05: áudio básico: sintetizador WebAudio (RPM, guincho de pneus, sinais de contagem/finalização) e beeper WinMM para nativo; janelas modais de briefing, perfil e resultados.
  - 129 testes em Rust passaram, clippy `-D warnings` e fmt limpos, release nativo/WASM compilados, 10 verificações no Chromium WebGPU aprovadas.
- Tarefas T00–T05 concluídas, código commitado, tag `iteration-009`.

### 008-race-loop
- [Run 001](iterations/008-race-loop/runs/001-race-loop/README.md):
  - T01: máquina de estados finitos da corrida (`RaceSession`): estados `Loading`, `Countdown(3..2..1..GO)`, `Racing`, `Paused`, `Finished`, `Results`, cronômetros, tempo de volta, melhor volta (`best_lap`), deltas de parciais.
  - T02: roteamento e checkpoints (`TrackCourse`): engenharia reversa do formato binário da EA Canada `.lsp` (Line Spline Path), 30 arquivos de pistas validados com 100% de sucesso, classificação automática em circuito/sprint (limiar de gap < 60m), portais de checkpoints com proteção contra atalhos, detecção de contramão («Wrong Way»).
  - T03: colisões com barreiras (`BarrierCollider`): rebote nas bordas da pista `.edg` com coeficiente de restituição 0.35 e atrito tangencial 0.75, prevenindo escape dos limites da pista.
  - T04: oponentes com IA e grid de largada (`AiOpponent`): seguimento de trajetória com perseguição pura (pure pursuit) e adaptação de velocidade à curvatura $v = \sqrt{a_{lat}/\kappa}$, perfis baseados em `.ais`, grid de largada em xadrez de até 8 carros, tabela de posições em tempo real por distância percorrida.
  - T05: HUD de corrida e tela de resultados: indicador de posição (P1/4), contador de voltas (Lap 1/3), cronômetro, temporizador da melhor volta, banner pulsante de contagem regressiva, aviso Wrong Way, modal de término na Web e telemetria no título da janela nativa.
  - T06: teste de integração de ponta a ponta (`tests/race_integration.rs`): 115/115 testes passaram; `fmt` e `clippy -- -D warnings` limpos; compilação release completa nativa e WASM.
- Tarefas T01–T06 concluídas, código commitado, tag `iteration-008`.

### 007-physics-simulation
- [Run 001](iterations/007-physics-simulation/runs/001-physics-simulation/README.md):
  - T01: dinâmica de Corpo Rígido 6 DOF (`rigid_body.rs`): massa, momentos de inércia, quatérnion de orientação, transformações locais/globais, integrador numérico com subpassos $\le 1/240$ s.
  - T02: grupo motopropulsor e transmissão (`powertrain.rs`): grade de torque de 21 pontos com passo de 500 RPM a partir de `.sim`, dinâmica de rotação do volante do motor (marcha lenta, corte de giro, resistência à rotação), relações de transmissão e diferencial.
  - T03: suspensão independente de 4 rodas (`suspension.rs`): consultas por raio à grade espacial `surface.rs`, forças de mola, amortecedores de compressão e retorno (bump/rebound), barras estabilizadoras, transferência dinâmica de peso da carroceria.
  - T04: modelo de pneus e freios (`tire.rs`): desvio longitudinal (slip ratio) e lateral (slip angle) dos pneus, elipse de atrito de Coulomb, coeficientes `front_grip`/`rear_grip` de `.sim`, trava estática dos freios ao parar.
  - T05: bancada de calibração (`calibration_bench.rs`): 102/102 testes unitários/integração passaram; determinismo em nível de bit confirmado; reprodução do fluxo de comandos de `replay.rpl`; aceleração e frenagem do 356A (0-100 em 14.37 s, 100-0 em 43.9 m) e Boxster 2.5L (0-100 em 7.83 s, 100-0 em 41.5 m).
  - T06: integração no visualizador (desktop/web): alternância em tempo real pela tecla `M` / botão da UI entre simulação 6 DOF e protótipo arcade; HUD de telemetria com velocímetro, tacômetro, marcha, aceleração lateral $g$ e reação das rodas; `fmt` e `clippy -- -D warnings` limpos; compilação completa nativa e WASM.
- Tarefas T01–T06 concluídas, código commitado, tag `iteration-007`.

### 006-game-systems
- [Run 001](iterations/006-game-systems/runs/001-game-systems/README.md):
  - T01: mapa PE de `nfs5.exe`, funções de carregamento de `.sim` (`0x0049c750`), `.ais` (`0x0049ca30`), fatores de escala. Veja [`simulation-evidence.md`](iterations/006-game-systems/research/simulation-evidence.md).
  - T02: analisadores `SimCar` (328 bytes) e `AisCar` (304 bytes) em `nfs-formats/src/sim.rs`. Validação de 88/88 arquivos `.sim` e 22/22 `.ais`.
  - T03: arquitetura de salvamento `.sav` (lista encadeada de seções `0x0065b634`), analisadores de catálogos `nfs5.car` (109 carros), `nfs5.trk` (15 pistas), `nfs5.fac` (34 missões Factory Driver) em `nfs-formats/src/career.rs`. Veja [`career-evidence.md`](iterations/006-game-systems/research/career-evidence.md).
  - T04: reversão de replays determinísticos `replay.rpl` (8 sub-amostras por tick, fluxo de entrada RLE, cabeçalho de 15 908 bytes para 8 carros), analisador `ReplayFile` em `nfs-formats/src/replay.rs`, descoberta da grade de torque de 500 RPM, bancada de referência em `local/experiments/bench/sim_baseline.json`. Veja [`telemetry-evidence.md`](iterations/006-game-systems/research/telemetry-evidence.md).
  - T05: integração, 83 testes unitários passaram, `fmt` e `clippy` (`-D warnings`) limpos, compilação completa `build.ps1 -Target all` (nativo + WASM) executada sem erros.
- Iteração concluída, commitada, tag `iteration-006`.

### 005-unified-driving
- [Run 001](iterations/005-unified-driving/runs/001-unified-driving/README.md):
  - Inicialização unificada desktop/web (`scripts/launch-viewer.ps1`), três `Launch-*.cmd`; desktop — web/WASM em janela separada do Edge/Chrome. CLI nativo preservado, adicionado catálogo sem argumentos e entrada contínua por quadros. Usuário confirmou operação interativa.
  - Web UI: Esc oculta/restaura menu, H desliga painéis, diagnósticos separados.
  - Protótipo: volante suave, limitação de ângulo por velocidade, máximo de 240 km/h, subpassos ≤1/120 s e filtro de bordas por altura. Não é a física original.
  - Grade espacial CPU sobre triângulos RD* estáticos antes do batching: altura/normal, seleção do nível admissível mais próximo e ID original de artigo/primitiva/triângulo. Todas as 15 pistas passaram na auditoria de centroides (109 707 triângulos), pior erro de 0.000164 m.
  - 72 testes unitários passaram, 3 testes especiais de GPU ignorados; fmt/clippy limpos; release nativo/WASM compilados; 44/44 modelos carregam.
  - Playwright 1.57 + janela normal do Chromium: menu/corrida/HUD/catálogo/foco verificados, sem erros na página. Vulkan offscreen nativo — skidpad e 356a inspecionados.
  - Reversão: auditoria reproduzível de PE/EDG/JNC, ressalvas sobre semântica de flags, inventário de FEData/Simulation/savedata para carreiras.
- Snapshots anteriores: `001-car-viewer`, `002-track-viewer`, `003-track-environment`, `004-track-topology`.
- [Plano 005](iterations/005-unified-driving/PLAN.md). [Próxima etapa](docs/next-iteration.pt-BR.md).
- Tarefas T01–T06 concluídas, código commitado, tag `iteration-005`.

### 004-track-topology
- [Run 001](iterations/004-track-topology/runs/001-topology-verification/README.md): capturas offscreen Vulkan de pistas e veículo:
  - `skidpad_topology.png`: exibição de 167 bordas de pista de skidpad (121 linhas contínuas) sobrepostas à geometria sem z-fighting.
  - `autobahn_topology.png`: renderização correta de linhas de múltiplas faixas e acessos da autobahn sobre a paisagem.
  - `car_356a_regression.png`: ausência de regressões visuais e lógicas na renderização de carros (356A).
- Formatos `.jnc`, `.edg`, `.map` totalmente pesquisados e especificados em `local/research/004-track-topology/README.md`.
- Analisadores `nfs-formats/src/topology.rs`: validadas todas as 15 pistas do jogo sem falhas.
- Montagem de polilinhas em `nfs-assets/src/track_loader.rs`: conexão de segmentos consecutivos de bordas da pista.
- Renderização `TopologyRenderer` em `porsche-viewer`: shader WGSL de linhas, deslocamento de profundidade `clip_pos.z - 0.0004 * clip_pos.w`, alternância de visibilidade (hotkey `T`, API `set_show_topology`).
- Interface Web: carregamento automático de recursos por padrão a partir de `local/game` (sem necessidade de selecionar arquivos manualmente), preservação dos botões de carregamento manual ("Pasta do jogo", "Arquivos") para sobrescrita com botão de reset de volta para `local/game`, menu suspenso nativo `<select id="targetSelect">` para seleção instantânea de pistas/carros sem apagar texto, checkbox "Bordas 3D".
- **Navegação de Carro Arcade na Pista (Arcade Car Navigation)**:
  - Carro esportivo Porsche estilizado (`car_mesh.rs`) com troca de cores da paleta (tecla de atalho `P`).
  - Física de carro arcade (`arcade.rs`): aceleração, frenagem, esterçamento dependente da velocidade, freio de mão com derrapagem (Espaço), cálculo de marcha (1..5, R, N) e rotações do motor (RPM).
  - Fixação na pista: adaptação de altitude ($Y$) e inclinação da carroceria pelas elevações e curvas da pista (`sample_road_elevation_fromEdges`), rebote nas bordas `.edg`.
  - Câmera dinâmica de 3ª pessoa com interpolação suave e troca de visões (Chase / Bumper / Free, tecla `C`).
  - HUD de corrida na versão Web: velocímetro translúcido de vidro (km/h), indicador de marcha, escala do tacômetro (RPM) e dicas de teclas. Na janela nativa o status é exibido no título da janela.
- Scripts de pesquisa de reversão preservados na pasta versionada `scripts/research/`.
- Testes: 53 testes unitários passam (26 em assets, 21 em formats, 6 em viewer), `cargo clippy --all-targets -- -D warnings` e `cargo fmt` limpos, compilações release nativas e WASM geradas. Verificação interativa no navegador executada (Playwright + teste manual).

### 003-track-environment
- [Run 001](iterations/003-track-environment/runs/001-environment-baseline/README.md): capturas offscreen Vulkan da pista `skidpad`:
  - `skidpad-overview.png`: visão geral da pista circular Skidpad do alto com adereços posicionados (cones de slalom, seta de largada) e panorama do horizonte.
  - `skidpad-cone-macro.png`: macrovisão do cone de tráfego `CONE` apoiado na superfície do asfalto, sem flutuação ou desalinhamentos.
  - `skidpad-arrow-macro.png`: primeiro plano da seta de direção de largada `ARW1`.
  - `skidpad-driver-view.png`: visão da perspectiva do piloto para a pista (cone de passagem, asfalto, estruturas, cerca e horizonte natural).
- Análise de cenários de posicionamento `.scn` (`nfs-formats/src/scn.rs`): decodificação de coordenadas, orientação 3x3 e FourCC. Mapeamento de 11/11 elementos em `skidpad_st1.scn`.
- Instanciação de adereços de biblioteca dinâmicos (`Base & 0x8000 != 0`): modelos de adereços são armazenados em `scene.prop_articles` e renderizados exclusivamente através do passo de instanciação (`PropDraw`), evitando o artefato de flutuação na origem (0, 0, 0).
- Carregamento e renderização do céu: textura do horizonte `horz` de `Sky/<track>.fsh` (dois blocos verticais 256x128) desdobrada em panorama cilíndrico de 360° com transição suave para a cor de fundo de terra/céu (`sky.wgsl`).
- Zero regressão: todos os 44 carros (`44/44 passed`) e todas as 15 pistas (`15/15 passed`) carregam e validam com sucesso.
- Testes: 40 testes unitários passam, `cargo clippy -- -D warnings` limpo, `cargo fmt` verificado, compilações nativas e WASM geradas.

### 002-track-viewer
- [Run 001](iterations/002-track-viewer/runs/001-track-baseline/README.md): capturas offscreen Vulkan da pista `skidpad`:
  - `skidpad-overview.png`: visão geral da pista circular, área interna e paisagem.
  - `skidpad-road-joint.png`: macrovisão da junção contínua de blocos adjacentes da pista `RD0040C` e `RD0048C` (distância entre vértices 0.00000).
  - `skidpad-tirewall.png`: macrovisão de barreiras de pneus `tir1`, muros de pedra, árvores e estruturas.
- [Run 002](iterations/002-track-viewer/runs/002-texture-format-and-batching/README.md): correção de texturas FSH de 16 bits `0x7e` (ARGB 1555) e batching de malhas:
  - Eliminada pixelização roxa em `farmland`, `castle`, `foothills`, `industrial`, `monaco1`, `monaco2`, `monaco4`.
  - Batching de geometria por materiais reduziu a quantidade de buffers/malhas em 97% (`castle` de 11 296 para 263, `industrial` de 8 101 para 240, `farmland` de 3 836 para 184), prevenindo exaustão de recursos do WebGPU.
  - Adicionadas imagens com zoom detalhado e visão panorâmica, confirmando ausência de artefatos.
- Análise de contêineres `karT` de CRP (`nfs-formats/src/track.rs`), suporte a tipos de primitiva 3 (triângulos), 4 (quads) e 1 (tiras de triângulos com salto de uniões degeneradas).
- Decodificador FSH suporta formatos: `0x7d` (BGRA 32bpp), `0x7f` (BGR 24bpp), `0x7b` (paletizados 8bpp), `0x78` e `0x7e` (ARGB 1555 16bpp com 1-bit alpha). Todas as 15 pistas do jogo validam e carregam com sucesso.
- Montagem de malhas `nfs-assets/src/track_loader.rs`: 100% de correspondência de materiais por `mt+0x28` com nomes de texturas FSH. Coordenadas em metros, transformação `[x, y, -z]` com orientação CCW gera normais corretas para o asfalto.
- Filtragem de adereços de biblioteca pela flag `Base & 0x8000 != 0` eliminou o artefato de objetos flutuantes no centro da pista.
- Zero regressão: todos os 44 carros da iteração 001 carregam com sucesso (`verify_all_cars.py`: 44/44 passed).
- Testes: 37 testes unitários passam, `cargo clippy -- -D warnings` limpo, compilações release nativas e WASM geradas.

### 001-car-viewer
- [Run010](iterations/001-car-viewer/runs/010-material-depth/README.md): todos os 44
  modelos carregados, 88 capturas GPU frontais/traseiras inspecionadas, sem novos defeitos visíveis.
- Corrigidos Base/style/LOD, canais pr sequenciais, escala/tr/Z/winding,
  atlases FSH, rodas e acabamento de modelos especiais.
- Sobreposição de faróis do 356b corrigida pelo campo assinado de material mt+0x114 -> depth bias.
- Pintura utiliza máscara alpha: lâmpadas/cromados mantêm a cor original.

## Aceitação e limitações

A iteração `009-game-shell` foi integralmente aceita (tag `iteration-009`).
Próxima etapa — `010-evolution-career`: ciclo completo da era Classic, árvore de torneios `nfs5.trn`, compra/venda de seminovos e mercado de peças.
Veja `docs/next-iteration.pt-BR.md` e o roteiro completo em `docs/roadmap.pt-BR.md`.

## Fundação do projeto

Rust/wgpu/winit, Scene compartilhada nativa/WASM, quatro crates no workspace (`nfs-formats`, `nfs-assets`, `nfs-game`, `porsche-viewer`).
local/game: 1742 arquivos / 599126359 bytes, manifesto SHA-256 em docs/game-manifest.json.
Ambiente e versões: docs/environment.pt-BR.md e docs/building.pt-BR.md; formato: docs/crp-format.pt-BR.md.
Git main, snapshots locais iteration-001..iteration-009; remote não configurado.
