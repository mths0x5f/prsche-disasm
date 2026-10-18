# Run299 — filhos originais da ação de frame

O `Porsche.exe` original, SHA256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`, indexado em `00476710..00476797`, 136 bytes. A consulta de índice `00476710` identifica chamadas de `0047619b` e `00476851`; o registro aceito não tem proprietário exato nem cobrindo. O Run274 tem um pin de entrada de protótipo para este endereço, sem um proprietário de objeto de jogo compilado. A declaração existente do 297 é preservada inalterada.

O `00476710.cpp` implementa `FrameActionBoundary_297::update_00476710(uint32_t)` com o self/ECX original, um argumento DWORD na pilha e RET4. Ele mantém em cache o grupo em `read(self+0xc)+index*0x38` ao longo dos callbacks. Cada iteração relê a tabela de filhos no `group+0x34` em cache, usa passo de filho `0x18`, lê o byte de flag do objeto `+4` antes de qualquer teste de nulo e invoca ou o slot 0 do destrutor virtual com o argumento 1, ou o slot `+0x1c` de update virtual. Após a destruição, ele relê a tabela de filhos, zera exatamente seis DWORDs naquele registro e então relê a contagem do grupo em cache em `+0x14`. No fim, zera essa contagem, inclusive no caminho inicialmente vazio. Mudanças no ponteiro de tabela do self não mudam a identidade do grupo em cache.

Um lote `/MP6` compilou duas unidades de tradução em 1,045 s. O COFF do jogo contém exatamente uma definição e zero símbolos não resolvidos, weak ou common. Bytes de código de máquina originais ocorrem apenas no oráculo da fixture separada, cujos callbacks virtuais são provedores de teste. Nenhum byte original nem provedor de teste é linkeditado no objeto do jogo. O resumo e os recibos reais identificam o fonte, o SHA do COFF, o compilador, as dependências, os pins de ferramenta e o manifest de entrada compartilhado comum.

A fixture nativa comparou 648 estados limitados de memória válida contra todos os 136 bytes originais, sem exigir nenhuma relocação do CALL original. Os casos variam índice de grupo 0/1/2, contagem 0..3, campo `+0x10` zero/não-zero, flags de objeto 0/1/255, caminhos de filhos mistos e mutações, pelos callbacks, da tabela de filhos, da tabela do self, da contagem em cache e do próximo objeto. Cada caso compara a arena inteira de 4096 bytes, os argumentos/ordem dos callbacks, a limpeza da pilha, os não-voláteis preservados e DF=0. Faltas por objeto nulo, ponteiros inválidos arbitrários, contagens/índices enormes e o comportamento do jogo inteiro permanecem fora desta verificação finita. A inicialização e o HOLD de buffer/layout do Run296 continuam em aberto.

```powershell
py -3 scripts/research/experiment-v2-frame-children-299.py --attempt 001 # concluída; não repetir
py -3 scripts/research/audit-v2-frame-children-299.py
```

A primeira invocação do produtor parou antes da compilação porque sua constante privada de diretório de saída estava errada; isso foi corrigido antes da captura. Houve exatamente um lote real de compilador, uma linkedição e uma execução nativa. A auditoria reverifica os recibos e pins preservados sem reexecutá-los. O alvo do jogo não foi reconstruído neste pacote.
