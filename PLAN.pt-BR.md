# Plano de Recuperação de Porsche Unleashed

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


Pacotes 189/190/192 concluídos, executores livres. Root — checkpoint 192 / transmissão.
7a9807a publicado; 172/174/175 aguardam 176. Em seguida bloqueadores de análise de global alias / ABI originais.

## Objetivo imediato: EXE completo do jogo a partir de C/C++

Esclarecimento do usuário 2026-10-11: o resultado desta etapa é a compilação e execução completa do jogo.
Checkpoint 160 enviado (pushed) c1a67fd; aceito o pacote seguinte 165. A biblioteca geral e os programas de verificação compilam;
o alvo real do jogo ainda não vincula (linka): 267 símbolos não resolvidos visíveis / 303 referências. Esta é a fronteira
atual do grafo recuperado, e não a contagem de todas as funções restantes: novos corpos podem
abrir novas dependências, incluindo chamadas indiretas e consumidores parcialmente recuperados.

1. Após a integração 173 aceita, continuar os candidatos de compilação mecânica, RTTI e stdio
   e o 004d3420 completo; 004a6a00 foi recuperado, mas o modo virtual ainda não está delimitado: 131 permanece isolado.
   Formatador fatal/bootstrap e strings aceitos no 143; auxiliares de float 147 aceitos; lowio 005a953e aceito no 156; em seguida motores decimal/locale.
   O 00525ec0 parcial requer o contrato EAX original; não conectar retorno adivinhado.
2. Com base no relatório game-link real, recuperar blocos conectados inteiros de inicialização/aplicação,
   renderizador/driver e serviços de recursos. Após cada pacote, repetir a vinculação do alvo
   real do jogo e contabilizar novas dependências; não fechá-las com stubs.
3. Obter um EXE real do jogo, executar a inicialização com recursos originais, janela/entrada,
   primeiro quadro, menu e encerramento regular. Este é um marco intermediário, não a execução completa do jogo.
4. Levar Quick Race, ambas as carreiras, física/IA/danos, progressão/economia,
   saves e som ao comportamento original verificado. Retornar a todos os itens de
   docs/recovery-validation-backlog.md. Somente então — esquema arquitetural e Rust.

## Esquema de funcionamento do jogo após a recuperação do código

- [ ] Após a análise e recuperação completas do código, construir e versionar
  um esquema arquitetural geral do jogo em `docs/architecture/`: inicialização/encerramento,
  loop principal do jogo, módulos e o grafo de suas conexões, threads/callbacks,
  proprietários de dados e ciclo de vida dos recursos.
- [ ] Detalhar separadamente as conexões de UI/modos/carreiras/saves com física, IA,
  danos, economia/garagem, renderizador, entrada e som.
- [ ] Fundamentar os esquemas com referências aos arquivos C/C++ recuperados e módulo/SHA/VA
  originais. Separar a arquitetura confirmada do original, a adaptação de plataforma
  e conexões ainda desconhecidas. Critério de conclusão: pelos esquemas é possível rastrear
  inicialização→menu→corrida→resultado/salvamento→saída e localizar o código de cada transição.

O objetivo do esquema é a subsequente reescrita do jogo em Rust (esclarecimento do usuário
2026-10-10). Ordem: baseline C/C++ recuperada → verificação do comportamento
original → esquema de arquitetura → Rust nativo/web. Para o Rust, detalhar adicionalmente
as fronteiras dos módulos, propriedade/ciclo de vida dos dados e troca entre subsistemas,
de forma que a migração preserve a semântica original e se apoie em uma estrutura compreensível.

