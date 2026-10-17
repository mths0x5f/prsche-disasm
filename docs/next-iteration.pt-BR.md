# Etapa Atual: v2/001-original-recovery

14/10/2026: compilation-first 192/190: 1054 VAs distintos de Porsche.exe geraram COFFs x86
reais: 924 do corpus geral + 130 folhas thiscall, 0 interseções. Em 27 corpos folha (leaf bodies),
os bytes de máquina coincidem com o original. Estes são candidatos, não um EXE jogável/aceitação de fidelidade;
a linha de base de produção de 476 funções completas + 6 parciais e a linkedição do jogo 173 com 267 símbolos / 303 referências permanecem inalteradas.
184: 3312 TUs reutilizados; 2460 alterados cobriram 37 batched cl + 12 pilotos / 153 falhas anteriores,
sintaxe 733→923, erros de globais ausentes 25306→16818, 0 perdidos / 0 fallback ambíguo.
188: 733 objetos reutilizados / 190 novos, 3 lotes /MP6 em 43.416 s, 0 erros de geração de código;
384 nomes indefinidos / 747 referências do subconjunto automático. 187: 127 COFF / 32 falhas, apenas 8 referências a __fltused.
186: 1258/1301 extensões RET inferidas coincidem; 42 divergências / 1 sem RET, argumentos de chamada ausentes permanecem abertos.
189 concluído: 99 reescritas exatas / 39 TUs, 1920 checagens nativas; 923→924 aprovações de sintaxe.
192: 923 COFFs reutilizados / 1 novo 00553a70, 2.732 s / 0 erros de geração de código; 190 com 130 COFFs folha / 29 falhas.
Reutilização byte-idêntica e evidências originais de ABI/dados são preservadas. Ainda não há EXE.

Resultado atual — [Run173](../iterations/v2/001-original-recovery/runs/173-float-transport-integration/README.md): **476 funções C++ verificadas** e 6 consumidores (consumers) parciais registrados.
Compilação geral MSVC Win32: 157 projetos / 292 TUs únicos; 137 alvos de comparação/alias, 9 OS nativos e 3 fixtures de link.
15 relatórios x86 originais recentes / 24 560 comparações, incluindo 8 791 repetições em produção sem observadores, mais 4 casos compostos; todas as 12 verificações nativas/link passaram.
Aceitas 46 novas funções: saída/análise de float original, transporte de rede inferior e construtores de rede.
00580ad0 verificada novamente via io_find canônico; o segundo algoritmo e a contagem dupla foram eliminados.
Linkedição do jogo: 0 erros de compilação / 267 símbolos não resolvidos / 303 referências / 0 outros diagnósticos; não há EXE jogável.
Esta é a fronteira de dependências atual, não o restante total. Proprietários de RTTI e o 004d3420 completo ainda estão em aberto.
Prioridade em 12/10/2026: grafo C/C++ totalmente compilável → primeira execução experimental; verificações profundas em lotes via backlog.
Funções verificadas e candidatos de compilação recuperados mecanicamente são contabilizados separadamente; não há stubs nem algoritmos adivinhados no jogo.
Auditoria SHA em lote/cache; inventário medido de 9,3→2,4 s refere-se a 156, e não a toda a restauração.
Rota: baseline C/C++ totalmente verificado → esquema de arquitetura do jogo → Rust nativo/web.
Execução completa do jogo, live timer/WM_CLOSE e homologação visual permanecem abertos.

Rota subsequente (esclarecimento de 10/10/2026): C/C++ restaurado e verificado
→ esquema arquitetural a partir das fontes → reescrita para Rust nativo/web.
O esquema inclui limites de módulos, propriedade de dados, ciclo de vida de recursos
e interação de subsistemas; a tarefa detalhada está fixada no PLAN geral.

