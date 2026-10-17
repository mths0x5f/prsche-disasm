# Validações Pendentes da Restauração v2

Checkpoint269/271/273:
- [x] 266: todos os 10 COFFs chamadores brutos de 00531f90 / RET0 cdecl DWORD completo auditados; vínculo exato,
  verificações nativas de identidade canônica / EAX / ESP / arena de 512 B PASS; COFFs do jogo reutilizados inalterados.
- [x] 268: 2 adaptadores stdlib Win32 existentes / 64 ciclos reais de trava recursiva / 256 chamadas,
  204 pins / 8 guardas PASS. Novo coletor rejeita suporte a dados executáveis / aliases;
  código exato de plataforma é suporte, não funções adicionais do jogo.
- [x] 269: 1125 VAs de função candidatas + 17 de suporte / 1142 membros, 416 nomes no link / 569 diagnósticos,
  7594 pins / 1140 símbolos em cache / 2 novos COFFs; 0 compilações, sem EXE/DLL.
- [x] 267/270/271: varredura HIGHLOW completa de 56 746 / 30 referências, 4 intervalos de candidatos omitidos 510 B / 167 instruções;
  índice de navegação separado / 15 pins / 7 guardas, índices antigos inalterados.
- [ ] Entrada/vivacidade/ABI de quatro candidatos e comportamento de preenchimento original 53c290;
  registros suplementares de candidatos não aceitam essas funções.
- [x] 272/274: um proprietário físico de 64 B + vínculo de base bruto, todas as 16 verificações nativas de
  zero em slots / identidade / gravações cruzadas / cópia de bits PASS; todos os 3 locais DIR32 brutos reais delimitados AND 0f / MEM4.
  Footprint exato / consumidores atuais são separados da vivacidade de funções candidatas.
- [ ] 272: array de ponteiros / unsigned int bruto é contrato de visão COFF x86, não garantia de tipo / alias C++ portátil.
  Bootstrap / inicialização / falha / concorrência reais permanecem em aberto.
- [ ] 006b4f20 também é o final exclusivo do 006b4b20..006b4f1f precedente; layout relativo completo
  e composição com futuros consumidores adjacentes permanecem em ESPERA (HOLD). Migração / unificação futura de proprietário
  deve preservar uma única tabela física, não definir outra cópia. Bootstrap / inicialização reais permanecem em aberto.
- [x] 273: 416 nomes reais -> 414 tarefas / 23 linhas resolvidas excluídas, 159 pins / 6 guardas.
  Retenções de extensão de sinal insegura de 595d0 e prefixo de trava de 5a4c05 mantidas.
- [x] 274/275: 1125 VAs de função candidatas + 19 de suporte / 1144 membros, 414 nomes no link / 566 diagnósticos,
  7626 pins / 1142 símbolos em cache / 2 novos COFFs / 0 compilações; 412 tarefas de pesquisa atuais.
- [ ] Próxima ABI de consumidor nativo em files.cpp 00568200 / 005682a0 + contrato original de handle_device em EAX completo
  dos quatro chamadores compartilhados; não silenciar retenção de 595d0 por meio de um alias adivinhado.

Run257 (17/10/2026):
- [x] Abaixamento (lowering) estático de CALL/RET/stack; 4 grupos de proteção, 19 casos de rejeição PASS.
- [x] Run258: 6 corpos originais / 104 B / 34 instruções, 36 864 comparações nativas e 4 verificações
  negativas PASS; 59 pins e 6 oráculos COFF reais verificados independentemente, apenas 3 CALL REL32.
  Homologação completa de CPU/jogo permanece aberta; todas as afirmações são limitadas às cadeias originais selecionadas.
- [x] 262: ADD/SUB/SBB/NEG sintéticos delimitados de byte/word/32, visões de byte alto/word,
  PUSH ESP / POP ESP / POP [ESP], CALL [ESP] / JMP [ESP+4] indiretos: 15 744 casos nativos PASS,
  19 oráculos COFF exatos / 70 B / 40 instruções / 28 pins, 19 840 mapeamentos explícitos de slot código-PC.
- [ ] 262: ISA / operandos / flags restantes, comportamento de falhas de memória guest / recursão / importação / callback
  e execução real do jogo; fixtures sintéticas finitas não comprovam tudo isso.

Checkpoint264/265:
- [x] 263: 3 corpos canônicos existentes de free/trava / 302 bytes PE, 1 lote de compilador / 0 avisos;
  4 pontos de corte de free original-Unicorn / 2048 bytes de arena / verificações nativas de trava/nulo PASS.
  Casos anteriores de 078551 heap + 31 travas citados, não reexecutados; auditoria de código-fonte / COFF / fechamento PASS.
- [x] 264: 1125 VAs de função candidatas + 15 de suporte / 1140 membros, 419 nomes no link / 581 diagnósticos;
  7493 pins antes/depois PASS, 1137 snapshots de símbolos reutilizados / 3 novos COFFs, 0 compilações.
- [ ] 264: Vínculo ABI bruto de 00531f90 com dez consumidores, provedores Win32 existentes,
  tabela / inicialização original de 006b4f20, concorrência / falha / composição completa do jogo.
- [x] 265: 419 nomes reais -> 417 tarefas, 22 linhas resolvidas excluídas; 159 pins / 6 guardas.
  A classificação genérica da fila não revoga as retenções de layout inseguro de 005925d0 ou 005a4c05 da 259.