Caminho ativo desde 2026-10-08 — [v2/001-original-recovery](iterations/v2/001-original-recovery/PLAN.md).
Corpus completo de todos os binários → original Windows/x86 compilável → porte
moderno. Iterações separadas `iterations/v2/*`, compilações `local/builds/v2/*`.
Resultado atual: 24 PE + 1 NE / 36 587 funções / 2 827 310 instruções
exportadas integralmente; 3 199 385 bytes executáveis ainda não foram classificados
como instruções. Todas as 36 587 funções tentadas pelo descompilador: 36 583 pseudo-C,
4 falhas/timeouts, 5639 funções com avisos. O inventário foi aprovado.
Diretamente C/C++ por escolha do usuário; a primeira execução do jogo é permitida mais tarde.
Árvore de endereços: 25 módulos / 36 587 funções; biblioteca nativa x86 e bancadas
isoladas. Run 002: startup 0x4b6710 verificado em 175 entradas. Run 003: mais 9 funções
C++ fe.txt/linha de comando → fluxo FE → despacho verificadas em 236 casos,
incluindo fe.txt real. Run 004: mais 11 funções da heap proprietária em C++;
551 casos coincidiram em toda a arena após cada operação, 236 regressões de FE passaram.
Run 005: mais 29 funções de requisições de arquivos/filas/conclusão/leitura em blocos;
89 comparações conjuntas FE/heap/IO passaram, 551 de heap e 236 de FE passaram.
Total de 50 funções manuais verificadas. Três callbacks omitidos adicionados
ao índice de SHA suplementar: 36 587 automáticos + 3 = 36 590 registros no catálogo.
Callees externos de CRT/SO/SIMD/disco/threads/callbacks ainda estão abertos; 0 correspondências
de bytes/módulos inteiros. Sem EXE v2 do jogo. Histórico de runs preservado.
Startup e dependências abertas — reference/startup.json. Proprietário — coordenador,
Run011 disk_backend e Run012 fe_callbacks. Invólucros de alocação/init de dispositivo já feitos no Run006;
worker/thread/espera/eventos/disco/arquivo e inicialização 0x4b6a50 ainda em aberto.
Run 006: mais 6 funções de inicialização de página/lista/dispositivo; 474 comparações x86 e 89 regressões
conjuntas passaram. Page wrappers movidos para a bancada comum, APIs de SO continuam como
fronteiras. Total de 56 funções verificadas; catálogo de 36 592 (5 suplementares).
Worker 0x568530 indexado (925 bytes), ainda não recuperado.
Próximo passo concreto — 0x5688d0 jump table → worker/controle/conclusão,
trampolim/início de thread 0x55f4f0/0x55f5f0, espera/eventos → backend de disco/arquivo.
Relatório: iterations/v2/001-original-recovery/runs/006-file-device/README.md.

2026-10-08: a pedido do usuário, mantemos a 012 como está e alteramos a abordagem.
Run 020: 47 loops originais de quatro rodas / 188 estados coincidiram com Rust;
221 testes (3 ignorados), fmt/clippy/wasm32/nativo/web e 3 Quick Race passaram.
Execução geral de navegador do Run 020 não concluída. O adaptador de força do jogo é mantido,
a 012 não está encerrada. Migrações adicionais na 012 foram interrompidas para o desenvolvimento da v2.
Run 019 enviado (pushed): 13b70f1.

Run 019, 2026-10-06: EDGs originais conectados à árvore geral de suportes do jogo.
3 árvores mistas / 27 consultas EDG, 8 seleções de corpo, 45 respostas completas,
5 ramos de altura / 29 estados de material coincidiram com x86. 220 testes em Rust, 3 ignorados;
fmt/clippy/wasm32, release nativo/web, 3 Quick Race e 21 verificações de navegador passaram.
API de corpo/roda em estado original separada do adaptador de força; campos/forças/cadência,
special/carro-carro, UI/missão/verificação visual permanecem na 012. Sem executores
ativos, proprietário do restante — coordenador. A seguir 0x499bc4..0x499eec: deslocamento
fallback/frontal e roda +0x64/+0x6c → forças. Fonte/fronteiras/comandos:
iterations/012-campaign-fidelity/runs/019-original-contact-runtime.

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

