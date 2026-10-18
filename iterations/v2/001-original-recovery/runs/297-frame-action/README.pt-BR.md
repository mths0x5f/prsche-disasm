# Run297 — ação de frame original

O `Porsche.exe` original, SHA256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`, `00476170..00476218` (169 bytes), é restaurado como o método tipado já existente do 290. O registro e as faixas de corpo aceitas não contêm proprietário nesta entrada. A implementação percorre slots de passo 0x38, verifica o ponteiro de objeto em +1c, chama o 00476710 com o índice atual e então usa a tabela, possivelmente alterada, em self+0c. Ela preserva o byte de flag em objeto+4, o ramo de slot+2c, o destrutor virtual (arg 1) / update virtual (+1c) e a semântica da cópia REP de seis DWORDs para frente, inclusive com sobreposição. Os campos de tabela e de contagem são relidos após as mesmas chamadas/escritas do original. Nenhum nome semântico de objeto é reivindicado além dos campos observados.

Um COFF do jogo define apenas `FrameAction_290::invoke_00476170`; o 00476710 continua sendo seu único símbolo externo. O contrato de ECX/um slot de pilha/RET4 dele é confirmado a partir do callee original. Provedores privados de callback e os bytes de máquina originais existem apenas na fixture nativa, nunca no objeto do jogo.

A fixture compara o método C++ com os exatos 169 bytes originais carregados em memória de teste executável privada. Apenas o operando do CALL REL32 original é alterado, para um provedor controlado do 00476710. 480 casos cobrem zero/um/múltiplos elementos, slots vazios, flag 0/1/255, caminhos de destruição/atualização, mudanças de tabela/objeto/contagem durante os callbacks e sobreposição de cópia por identidade/para frente/para trás. São comparados o estado completo da arena de 4096 bytes, a ordem e os argumentos dos callbacks, o RET0, os registradores não-voláteis do x86 e DF=0. O EAX é não especificado para o método void. Essa comparação finita em memória válida não prova o comportamento do jogo inteiro, a equivalência de faltas nem o comportamento com DF=1.

A tentativa 001 compilou as duas TUs, mas sua fixture privada precisava de memcpy/memcmp não resolvidos, sem CRT. Aquela linkedição falha e seu recibo estão preservados. Substituir essas chamadas da fixture por laços de bytes com nomes separados exigiu um segundo lote MP6; a tentativa 002 compilou, linkeditou e passou nas 480 comparações. Isso foi uma correção de fixture, não uma mudança no algoritmo de jogo recuperado. Fontes/includes, objetos, comandos/logs/recibos reais e ferramentas estão fixados; as entradas do repositório usam o manifest imutável comum. A auditoria não faz nenhuma reexecução nativa nem recompilação.

```powershell
py -3 scripts/research/audit-v2-frame-action-297.py
```

A inicialização da raiz 00628960, a implementação do 00476710 e os alvos virtuais reais continuam trabalho separado. Nenhum EXE de jogo nem aceitação visual/em execução é reivindicado.