Checkpoint261:
- [x] 259: 2 corpos canônicos / 2 vínculos exatos de PE/fonte/COFF/auditoria nativa PASS.
  Reparos apenas de fixture preservaram objetos de jogo/vínculo; um recibo nativo obsoleto sobrescrito
  foi explicitamente registrado como limitação. Cinco raízes de inclusão agora correspondem à ordem observada.
- [ ] 259: O consumidor real de retorno de char 005925d0 estende o sinal de AL, diferentemente do DWORD original.
  Recuperar contrato de retorno do chamador antes do alias; composição de provedor FILE/TLS/heap aberta.
- [x] 260: Cobertura de sintaxe 257 de 25/85, 60 rejeitadas; não é homologação nativa/do jogo.
- [x] 261: 1122 VAs de função candidatas + 15 de suporte, 417 nomes no link / 579 diagnósticos, 7461 pins PASS;
  1133 snapshots de símbolos reutilizados / 4 novos COFFs, 0 compilações. EXE/DLL real ausente.
- [x] 261: free canônico conectado em 263/264, vínculo bruto em 266/269, provedores reais de travas Win32 em 268/269,
  tabela compartilhada delimitada em 272/274. Provedores anteriores de fixtures controladas não são provedores do jogo.
- [ ] Inicialização completa do heap original / tempo de vida / adjacência / concorrência e visões tipadas portáteis permanecem em aberto.

Checkpoint249/256: 1120 VAs de função candidatas / 13 de suporte; 418 nomes vinculados permanecem. Sem EXE.
- [x] 246: Piloto de tradução estática de 76 B / 28 instruções para C++, 375 808 comparações de estado nativo (CF/ZF/SF/OF,
  registradores GP/ESP relativo/RET8/memória de 64 B), PE exato + 3 oráculos COFF / 46 pins independentes PASS.
- [ ] 246: CPU completo/PF/AF/flags indefinidas/x87/SSE/CALL/importação/callback/carregador de memória guest;
  o piloto usa proprietários existentes e adiciona 0 funções aceitas. Instruções desconhecidas falham antes de compilar.
- [x] 247: 3 corpos canônicos + 3 vínculos, 103 bytes de oráculo original / 52 CALLs / 4056 casos / 293 pins PASS.
- [ ] 247: Composição de FILE/TLS/provedor compartilhado; IDs originais 28..47 de 5a4c05 não cobertos pelo
  prefixo canônico de 26 slots. Sem solução alternativa silenciosa de limites ou proprietário duplicado.
- [x] 250/254: 23 DWORDs zero graváveis, 219 referências diretas MEM4/HIGHLOW completo; auditorias independentes/nativas PASS.
- [ ] 250/254: Aliases computados/layout completo/tempo de vida de original.data; 9 células filtradas adiadas devido à cobertura/WIP.
- [x] 251: A seleção em cache da 248 não era prova completa de PE/WIP; registradas 4 referências não indexadas de 006c0508 e
  provedor de endereço WIP existente 0065b928. Nunca tratar conjunto de candidatos como aprovação de alocação.
- [x] 252: Todos os 85 intervalos de corpos ausentes decodificados / 8516 instruções; 0 corpos inteiros suportados pela 246.
  CALL+pilha e 3 casos de tail JMP externos orientam trabalho futuro de backend, não constituem aceitação.
- [x] 255/249: Recibos exatos de compilador/COFF empacotados para coletor congelado sem comandos nativos.
- [x] 256: Diagnósticos reais validados da 249 atualizaram a fila automática de 416 tarefas; sem execução do jogo.
- [x] 253: 30 bytes de PE/oráculo exatos / 6 instruções; 18 432 comparações nativas de ponto de corte / 49 pins / 8 guardas PASS.
  MissingEntry explícito + três PCs de destino originais, JSON retém proveniência de piloto VM isolado; sem alimentação de fila do jogo.
- [ ] 253: Funções chamadas reais/ABI de receptor FUN nativo/transferências indiretas/CALL/carregador guest/EXE do jogo.
  O piloto para antes do destino; não comprova conclusão da função ou captura real de falha do jogo.

Checkpoint245: Fila automática de fronteira construída a partir do arquivo validado 243 e log de diagnóstico real.
- [x] 245: 442 nomes não resolvidos exatos / 632 diagnósticos -> 440 tarefas; 17 linhas resolvidas excluídas.
  Estados aceito/parcial/WIP/probe/interior/ABI/dados/provedor mantidos distintos; 159 pins PASS.
- [x] 245: 6 guardas significativos incluindo proprietários duplicados, referências não mapeadas, comentários/strings de fonte,
  identidade em tempo de execução/entradas desconhecidas/deduplicação; apenas parser de entrada em tempo de execução, sem captura real de falha do jogo.
- [ ] O loop de compilação/restauração automática não é concluído pela geração da fila.
  O piloto de instrução 246/257/258 é completo apenas dentro do seu escopo finito documentado;
  lançamento de CPU completo/jogo/fidelidade original completa ainda permanecem em aberto.

Checkpoint243: 1117 VAs de função + 8 de suporte, 442 nomes não resolvidos vinculados; EXE real do jogo ausente.
- [x] 234: 4 wrappers originais, 2048 pares SDK original/nativo + 2048 capturas thiscall, 445 instruções PE.
- [ ] 234: Contratos de ECX perdido/void(void) nativo 00468100/004d8230/004d8240/00538d80 exigem propagação
  de receptor no chamador; sem aliases genéricos. Novas implementações de funções chamadas 4d23f0/4d2100 abertas.
- [x] 240: Fragmentos canônicos C++ exatos + 2 vínculos cdecl, 70 bytes de oráculo original / 8 chamadores,
  2268 casos/identidade de destino/ESP/não voláteis; auditoria independente de 279 pins / 28 cabeçalhos PASS.