Run 013 dentro da 012, 2026-10-05: suportes de tipo 1 originais / seleção de nível rastreados;
36 polígonos / 10 seleções de folhas / 10 divisões quadráticas passaram no x86 original. Predicados
e seleção de folhas migrados para Rust, comparados com o original; verificações passaram.
Fonte Base/pr/vt/df encontrada, timer 128 / contadores de 64Hz rastreados. Executores finalizaram.
A seguir coordenador: flags brutos/material e consulta de folha espacial até o runtime. Compilação fa56d05.

2026-10-05, Run 012: callback de canto incluído na verificação do x86 original;
468 estados coincidiram. Migrado trecho separado em Rust de contato preparado,
por enquanto fora do loop do jogo. Geometria de pontos / direção da normal verificadas separadamente.
A seguir contrato completo de seleção de contato e ligação de campos originais com o estado do veículo.

Run 011, 2026-10-04: por decisão do usuário, recuperamos o original em todos os
subsistemas, incluindo código antigo. Varredura (sweep) independente de fronteiras removida do runtime
e preservada em local/experiments/012-swept-boundaries-20261004. Compilação — fa56d05.
Primeiro concluímos a 012: consumidores originais de física/contatos, missões e UI,
comparação com o original. 2026-10-05: EDG → consulta → reação 0x494000 rastreados;
64 verificações do trecho de reação em instruções x86 originais passaram. Em seguida reação
angular e condições de aceitação de contato; migração para o runtime ainda não realizada.
013 planejada para danos e mercado de usados, não iniciada. Regras: AGENTS.md.

2026-10-04, Run 010: o usuário completou a 0M01 e relatou o ciclo "Continuar".
Confirmada a reexibição do resultado mantendo a fase 4/5 inalterada.
JS corrigido, a regressão reproduziu o erro antes da correção e passou depois.
Corrigida também a referência da 1m01 ao boxster.sim ausente → boxster25.
Windows/WASM compilados. Chromium confirmou Continue, salvamento, início real
da 1m01 e repetição após fail (finalização em modo de teste). Cinco testes em Rust da Factory passaram.
Run 010 concluído. A seguir: aceitação de jogabilidade da próxima missão e defeito de limites do Quick Race.


Atualizado em 2026-10-03. Ativa **012-campaign-fidelity** a partir da 011 concluída.
Run 008: conectadas geometria/animação de rodas do CRP, contato da carroceria com a pista
em capotamento e colisões jogador/IA/IA. A bitola do Boxster é obtida do modelo.
184 testes em Rust passaram; Windows/WASM compilados. O navegador confirmou pivôs de roda,
rotação/esterçamento e contato no Quick Race; regressão geral 21/21. Ambas as repetições da 0M01 —
5/6 pontos sem capotar, porém com tempo esgotado (timeout). Modificações salvas no commit 9efb71c.
Run 009 a pedido do usuário: índice geral de todos os EXE/DLL/ASI/OCX, funções Ghidra
e referências, busca por string/endereço, dados em `research/binary-index/` sob controle do Git.
Antes das próximas alterações de comportamento, é obrigatório consultar o índice (AGENTS.md).
Cobertura verificada: 25 caminhos PE / 24 binários únicos, 36 510 funções;
clcd16.dll (NE) explicitamente fora da análise PE. Busca de string/endereço e desmontagem funcionam.
Próximo passo após publicação: via índice restaurar o caminho original de
missão/física e levar a 0M01 ao resultado dentro do limite original.

Prioridade do usuário 2026-09-29: publicamos um checkpoint intermediário agora.
O [Run 007](iterations/012-campaign-fidelity/runs/007-publish-checkpoint/README.md)
contém funções em funcionamento, restrições e instruções de execução. Em seguida — um passo
de jogo concluído: 0M01 do início ao resultado correto. Engenharia reversa curta de consumidor específico,
correção, corrida, commit pequeno; não postergar a publicação até a reversão completa.

Bloqueador histórico Run 006: recuperar os consumidores de EXE SIM 0x10c/0x110 e a fonte
da geometria de rodas. Sua interpretação como bitola força o runtime a aplicar 1 m;
a semântica original não foi estabelecida. Dois erros de forças/raios de suspensão corrigidos,
172 testes em Rust passaram, Windows/WASM compilados, mas attempt-5 ainda capota
após o 2º ponto. Sem colisão da carroceria com o solo. Passo a passo completo/UI permanecem abertos.

