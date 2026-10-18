# Run298 - algoritmos de frame no alvo real do jogo

Todas as 156 unidades de tradução C++ do grafo real do jogo Win32, de oito projetos, compilaram. Isso inclui quatro funções recuperadas dos runs 295/297/299 e as duas células float somente-leitura exatas do 300. A entrada normal do Run102 e o grafo de fontes canônico estão preservados; callbacks privados de teste e oráculos de bytes originais estão excluídos.

A linkedição agora reporta **266 nomes não resolvidos / 302 referências**, abaixo dos 269/305 do 293. Os três contratos fechados são o iterador 00423840, a ação 00476170 e a cauda 00482e50. O novo filho 00476710 e os provedores de dados float compõem sem expor novos símbolos não resolvidos. Esta é uma build de fontes nova, não uma contagem de candidatos WHOLEARCHIVE. **Nenhum EXE do jogo existe nem foi executado.**

Os pacotes comparam 441 bytes de função original em 1139 casos nativos finitos (295: 11, 297: 480, 299: 648). O Run300 prova 8 bytes de dados somente-leitura e 35 leituras originais indexadas. Essas verificações estabelecem os algoritmos/dados limitados declarados, não a fidelidade completa do jogo nem o comportamento real dos alvos virtuais.

Os runs 296 e 301 preservam um HOLD separado para o armazenamento da raiz: o consumidor original de TRACK_NAME permite strings controladas com mais de 31 caracteres, e a cópia original seguinte cruza o 00628960. Um ponteiro fictício isolado perderia essa relação de memória compartilhada. A inicialização da raiz e o layout compartilhado original continuam não recuperados.

A configuração 001 passou. A build 001 parou em "Checking Build System" dentro do sandbox e seu log/recibo está retido. A build 002 aprovada, fora do sandbox, compilou todos os 156 fontes em 9,642 s, com 389 pins de fonte/dependência inalterados, zero erros de compilador e zero outros erros de linkeditor. Permanecem três avisos inalterados de redefinição de macro de plataforma. Os fechamentos de fonte usam um manifest imutável comum para os dois resultados de build. A auditoria independente em lote reusa um único leitor entre os pacotes e verifica recibos, bytes originais, nomes de arquivos realmente compilados, provedores COFF novos e a diferença precisa de fronteira. Ela não faz nenhuma reexecução nativa nem compilação.

```powershell
py -3 scripts/research/audit-v2-frame-game-integration-298.py
```

O `CMakeLists.txt` é a entrada reprodutível de fontes. O produtor da build exige uma nova tentativa única; não repita tentativas concluídas. O estado nativo de inicialização, os provedores de render/recursos/entrada, a primeira tela e a jogabilidade completa continuam em aberto. O próximo trabalho conectado é o vínculo original de encerramento de heap 004a54e0→0059eb20 e o layout compartilhado da raiz de frame; o REA está sendo avaliado como auxílio de navegação, não como substituto das verificações de equivalência.
