# Automação da Restauração

O projeto restaura o código original de *Need for Speed: Porsche Unleashed* (2000).
A base metodológica é a mesma descrita pelo autor no repositório
[prsche-disasm](https://github.com/xfynx/prsche-disasm): descompilação estrita
guiada por binários, oráculos nativos em COFF, linkedição incremental de pacotes
comprovados e rejeição categórica de aproximações ou códigos adivinhados.

O README do autor relata GT4 e God of War II; localmente nós não executamos esses jogos.

## Ciclo Imediato para Porsche

1. Compilar alterações comprovadas e correlacionadas em um único lote de compilador (compiler batch); salvar
   o comando, código de saída (exit code), tempo e log antes da análise dos resultados.
2. Unir pacotes prontos em uma única linkedição. Reutilizar COFFs,
   snapshots de símbolos e verificações SHA; não repetir a compilação devido a erros de relatório.
3. A partir das dependências reais não resolvidas, obter a próxima fila automaticamente:
   proprietário canonical/WIP existente, ABI incorreto, corpo ausente, dados ou
   provedor de plataforma. A prioridade considera o número de consumidores (consumers) e o tamanho do corpo.
4. Antes de uma nova implementação, verificar proprietários aceitos e em andamento (WIP), incluindo intervalos internos (interior ranges).
   Conectar o corpo C++ existente e comprovado. O Run240 demonstra a extração
   mecânica de fragmentos canônicos exatos sem reimplementação do algoritmo.
5. Após o surgimento do EXE jogável, coletar pontos de entrada indiretos reais, transições
   e falhas de provedores durante a execução. Comparar entradas/estados/saídas com o original.
   A linkedição diagnóstica atual de DLL não é a execução do jogo.

O Run241 verifica as raízes de inclusão (include roots) pelo comando de compilador realmente executado.
O Run243 une as alterações prontas. O Run245 forma a fila a partir dos resultados
da linkedição: 442 nomes não resolvidos geraram 440 tarefas, 17 linhas já resolvidas foram excluídas.
Seis verificações de parser/owner passaram. O analisador de runtime-misses aceita uma lista de endereços
com o identificador do EXE de origem; a execução do jogo e a coleta desses endereços ainda não existem.
Comandos e limites de verificação são preservados no README dos runs correspondentes.

Checkpoint atual 264/265: 1125 candidate function VAs + 15 support objects,
419 actual link names → 417 research tasks. O Collector reutilizou 1137 symbol
snapshots e leu apenas 3 novos COFFs; 0 compiles / one archive-link 9,579 s.
Novos corpos podem abrir dependências reais de saída: o número de nomes não resolvidos
não é obrigado a diminuir após cada pacote. A ordem de trabalho deve considerar
o pacote correlacionado de provider/ABI/data, e não apenas o número de funções adicionadas.

Atualização 274/275: 1125 candidate VAs + 19 support objects, 414 actual link names → 412 tasks.
Código de Win32 provider é considerado support. As visões de raw/canonical heap-table possuem um
owner de 64B para três locais de masked MEM4 comprovados; isso não restaura o preceding-region
layout, startup ou entry/liveness de candidate functions navegacionais. 1142 symbol snapshots
reutilizados / 2 new COFFs / 0 compiles; actual archive/link 8,827 s. O próximo source packet é —
files.cpp 00568200/005682a0 e ABI de shared callers, preservando a contenção de 595d0 MOVSX.

### Contrato de Pacote Pronto

O Collector241 espera `original_sha256`, `compiler_sha256`, `input_sha256` e
`validation.json`, que fixa o SHA de um sumário específico. Para dados, são necessários
`kind: original-writable-data` ou `original-readonly-data` e `support_objects`;
ligações exatas são publicadas em um pacote `proven-link-contract` separado.

O Collector268 também aceita `native-platform-provider`: fragmentos de plataforma existentes
exatos, símbolos reais de código/importação e o fechamento observado do compilador. Esse código
é considerado support, e não recovered game function. O suporte de dados/ligações não pode ter
seções executáveis de COFF; namespaced data é permitido sob a mesma validação. O Run268 verificou
dois adaptadores de critical-section do Win32; o Run269 fechou seus actual link names e a ligação raw de free.

Arquivos antigos de manual/corpus/index podem ser pacotes finalizados com SHA fixado (SHA-pinned).
O novo material de navegação é armazenado separadamente em `research/binary-index/supplemental`.
O Run271 utiliza `candidate_entry_va`, `entry_status: unproved`, sem `entry_va`:
isso impede a aceitação automática de um candidato como função comprovada.

Comprovantes reais de compilador/link/nativos (receipts) e logs são salvos antes da análise do resultado;
arquivos de recibo também são incluídos no fechamento (closure). O comando e o exit code não podem ser deduzidos
apenas pela presença do COFF. Para raízes de inclusão entre aspas, são necessários o comando `/I` real e o recibo.
`/sourceDependencies` preserva a compilação paralela `/MP`; `/showIncludes` a desativa.
Novos relatórios e fontes são salvos em UTF-8/LF antes do cálculo do SHA. Bytes históricos
fixados são preservados com precisão. O Run255 demonstra um adaptador somente de metadados
para o formato antigo, sem recompilação e sem alteração dos pacotes já finalizados.

## Experimento Separado com Tradução Automática de x86 para C++

O Run246 testou o primeiro conjunto reduzido: `00590290`, `00590070`, `004930f0`.
A partir de 76 bytes PE exatos / 28 instruções, obteve-se automaticamente C++ com registradores
explícitos, operações de memória, flags e saltos diretos entre rótulos.
Durante a execução do C++ gerado, as instruções não são decodificadas.
375 808 comparações com corpos x86 originais passaram: EAX/ECX/EDX e registradores
preservados, variação relativa de ESP em RET/RET8, CF/ZF/SF/OF e gravações em memória.
Uma auditoria independente verifica o PE, a regeneração do C++, oráculos COFF e recibos.

Um lote de compilador de quatro TUs levou 1,686 s; a bancada nativa — 1,185 s.
A primeira linkedição revelou dependência de memcpy; os mesmos COFFs foram relincados com a CRT,
sem recompilação. Estes são proprietários existentes da restauração principal:
não há novas funções aceitas, a compilação do jogo e o registro não foram alterados.

A cobertura do tradutor sobre a fila de corpos ausentes é verificada separadamente dos três
exemplos estudados. O efeito sobre a velocidade de restauração de grandes partes do jogo ainda
não foi medido.

O Run252 já mediu todos os 85 corpos ausentes da fila atual: nenhum é suportado
integralmente pelo conjunto do Run246; 80 contêm CALL. Com base nesse resultado, o Run253 adicionou
JMP direto externo em três wrappers curtos. 18 432 comparações nativas confirmaram
o estado no ponto de transferência de controle, incluindo o ECX de entrada e a pilha inalterada.
Na ausência de um alvo de VM, o despachante para com `MissingEntry` e registra
o PC de destino original. Três endereços no log possuem `provenance: isolatedVMpilot`;
essas são lacunas do backend experimental de VM, e não uma afirmação sobre corpos nativos
ausentes ou a execução do jogo. Os alvos chamados permanecem incompletos.

O Run257/258 implementou essa expansão: PUSH/POP, aritmética de ESP e CALL/RET com verificação
do PC de retorno original. Três cadeias originais registradas (6 corpos / 104 bytes / 34 instruções)
passaram por 36 864 comparações nativas de registradores, CF/ZF/SF/OF, memória de objetos e pilha.
MissingEntry, PC de retorno corrompido e orçamento de instruções esgotado produzem parada explícita.
A compilação de 8 TUs em um único lote /MP6 levou 2,243 s, a bancada nativa — 2,064 s;
a auditoria independente de 59 pins passou.

O Run260 mediu novamente a fila anterior: 25 dos 85 corpos agora são traduzidos integralmente
de forma sintática. Isso não constitui prova do comportamento dessas 25 funções. A primeira falha
nos 60 restantes está frequentemente associada a MOVSX, OR, deslocamentos (shifts), condições adicionais
de saltos e x87. O próximo passo é testar instruções em fixtures nativas e reunir intervalos originais
correlacionados, mantendo a parada explícita em chamadas/importações desconhecidas. A aceleração
completa até o EXE do jogo ainda não foi mensurada.

O Run262 testou separadamente os cantos de CPU anteriormente não executados: 15 744 casos nativos
sintéticos para ADD/SUB/SBB/NEG de byte/word/32 bits, visões parciais de registradores, PUSH/POP ESP,
POP[ESP], indirect CALL[ESP]/JMP[ESP+4]. 19 oráculos COFF / 70B / 0 relocações coincidiram;
auditoria de 28 pins PASS. Esta é uma validação de infraestrutura de CPU; não há novas funções do jogo aqui.
Ponteiros de código e PC de retorno são normalizados apenas nos slots explicitamente designados da bancada.
A semântica de instruções e flags deve ser conferida com o
[Intel SDM](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html),
e o comportamento de uma função específica — com o Porsche.exe original.

Critérios do experimento:

- O gerador obtém instruções a partir de bytes PE verificados. Uma instrução não suportada
  ou ponto de entrada desconhecido gera um resultado de diagnóstico explícito.
- Sem funções aproximadas, chamada de código de máquina original como implementação
  do jogo ou fallback silencioso que oculte lacunas de tradução.
- Comparam-se registradores, flags essenciais, pilha e alterações de memória, incluindo
  valores de borda. A compilação por si só não constitui homologação.
- Registram-se os custos de tradução e verificação em relação à restauração atual.
  Importações Win32, callbacks e ponteiros de código exigem contratos separados.
- O experimento permanece em `local/experiments`, com gerador e relatório versionados.
  Seu resultado determinará a aplicabilidade a um número maior de funções. Os proprietários
  verificados existentes e o plano para posterior descrição estrutural/porte em Rust são preservados.

Ainda não foram implementados importações/callbacks, carregador completo de memória guest, x87/SSE,
PF/AF/flags indefinidas, exceções e coleta de falhas reais de execução do jogo (runtime misses).
Instruções não suportadas, bytes truncados e saltos fora dos limites das instruções
são rejeitados antes da compilação. Lacunas de tipos e dependências não podem ser consideradas resolvidas pelo simples fato
de que outra arquitetura de processador já foi recompilada com sucesso em outro projeto.