Histórico da verificação atual:

Run 006: corrigido o suporte ausente da pista Skidpad após MESH04.
169 testes em Rust passaram, Windows/WASM compilados. A repetição completa 4/6 pontos,
sem falhar; perde a trajetória na curva e sofre timeout. Próximo
passo — separar o erro de controle da sonda da física, depois fluxo completo de resultado.
Ambas as corridas salvas em runs/006-mission-playthrough; iteração aberta.
Continuação: attempt-3 comprovou o capotamento na curva. Corrigido o sinal invertido
das forças da barra estabilizadora, reproduzido por teste isolado; nova verificação em andamento.
Attempt-4 mostrou a persistência do capotamento. Próximo erro confirmado —
projeção em vez de interseção do raio da suspensão com o solo durante inclinação lateral. Implementado
raycast sobre os triângulos finais originais; regressão e repetição em andamento.
Snapshots 001–011 congelados; observações do usuário são corrigidas exclusivamente na 012.

## Objetivo

Porte completo para Windows, Linux, macOS e web: Evolution, Factory Driver,
demais modos, regras de eventos, economia, perfis/saves, interface e som.
Grandes etapas: [docs/roadmap.pt-BR.md](docs/roadmap.pt-BR.md).
Visualizador e carro arcade são ferramentas auxiliares.

## Concluído: 011-factory-driver

Plano de trabalho: [iterations/011-factory-driver/PLAN.md](iterations/011-factory-driver/PLAN.md).
Resultados: [STATUS.pt-BR.md](STATUS.pt-BR.md). Relatórios: [Run 001](iterations/011-factory-driver/runs/001-factory-driver/README.md).