- [ ] 240: Prefixo real da tabela de travas CRT de 26 vs 48 original e composição provedor/global;
  fidelidade total de falha/concorrência/registrador/jogo. Fixture controlada não é produção.
- [x] 241/243: Raízes de inclusão canônicas verificadas contra recibo de compilador real bem-sucedido;
  todo fechamento de fontes entre aspas fixado. Lote serial 240 relatado com precisão, não reivindicado como MP6.
- [x] 242/243: Mesmo armazenamento de 4 bytes com/sem sinal exato; 125 referências MEM4/HIGHLOW e
  identidade de endereço nativo/gravações cruzadas de bits altos/restauração PASS. Nenhuma reivindicação de alias genérico/propriedade total de dados.
- [ ] Automação: Rastreamentos reais de falhas nativas do jogo e piloto amplo de instrução para C++ permanecem abertos;
  veja docs/recovery-automation.pt-BR.md. Fila de link estático não substitui execução nativa.

Checkpoint233 (16/10/2026): 1111 VAs de função + 4 objetos de suporte, 442 nomes não resolvidos vinculados.
- [x] 223/229: Comparações nativas/x86 originais exatas 229376+368640; BYTE com sinal chamado direto,
  argumentos de pilha retidos, comportamento de índice/contagem/status restaurado. Auditorias independentes PASS.
- [ ] 229: Alvos de callback 005907b0 em 006b49e0/contratos de entrada; saída original do parser >=164 B
  contíguos e pacote de callback 4 DWORD. Não adotar locais sobrepostos/casts adivinhados de getC.
- [x] 226/231: 5 células escalares originais graváveis, bits exatos zero/128/1/10, permissões nativas,
  gravação/leitura/restauração; par adjacente 226 retém separação de 4 bytes. Todos os locais HIGHLOW diretos verificados.
- [ ] 226/231: Aliases computados/layout completo/propriedade/tempo de vida de .data original antes da produção.
- [x] 227/228/233: Fechamentos reais de COFF de suporte, contagens separadas de função/suporte e arquivo/link.
- [ ] 224: Probe canônico em cache 005a2248 possui instrumentação formatter_text_read_trace; excluído.
  Construir proprietário canônico não instrumentado apenas após união exata de ABI/globais de locale compartilhados.
- [ ] 232: Rastrear inicialização real do callback 006b49e0; 0058ff50 apenas comprova 006b49c8/49a1,
  não a tabela 006b49e0/49a2. Referências estáticas de índice são navegação, não prova semântica.

Checkpoint222 (16/10/2026): 1109 VAs de função + 2 objetos de suporte, 445 nomes não resolvidos vinculados.
- [x] 217/222: Vínculo cdecl exato de 00590290 resolveu arquivo inteiro real; 1088 casos / 18 497 checagens de ABI.
- [x] 218: Fluxo de dados de estado do renderizador original reparado; 119 instruções consumidoras / 416 B,
  1341 instruções PE totais, 28 rastreamentos de limites nativos controlados. Retidos C4146 de jogo / C4244 de fixture.
- [ ] 218: Fidelidade total de provedor/tempo de vida/registrador/falha original; contrato raw data-pointer
  int/code* de FUN00571630 deve ser preservado quando seu proprietário real for vinculado; sem cast genérico.
- [x] 221/222: Duas células float4 originais somente leitura, bits exatos + permissões nativas READ!WRITE,
  738 leituras indexadas verificadas em PE/Capstone real; aliases formais existentes de bytes devem compartilhar células mais tarde.
- [ ] 219/221: 26 locais HIGHLOW adicionais apontam para 1.0f fora dos intervalos indexados. Resolver limites
  de instrução/fluxo de controle antes de inferir ausência de obtenção de endereço/relações de array.
  Decodificações candidatas estão em research/binary-index/readonly-scalar-relocation-gaps.json.
- [ ] 221: Relações/usos indiretos/propriedade de alias compartilhado de .rdata original antes da produção.
- [x] 220: Pacotes de suporte duplicados/adulterados rejeitados antes de quaisquer comandos nativos; funções/suporte
  contados separadamente, diretivas COFF reais verificadas, aliases comprovados separados da resolução da CRT.
- [x] 225/226: Inicialização zero delimitada/permissões de gravação/layout adjacente de fixture PASS;
  propriedade de todo o programa permanece adiada acima.