A decisão do usuário de 08/10/2026 substitui a ordem anterior: manter a v1 como está,
criar uma v2 separada e restaurar o original compilável completo a partir dos binários.
Plano ativo — [v2/001](../iterations/v2/001-original-recovery/PLAN.pt-BR.md).
Esclarecimento: diretamente C/C++; a primeira execução do jogo pode ocorrer mais tarde. Run 002
criou a árvore de endereços e a biblioteca/probe x86. Run 003 restaurou nove
funções de FE stream e as comparou em 236 casos com o x86 original. Run 004
restaurou 11 funções do heap próprio: 551 comparações de toda a arena após
cada operação passaram. Run 005 restaurou mais 29 funções de fila de arquivos,
leitura de conclusão/chunk e listas. 89 comparações conjuntas de FE/heap/IO, 551 regressões de heap
e 236 de FE passaram; total de 50 funções. Próximo pacote — wrappers de alocação
0x56e5f0/0x56e640, inicialização/worker de dispositivo 0x568390/0x568530 e despacho de disco/arquivo.
O worker imediato da bancada ainda não reproduz os threads originais;
após a restauração — nova verificação conjunta e inicialização 0x4b6a50.
Chamadas desconhecidas de OS/CRT/SIMD e outras permanecem como dependências externas;
suas substituições gravadoras existem apenas nas bancadas. Run006 já restaurou wrappers
de página/construtores de lista/inicialização de dispositivo: 474 comparações e 89 regressões conjuntas
passaram, totalizando 56 funções. Em seguida, worker 0x568530, jump table 0x5688d0,
trampolim de thread/start/wait/events e despacho de disco/arquivo.
Compilações — `local/builds/v2/001-original-recovery`; dados em `local/game` compartilhados,
imutáveis. 012 não é declarada concluída. O plano anterior abaixo é histórico,
incluindo a transferência de danos/usados para a 013: na v2, esses sistemas são restaurados
no grafo de fontes completo, os novos números de etapa serão definidos pelo plano da v2.

Atualização de 04/10/2026: primeiro concluímos a 012 pelo comportamento original,
sem criar um modelo aproximado do zero; verificamos a lógica existente da mesma forma.
Depois — [plano 013: danos e mercado de usados](planned-damage-used-cars.pt-BR.md).
A engenharia reversa de contatos/danos começa na 012; a própria 013 ainda não foi criada.

Atualizado em 25/09/2026. Após as observações do usuário sobre a 011, a prioridade foi alterada:
conformidade das carreiras com o original, início das missões e estabilidade de movimento. 001–011 congelados.
O snapshot 012 foi criado a partir do 011 sem os runs anteriores. O código da 011 foi salvo como resultado histórico,
mas suas afirmações anteriores de conformidade total não foram confirmadas pela verificação atual.

1. T01: telas de Evolution/Factory Driver: salas separadas e transições corretas,
   fontes de imagens/briefings conforme os Layouts do original. Nenhum briefing comum
   de Rolf com o esquema 0M01 para Evolution. Quadros e roteiros de referência, não apenas CSS.
2. T02: Factory Driver 0M01: largada/direção/roteiro/objetivos. Verificar SCN Start,
   distinguir o centro do gatilho da posição confirmada do carro. Corrigir o grid
   de largada comum nas missões; o reinício deve retornar à mesma largada.
3. T03: eliminar impulso da suspensão no primeiro/repetido contato, pista fictícia
   em y=0 ao errar e seleção de outro nível de estrada. S freia até a parada,
   em seguida engata a marcha à ré se mantido pressionado; W simetricamente para a marcha à ré.
4. T04: compilações reais nativas/WASM, verificações em navegador de duas carreiras, regressões
   físicas e fonte de cada afirmação. Não declarar todo o Factory Driver
   como restaurado pela simples presença de uma lista de missões ou teste sintético.

Tarefas/verificações de trabalho: [PLAN 012](../iterations/012-campaign-fidelity/PLAN.md).
Som e cockpit foram preservados no [plano adiado](planned-audio-cockpit.pt-BR.md), após as correções.
Carreiras completas, outros modos e sistemas operacionais atuais permanecem o objetivo do [roteiro](roadmap.pt-BR.md).