1. **T01 — engenharia reversa do Factory Driver:** especificação de 34 missões de `nfs5.fac` e base de idioma `festrings.csv`.
2. **T02 — motor de desafios e manobras:** detectores `StuntDetector` (180° slide, 360° spin, reverse J-turn, penalidades de slalom, controle de danos à carroceria).
3. **T03 — patentes de carreira e carros de recompensa:** de Applicant a Master Ace Driver, carros bônus ('78 911 Turbo 3.3, '73 Carrera RS 2.7, '99 911 GT3 Factory Edition).
4. **T04 — interface web da escada de missões:** janela modal `#factoryMissionsModal`, filtros de Tier 1–3, falas de Rolf, status e melhores tempos.
5. **T05 — eliminação de defeitos de campanha e autenticidade de interface:** briefing autêntico, correção do erro de compra de carros, carregamento de modelos 3D reais da Porsche nas missões, correção da pista Canyon.
6. **T06 — integração e aceitação:** 142 testes em Rust passaram, Clippy/Rustfmt limpos, Playwright E2E 12/12 verificações 0 erros, compilação release nativa e WASM.

## Snapshots concluídos

- [001-car-viewer](iterations/001-car-viewer/README.md): modelos de carros.
- [002-track-viewer](iterations/002-track-viewer/README.md): geometria de pistas.
- [003-track-environment](iterations/003-track-environment/README.md): ambiente.
- [004-track-topology](iterations/004-track-topology/README.md): topologia, protótipo de corrida.
- [005-unified-driving](iterations/005-unified-driving/README.md): execução unificada, superfície.
- [006-game-systems](iterations/006-game-systems/README.md): formatos dos sistemas de jogo.
- [007-physics-simulation](iterations/007-physics-simulation/README.md): simulação do carro.
- [008-race-loop](iterations/008-race-loop/README.md): loop de corrida e oponentes.
- [009-game-shell](iterations/009-game-shell/README.md): shell, perfis, primeiros eventos de carreiras, som.
- [010-evolution-career](iterations/010-evolution-career/README.md): modo Evolution, economia, tuning, auditoria de 15 pistas.
- [011-factory-driver](iterations/011-factory-driver/README.md): modo Factory Driver (34 missões, manobras, patentes).

Histórico de verificações — em STATUS.pt-BR.md e nos runs dos snapshots. Defeitos encontrados
posteriormente são corrigidos em um novo snapshot, sem reescrever a história.

## No momento: 012-campaign-fidelity

Prioridade do usuário de 2026-09-25: corrigir a incompatibilidade de interface e objetivos,
início incorreto do Factory Driver, decolagens de carros e freio/marcha à ré na tecla S.
Plano de trabalho: [PLAN 012](iterations/012-campaign-fidelity/PLAN.md).
T01 — telas de carreiras; T02 — cenário/início de missões; T03 — contatos e entrada; T04 — aceitação.
Sem Computer Use foram concluídos os objetivos SCN da 0M01 em vez de término falso por volta,
regressão de contatos/frenagem, extração de UI e compilações Windows/WASM. 151 testes em Rust e
14 verificações de navegador passaram. Aceitação visual aberta: câmera da 0M01 obstruída pela geometria,
UI 1:1 e regras do original exigem conferência. CLI nativo ainda utiliza física de tabelas.
Checkpoint 2026-09-26: todas as tarefas permanecem abertas e parcialmente concluídas; detalhes,
restrições e comandos exatos de continuação — em [PLAN 012](iterations/012-campaign-fidelity/PLAN.md)
e [Run 001](iterations/012-campaign-fidelity/runs/001-fidelity-repair/README.md).
Áudio/cockpit adiados até estas correções: [plano](docs/planned-audio-cockpit.pt-BR.md).

Continuação 2026-09-26: Computer Use verificado, `sky.list_apps()` → `spawn EPERM`.
Run 002: arquivos SIM originais conectados ao runtime web, adicionado Quick Race,
corrigidos o sinal de curva da IA, lookahead de sprint e métrica falsa de auditoria antiga de pistas.
157 testes em Rust passaram; Chromium 19 verificações passaram, 0 erros de JS, 1 falha aberta
de mudança de direção na 0M01. Cenários, tabelas AIS/AI e contagem de participantes da campanha ainda
não foram recuperados. Próxima prioridade — comportamento comprovado da 0M01 e composição de corridas
com base em dados originais/EXE, e não na extensão de cenários aproximados.
Run 003, 2026-09-27: corrigido impulso de frenagem das rodas (R→frente 8/8 repetições),
conectada a escala comprovada de SCN v4. 162 testes em Rust e 20 verificações no Chromium passaram,
0 erros de JS / falhas conhecidas; Windows/WASM compilados. A câmera é obstruída por L A / ARW1;
o EXE comprovou a alternância ausente de setas via links de animdefs.txt/triggers.
Próximo passo — primeira ativação de seta e conexão deste mecanismo.
Aceitação visual permanece aberta. Veja [Run 003](iterations/012-campaign-fidelity/runs/003-factory-diagnostics/README.md).

## Regras permanentes

Run 004 verificado: setas vinculadas a animdefs/SCN conectadas, obstrução inicial de câmera
eliminada; 166 testes em Rust e 21 verificações no Chromium passaram. Windows/WASM compilados.
A seguir — consumidor start-pose e condições originais de despacho de trigger, depois conclusão
completa da 0M01. O objetivo geral de carreiras/UI permanece aberto; sem atribuições ativas.
Run 005 (2026-09-28): predicado shape1 implementado — diagonais da carroceria, limites
de SCN heading/velocity/speed e End baseado em tipo. 169 testes em Rust / 21 verificações de navegador passaram,
Windows/WASM compilados. A seguir — limites originais exatos / origem do modelo, corrida completa da 0M01
e fluxo de penalidade/resultado. Agentes interrompidos por limite de cota, atribuições finalizadas.

- `local/game` é apenas para leitura; experimentos que alteram o original — em `local/experiments`.
  Não copiar recursos para os snapshots ou Git.
- Novo snapshot — via `scripts/new-iteration.py`, sem runs e caches anteriores.
- Antes do trabalho, conferir STATUS, PLAN ativo e runs com o Git e o disco.