Checkpoint216: 1108 funções nativas; 432 nomes não resolvidos / 624 diagnósticos:
89 funções ausentes, 36 canônicas fora da união, 1 incompatibilidade de símbolo compilado, 299 visões de dados,
7 contratos CRT impressos. Esta é a fronteira de candidatos, não o restante completo do jogo.
- [x] 214: Saída DWORD real restaurada, SUB/ADD/*1000 módulo 32 e IDIV com sinal;
  42 instruções PE originais / contrato SDK, 36 864 comparações asm-tail nativas + 3 casos de guarda PASS.
  Correção de contagem de RET apenas em metadados: 3 caminhos originais → 1 epílogo nativo, sem reexecução nativa.
- [ ] 214: Execução completa do corpo/provedor original, inicialização bem-sucedida do provedor,
  falhas de divisão por zero, concorrência/tempo de vida de objeto e equivalência de registradores de saída.
  Fixture nativa usa callback controlado + asm inteiro verificado, não o DirectSound original.
- [x] 216: Um novo objeto, 1107 snapshots de símbolos / 531 pins de plataforma reutilizados; 6804 pins PASS,
  um arquivo/link, 0 compilações. Sem EXE ou integração de produção.

Checkpoint215: 1107 funções candidatas nativas, arquivo/link real com 426 nomes
não resolvidos / 618 diagnósticos; 90 corpos ausentes / 36 canônicos fora da união / 1 incompatibilidade de VA compilada,
292 nomes de dados / 7 contratos CRT impressos. Produção 173 inalterada.
- [x] 211: 127 instruções PE, 2 contratos comprovados de chamada direta e 2 locais de CALL+ADD ESP, 8 nativos.
- [ ] 211/215: Definição real de 00590290 com 0 argumentos vs chamador com 2 slots não utilizados: ABI cdecl bruto pode coincidir,
  mas símbolos C++ diferem. Resolver através de declaração compartilhada comprovada/contrato de proprietário,
  não por alias geral; preservar slots extras do chamador onde o rastreamento de hardware os exigir.
- [x] 215: 1094 snapshots de símbolos reutilizados / 13 novos objetos reais, 6780 pins exatos antes/depois;
  nenhuma nova compilação. Propriedade exata/interior suplementar 210/212 encontrou 0 sobreposições.
- [ ] 213: Único candidato restante de reutilização de callback 00537b40; C2065/C2664/C2440 e fluxo de dados
  do chamador ainda precisam de prova. A identidade de slot 207 não permite casts chamáveis em todo o corpus.
- [ ] 214: Vincular WORD_006b48da_214 privado a 006b48da:2 original (base 006b48d8+2)
  quando os proprietários de dados nativos forem restaurados; alocação de word isolada não deve quebrar aliases.

Checkpoint207–212 (15/10/2026), antes da união geral:
- [x] 207: 4 COFFs reais; callbacks do renderizador original / contratos CALL/RET do SDK Release,
  1042 instruções PE e evidências de local de chamada/pilha nativas verificadas; 0 reexecuções de Ghidra/runtime nativo.
- [ ] 207: Inicialização/propriedade de provedores/slots do renderizador, equivalência total de registradores
  voláteis/runtime; externs tipados não criam proprietários de dados.
- [ ] 208: 3 candidatos compilados de 9; 6 falhas preservadas. 211 verifica separadamente dois
  contratos de chamada direta; não ocultar as falhas restantes de chamada/tipo/string.
- [x] 210: 2 COFFs; alias FILD32 com sinal em 004012b0 / 7 externs exatos e contrato de vcall
  ECX self + pilha1 em 004032d0, 61 instruções PE. 212: 2 COFFs / 5 ocorrências de fatias de bytes / 57 instruções PE.
- [ ] 210: 004012b0 intermediários não arredondados retidos em x87/arredondamento/palavra de controle,
  estouro de inteiros, funções chamadas completas; 004032d0 função chamada real/tempo de vida global/execução de ABI.
- [ ] 212: Visões de extensão uint4 não são alocações canônicas/fusão de aliases;
  execução original/tempos de vida globais/estouro de índice com sinal em 00598630 permanecem abertos.
  C4146 de negação sem sinal inalterada retido; não alterar silenciosamente a presença de sinal.
- [ ] 214: Contraexemplo concreto de saída perdida em 0058f5d0: CALL [vtable+10] em 0058f5ed,
  MOV EAX, [ESP], SHR 1 em 0058f5f8; getC usa erroneamente o endereço do objeto COM. Restaurar valor de saída
  DWORD comprovado e callback do SDK antes de considerar a compilação como algoritmo utilizável.

Checkpoint202–206 (15/10/2026): 1094 candidatos nativos distintos, link de diagnóstico real
413 nomes / 600 diagnósticos; produção 173 inalterada. A compilação de candidatos não encerra a fidelidade.
- [x] 202: 97 instruções PE originais, 9 gravações raw32 / 8 visões de bits float e 1024 casos de bits nativos
  (não alinhado/sobreposição/NaN/subnormal/ordem de captura) verificados; auditoria somente leitura PASS.
- [ ] 202: 00485100 completo contra execução original, exceções x87/SSE/arredondamento e
  equivalência de chamadores/registradores. ECX de saída físico corrompido; original preservava ECX.
  A coincidência de entrada ECX/retorno EAX/RET8 não fecha este risco.
- [ ] 203: Validação de ABI original/corpo completo de 21 candidatos compilados; quatro falhas
  de chamada por ponteiro 00540480/005404e0/00554530/0058f1f0 exigem consumidores originais.
  Saída/tempo do compilador observados não foram salvos após travamento de metadados e permanecem nulos;
  COFF real/fonte/inclusões/diagnósticos próprios verificados, lote não foi repetido.
- [ ] 206: 133 nomes de função (36 canônicas fora da união / 97 ausentes), 273 nomes de dados
  (proprietários/inicializadores/aliases sobrepostos), 7 contratos CRT impressos; sem definições adivinhadas.
  O total não resolvido de 413 refere-se à união candidata de diagnóstico, não ao restante completo do jogo.
- [ ] 205: Avisos históricos/regex — apenas fila de prioridade; confirmar cada reescrita futura
  de representação por RAM/CAST/instruções originais antes de alterar a fonte.

Comandos de verificação somente leitura dos pacotes atuais:
`py -3 scripts/research/audit-v2-float-bits-202.py` e
`py -3 iterations/v2/001-original-recovery/runs/203-consumer-declaration-pilot/audit.py`.
Comando real de união/evidência de cache: `runs/206-frontier-and-float-union/README.md`.
Abaixo estão os checkpoints históricos; seus limites numéricos foram substituídos pelo 206.

Final do checkpoint 199 de 15/10/2026: 1072 COFFs reais (924+148), 28 correspondências literais de corpos folha.
Arquivo/link real executados por CLI 198 repetível sem compilação: 403 nomes brutos / 393 vinculados,
fronteira coincidiu totalmente com a 198. 197 adicionou 2 COFFs reais, não novas funções aceitas.
- [ ] 197: Abaixamento completo de high-IR/nativo do chamador e equivalência de estado/registradores voláteis;
  44 instruções PE / 4 trechos de CALL / raw ECX + pilha + EAX/RET8 verificados, 004930f0 exata em 15 B.
- [ ] 194/200: 7 visões float4 por consumidor → lote delimitado de TUs alterados; 8 links diretos de RAM
  não comprovam propriedade de dados/aliasing/tempo de vida. 3 conflitos de direção FSTP no Capstone,
  armazenamento de registradores/tokens únicos e strings apenas com endereço/não resolvidas devem ser preservados separadamente.
  Potenciais 757 corpos de lacuna _DAT / 330 de string — fila de pesquisa, não cobertura aceita.

15/10/2026: 198 arquivo/link real de 1070 objetos: 403 nomes brutos / 780 referências de objetos,
393 nomes vinculados não resolvidos / 581 ocorrências de diagnóstico; 16 novos proprietários de dados, fronteira de 145 funções
inalterada. CRT de plataforma resolveu 10, saída EXE/DLL ausente. Auditoria de 6516 pins PASS.
- [ ] 198: 241 definições de dados/inicializadores/aliasing, 145 dependências FUN e 7 contratos CRT impressos.
  O --thiscall-summary repetível aceita pacotes futuros de ABI disjuntos; não adicionar stubs.

15/10/2026: 196 — 1070 candidatos de compilação distintos (924+146), 16 novos objetos,
27 correspondências de bytes de corpo em cache preservadas. 195 — link diagnóstico real de 1054 objetos:
377 nomes / 564 ocorrências de diagnóstico, 387 nomes brutos / 763 referências de objeto, sem EXE.
- [ ] 196: 13 falhas folha restantes; aliases impressos de FP 194, gravação de valor de ponteiro 00536120,
  duas expressões escalares parciais / uint3; avisos de conversão 00485100 preservados explicitamente.
  14 gravações de endereço raw32 verificadas por PE MOV/HIGHLOW/ECX e 179 VAs de tabela;
  tempo de vida de classe/layout/despacho e fidelidade total do algoritmo não são comprovados por isso.
- [ ] 195: Vincular 36 proprietários canônicos via ABI comprovado; restaurar 109 corpos FUN
  ausentes, 225 proprietários de dados/aliases/inicializadores e 7 contratos CRT impressos.
  Estas são dependências da união candidata, não substituem o link do jogo 173 com 267/303 nem o restante total.

15/10/2026: 193 confirmou duas correções de armazenamento raw32 em CALL/RET original
e IR alto, 373 instruções indexadas coincidiram com o PE. Isso encerra dois contraexemplos
para o mecanismo de recuperação de entradas de chamadas perdidas, não sua aceitação nativa/corpo completo.
- [ ] 193: Verificar os 42 contratos de incompatibilidade restantes individualmente por entradas de hardware;
  dois deles corrigidos em piloto isolado do Ghidra, sem integração de produção/nativa.
  Em 00489530 void inferido/registradores ocultos e 22 chamadas aninhadas ainda estão abertos;
  armazenamento raw32/personalizado não comprova tipos semânticos/classe/tempo de vida.

Exigência direta do usuário em 10/10/2026: retornar às verificações ignoradas.
O coordenador atualiza esta lista a cada checkpoint e a verifica
antes da homologação arquitetural/porte para Rust; um item é encerrado apenas
com referência à verificação realmente executada. Compilação, oráculo diferencial delimitado
e correspondência visual são resultados separados.

Checkpoint173: 476 completos + 6 parciais; 157 projetos / 292 TUs, 24 560 comparações originais recentes
(8791 repetições de produção), 12 verificações nativas/link PASS. Link do jogo com 267 símbolos / 303 referências; sem EXE.
Vtables nativas conectadas também em construtores 171; inicialização real de RTTI/provedor/rede ainda não comprovada.
Saída de float 167 e análise 170 passam no original nativo real, arena completa/ABI/estado x87;
divergências de saída NaN/FPU no Unicorn preservadas explicitamente, não ocultadas.
Reutilização canônica de 00580ad0 e equivalência observador/produção em 8791 casos confirmadas na 173.

A primeira compilação/execução candidata experimental é permitida antes da conclusão de todas as provas delimitadas;
cada verificação de consumidor/ABI/global/dados/comportamento ignorada deve ser salva aqui ou no README do pacote
vinculado. Esse candidato não deve ser considerado um jogo fiel aceito; não substituir o código-fonte
por stubs/adivinhações. Auditoria de compilação em massa 178 e corpo mecânico 177 possuem status separado.
Retornar a comparações completas de grafo, limites de CRT/exceções não mascaradas/entradas inválidas,
tempo de vida de RTTI/cache de tipos e fidelidade/SO ao vivo antes da homologação final/Rust.

Compilação em primeiro lugar de 14/10/2026 192/190: 1054 VAs candidatos nativos distintos,
924 automáticos + 130 folhas thiscall; bytes de corpo de 27 folhas idênticos ao original. Sem EXE completo.
184 declarações globais/layout 4604 verificadas; 837 conflitos / 681 grafias inválidas / MXCSR sem nome
e lacunas de alias impresso não fechadas. 188 cache 733 / novos 190, 3 chamadas nativas em lote PASS.
186 RET original com 42 incompatibilidades / 1 sem RET e receptor/argumentos de chamada ignorados exigem
consumidores CALL/RET originais; 1258 correspondências de RET não autorizam reescrita geral do chamador.
190 nova tentativa 32: 3 novos / 127 reutilizados, 130 COFFs folha; 29 falhas de compilação abertas, 189 prova de fatias seguras com 1920 verificações concluídas; 519 fatias não suportadas permanecem explícitas.
192 novo 00553a70 compilado após 189; comportamento de jogo/x87/aliases/ABI do chamador ainda abertos.
Prova de ABI nativo de método de classe não comprova tempo de vida real de classe/armazenamento global/callbacks.

Experimentos de compilação em primeiro lugar de 14/10/2026:
- [ ] 177: Efeitos canônicos/proprietários de endereços globais para 134 costuras diretas + 10 virtuais + 52 de endereço;
  comparação de corpo completo original/nativo, DF60 e x87-live5, callbacks reais.
- [ ] 178/180/181: Sucesso de sintaxe/COFF não comprova ABI/semântica original;
  verificar protótipos inferidos, registradores ocultos, armazenamento sobreposto e floats estendidos
  antes de avançar os candidatos. Arquivos-objeto construídos sem dependências adivinhadas.
- [ ] 179: Cabeçalhos inferidos/HighGlobals são evidências da análise do Ghidra;
  conflitos de tipos/layout/alias/inicializadores devem ser preservados e verificados por consumidores originais.
  Exportação completa somente leitura não deve ser considerada declaração de fonte original pronta.
As verificações devem ser combinadas por blocos dependentes; baseline fixado/SHA devem ser reutilizados,
sem remover essas obrigações em prol de uma primeira execução precipitada.

- [ ] Compilar EXE do jogo e executar inicialização de origem com recursos reais.
  Bloqueador: Link do jogo no Run173 possui 267 símbolos não resolvidos / 303 referências;
  erros de compilador e outros erros de linker — 0. Retorno: após eliminação de
  dependências; primeiro inicialização/encerramento, depois quadro, entrada, menus e modos de jogo.
- [ ] Verificar encerramento via WM_CLOSE→GetMessage=0→callback de timer de origem,
  incluindo produtor de tempo 006b7c40. Run086/098 verifica outro ramo de origem de
  mensagem de limpeza 0x466→destroy→join. Retorno: após conexão de callback/inicialização de diagnóstico de origem e fixture de live timer-thread. Run110 encontrou worker
  ignorado 00565270..533e (207 B), setup 565030 original o passa para 55f420.
  Run112 worker restaurado e integrado na 111 (6/6 casos de oráculo); pacote de setup/
  thread/timer 118 integrado na 121: 9 casos, ThreadRecord persistente de 28 bytes,
  retestes de loop de evento/id ao vivo. Vínculos de desligamento do SO 125 verificados por 6 processos filhos.
  123 ciclo de vida (21 casos), 127 wait (16) e 130 stop→wait integração (3) aceitos na 126.
  Agendamento de timer ao vivo e WM_CLOSE ponta a ponta ainda não executados.
- [ ] Verificar contexto de inicialização completo 004d1a90→004d3420→004d1ba0 dentro de app_main.
  Revisão 128/129: original reserva 0x188 bytes de pilha, objeto de 0x180 bytes é passado
  em ECX; chamador antigo descrevia apenas dois DWORDs e fixture ocultava essa discrepância.
  Run129 corrige chamador/armazenamento/ABI; 4 casos de intervalo e 15 casos principais com ctor/dtor
  reais passaram isoladamente. Homologação geral 126 passou: [15 casos principais compostos](../iterations/v2/001-original-recovery/runs/126-event-integration/application-main/verification.json) com ctor/dtor reais.
  Retorno: após grafo completo de analisador/contexto e inicialização ao vivo;
  004d3420 completo (8589 B), vtable e suas dependências reais permanecem abertos.
  Também abrir proprietário/extensão única da string 005e8e50: Run081 encontrou dois
  modelos separados de string vazia; 129 usa proprietário existente sem nova suposição de tamanho.
- [ ] Verificar dispositivos DirectInput reais e caminhos de caps/leitura com cadeia
  de janelas vinculada. Run096 verifica consumidor 0055feb0 com limites controlados;
  fixture nativa de ciclo de vida não conecta todo o grafo de entrada. Retorno: após vínculos.
- [ ] Executar despacho de driver THRASH, transições de tela cheia e quadro real.
  Declarações stdcall e verificações bem-sucedidas de oráculo não comprovam driver real.
  Retorno: após restauração de dependências de driver/serviço/vtable do link do jogo.
- [ ] Reproduzir loop de stream/reprodução/áudio/renderização MAD inteiro. Run094
  restaura apenas consumidor de cabeçalho; não usá-lo como 004dc850 completo.
  Retorno: após restauração de consumidores de stream/decodificador/áudio.
- [ ] Comparar produtores de caminhos 0065b32c/334/360 e serviço de filme 0069ed0c com original.
  Proprietários BSS únicos atuais não comprovam inicialização de origem/ativos válidos.
  Retorno: na restauração dos produtores de inicialização correspondentes. Run116
  encontrou startup_subsystem 004b6ff0: install.txt→tabela de 60 ponteiros 65b2a0..65b38f.
  Run117: 9 casos de oráculo de componentes e 7 verificações compostas confirmaram 49 entradas
  do install.txt real e cinco visões de tabela compartilhadas. Inicialização real com ativos
  ainda não executada; serviço de filme 0069ed0c permanece aberto.
- [ ] Verificar caminhos longos e limites de origem de buffers de pilha em 00427a60/0059dd00.
  Oráculo do Run103 é limitado a prefixos que cabem no buffer local de 100 bytes;
  estouro de origem além desses casos não foi verificado. Retorno: junto
  com produtores de caminho e experimento controlado isolado em x86 original.
- [ ] Confirmar compilador/CRT/flags e correspondência binária onde ela for necessária.
  No-op do Run100 coincide semanticamente, mas RET 0 do MSVC difere de RET original.
  Zero correspondências binárias não é ocultado pelo número de funções recuperadas.
- [ ] Homologação visual e de jogabilidade completa: quadros/transições originais,
  Quick Race, ambas as carreiras, física/danos/IA/economia/salvamentos/som.
  Retorno: após linha de base original funcional; probes atuais não comprovam isso.

- [ ] Concluir formatador original completo: caminhos float/wide/locale, inicialização
  de callback em tempo de execução, efeitos de gravação em arquivo/auxiliar/preparação de descritores e inicialização de lowio.
  Run136 conecta wrapper da produção 108→analisador 124→auxiliares 119→limpeza 132;
  descritor canônico possui 32 bytes, wrapper grava apenas prefixo de 16 bytes original.
  Cauda opaca não inicializada não é zerada; adaptador de teste com seed separadamente.
  Run124: 62 casos após correções de tabela lead-byte, prefixo hexadecimal zero e preenchimento largo.
  Run132: 23 casos, flags são relidas após callback, cauda não é decodificada antes de saída antecipada.
  Run134: 12 casos conectados com wrapper real e divisão/resto sem sinal real da 137;
  Run137: 72 casos em tempo de execução. Essas verificações delimitadas não comprovam CRT/locale ao vivo.
  Run138 aceito no arquivo de produção: 8 intervalos de imagem inicial / 5057 bytes, relocações PE e identidades de ponteiros;
  callbacks não foram executados, nenhuma função foi adicionada. Isso não é inicialização em tempo de execução.
  Retorno: caminho fatal 005abee8→005a2e22, gravador de callback 005a0f5d e seus consumidores float,
  inicializador lowio 005a953e e consumidores de backend reais.
- [ ] Restaurar contrato EAX completo do destrutor base 00525ec0.
  Run135: ramo de alocação nula preserva EAX de entrada no x86 original, C++ tipado
  retorna 0; duas seeds diferentes documentam divergência. Destrutor parcial
  isolado, não conectado na biblioteca/registro de produção. Seis funções completas possuem
  prova delimitada separada em 16 casos, pacote isolado inteiro — 20 contratos delimitados.
  Retorno: comprovar retorno/ABI visível ao chamador de todos os ramos e repetir ctor→contexto→dtor
  composto com dependências vinculadas; vtable 004d3420 permanece aberta.
- [ ] Comprovar domínio de modo com sinal do inicializador de áudio 004a66b0 e grafo de consumidores completo.
  Run131: 8 casos isolados; metade do timer com sinal corrigida (−2→−1), consulta 00565680
  preenche todos os 124 bytes. Índice −9 ainda no intervalo fixado, −10 sai dele;
  guarda original ausente. Não substituir leitura por clamp/throw adivinhado.
  Retorno: rastrear produtores reais de modo e tabelas, verificar valores negativos
  com x86 original e depois grafo geral de inicialização/dispositivo. Pacote isolado.

Proprietário de todos os itens em aberto — o coordenador. Estado no checkpoint 136:
nenhum item ponta a ponta acima foi declarado como concluído. Dispositivo do Run133 possui 10
casos delimitados após correções de sobreposição/célula de ponteiro autoritativa; isso não é verificação
de dispositivo de áudio real. Não há atribuições ativas de executores.

Checkpoint143: 28 novas funções completas aceitas com verificações originais de ABI/estado/efeito.
139 callbacks de memória em pool, 140 bootstrap/fatal de CRT, 141 pontes de aplicação,
142 ciclo de vida de áudio, 144 strings/diálogo, 145 ciclo de vida de rede incluídos na biblioteca geral.
Caminho de erro da CRT: 94 casos conectados com corpos reais de string/diálogo; 17 relatórios
x86 originais recentes / 7928 comparações e 4 casos compostos não encerram inicialização ao vivo.
Novas importações Win32 compiladas e conferidas com IAT, mas fixture de OS de diálogo/erro ao vivo separada
ainda não existe. Retorno: verificar module-name/stdhandle/WriteFile reais e
resolução lazy de user32 sem fatal terminal antes da inicialização completa do jogo.
142 elimina armazenamento duplicado 656868/9 através de aliases. Modo virtual de áudio
não é limitado ao consumidor original 004a6a00: bloqueador de domínio com sinal 131 permanece.
Rastreamento de armazenamento da 145 confirma contagem/tabela 005e8bfc/005e8c00, mas extensão máxima
e proprietário canônico não foram comprovados; tabela de fonte permanece não resolvida.
147/148/149 prontos exigem homologação geral; flags x87 do Unicorn não devem ser consideradas verdade de hardware:
147 contém oráculo de hardware original real separado, aceitação à frente.

Checkpoint153: 35 novos corpos completos aceitos em 147..151. 18 relatórios x86 originais recentes /
5816 comparações (incluindo 256 casos de CPU x87 original real), 4 casos compostos e
8 verificações nativas/link passaram. Vínculos de erro de CRT nativos verificados por fixture de OS real:
caminho/truncamento de módulo, stdhandles, roundtrip de WriteFile/alça inválida e busca de símbolos
user32. MessageBox ao vivo, fatal terminal e inicialização completa da CRT permanecem abertos.
147 preserva 128 discrepâncias de flags do Unicorn; flags de FPU de hardware conferidas com
os 24 bytes originais reais (única relocação de operando zero verificada).
149 rastreamento de leitura do native walker verificado por observador privado PAGE_GUARD/VEH; corpo de produção
sem instrumentação. Cópia de contexto 150 ainda usa limite tipado 005a1a40.
151 identidades de vtable originais 005b4968/70 ainda exigem relocação nativa canônica
e consumidores; identidade literal bruta no oráculo não comprova despacho virtual nativo.
152 lowio, 154 movimentação de contexto, 155 sessões de rede estão em trabalho paralelo.

Checkpoint156: 152/154/155 aceitos, 13 corpos completos / 4394 novos casos. 12 relatórios recentes /
8546 comparações, 4 compostos e 9 verificações nativas/link passaram. 154 cópia exata de memória
compara 130 440 acessos ordenados, incluindo sobreposição/autocópia/alinhamento/DF.
152 vínculos Win32 confirmados por IAT e fixture de OS real, incluindo trava recursiva /
disputa entre threads; isso não é aceitação completa de alça herdada/concorrência ao vivo da CRT.
155 encerramento conecta funções chamadas reais 139/145/148/151; vtable 5b4978 adicionada ao
backlog explícito de relocação nativa junto com 5b4968/70. 157/158/159 executados em paralelo.
Otimização de SHA em lote não altera critérios de comportamento: 3 testes de segurança de mutação/cache
passaram, benchmark 9,2897→2,3805 s / counts_equal=true. Antes do checkpoint executar
scripts/research/audit-v2-proofs.py com o novo --report; fontes de cada arquivo único
são hasheadas uma vez, alterações durante a auditoria são rejeitadas.

## Checkpoint160: Integração CRT/texto/rede

- [x] Aceitar 157/158/159: 43 corpos completos / 10 339 comparações de pacotes; compilação geral de 144 projetos / 270 TUs,
  12 relatórios originais recentes / 14 491 comparações + 4 casos compostos comprovados por componentes,
  10 fixtures nativas/link. Fontes e limites em runs/160-crt-text-workers-integration.
- [x] Corrigir prefixo canônico da tabela de travas da CRT para 26 DWORDs: trava 19 no consumidor de texto,
  trava 25 no definidor de locale; 104 bytes originais/SHA, aliases iniciais, destravar 19/25 lazy/existente verificados.
- [x] Verificar 10 novos adaptadores IAT Win32: preenchimento com zero/liberação de heap, IDs de TLS/thread/último erro,
  isolamento de thread, invólucro Interlocked e incrementos concorrentes.
- [ ] Conectar novos wrappers de CRT ao alocador de blocos pequenos real e motores de locale originais;
  inicialização/falha/concorrência de alocador ao vivo/TLS verificar após 161/162. Costuras de registro
  no oráculo original não comprovam esses caminhos de SO/jogo. Tabela de sinais 005e5ec8 permanece não resolvida.
- [ ] Substituir identidade bruta de vtable de rede original por palavras com relocações nativas canônicas.
  163 comprovou slot0/RTTI/HIGHLOW e lacunas de índice 48ad70/48b340/5a1056; 164 restaura destinos.
  Despacho virtual nativo em produção ainda não aceito. Extensão/proprietários de 5e8e50 e 5e8bfc/5e8c00 abertos.
- [ ] Retornar ao 004d3420 completo e inicialização do jogo. 279 símbolos não resolvidos — fronteira
  atual, não o número total restante. SHA/cache em lote reduz retrabalho, não substitui verificações originais.

## Checkpoint165: Heap Pequeno, Locale e Grupos

- [x] Aceitar 161/162/163: 25 corpos completos / 3909 casos de pacote; 148 projetos / 278 TUs,
  13 relatórios originais recentes / 8082 comparações + 4 casos compostos; 11 fixtures nativas/link PASS.
  161 fixa 15 207 snapshots intermediários / 14 936 pré-limites e alias de cópia de 835 B / 46 HIGHLOW.
  162 fixa 34 exceções protegidas reais, escopos originais/bytes de manipulador/restauração nativa de FS.
- [x] Verificar 15 adaptadores de plataforma com ciclo de vida real de heap/VM Win32,
  LCMapString/conversão de caracteres/classificação/CPInfo. Isso é smoke test de SO, não paridade completa de jogo.
- [x] SHA original em lote no índice manual: 37 funções → 1 leitura/hash binário, alterações concorrentes
  rejeitadas; 9 testes de cache/atualização/índice manual PASS. Relatórios históricos inalterados.
- [ ] Inicialização/concorrência/estouro de pilha de alocador de blocos pequenos/TLS/locale original ao vivo
  com recursos reais permanecem abertos. Fixture nativa de VM não comprova todo o alocador.
- [ ] Aceitar destinos de vtable 164 / saída 166; lacuna de índice 48ad70/48b340/5a1056 complementar por SHA.
  Vptr de construtor bruto e comparações de identidade substituir junto aos proprietários nativos canônicos;
  RTTI e extensão de string vazia compartilhada exigem consumidores originais, dados de fixture não levar para o jogo.
- [ ] EXE completo do jogo: 273 não resolvidos / 308 referências; diagnósticos de compilação/outros 0.
  Após fechamento da fronteira retornar à inicialização 004d3420, modos/carreiras/aceitação visual/ao vivo.
