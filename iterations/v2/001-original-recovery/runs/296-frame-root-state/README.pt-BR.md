# Run296 — o armazenamento da raiz do frame permanece em HOLD

O `Porsche.exe` SHA256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39` tem 27 consumidores DWORD diretos indexados de `00628960`, casados exatamente por 27 sítios HIGHLOW originais e 27 padrões de bytes DWORD crus. Não há alvos HIGHLOW dentro dos outros três bytes. Essas varreduras servem de navegação e não estabelecem a ausência, em todo o programa, de aliases computados. Os quatro bytes carregados iniciais são zero; **não existem bytes em arquivo físico** para este endereço: ele pertence à cauda virtual gravável de `.data`, preenchida com zeros pelo carregador do PE.

A inicialização é explícita: `00471b70` aloca `0x3c` através de `0059ef90`, chama o construtor `004874a0` com a alocação em ECX e armazena o EAX retornado em `00471bae`. A falha de alocação armazena zero em `00471bb5`. A limpeza `00471c40` lê a célula, chama `00487590`, libera através de `0059f050` e a zera em `00471c6d`. Nenhuma dessas três entradas de função tem proprietário aceito no registro. O header congelado do 290 apenas declara a célula tipada; nenhuma definição canônica de armazenamento foi encontrada no fonte recuperado. A inicialização e o comportamento do objeto apontado continuam não implementados.

O armazenamento isolado ainda não pode ser aprovado: `00471b72..00471b97` calcula o comprimento da string em tempo de execução no `00657444` mutável e então a copia, incluindo o NUL, com REP MOVSD/MOVSB para `00628940`, apenas 32 bytes antes da célula raiz. Não há limite nessa cópia. Os pontos de corte de bytes originais no Unicorn param antes da alocação, em `00471b99`: comprimentos de origem 0/31 deixam os canários da raiz intactos; comprimentos 32/35/40 sobrescrevem bytes da raiz. Essas entradas controladas demonstram a relação de endereços e os possíveis efeitos de memória, não uma afirmação de que o jogo forneça tais strings. Escritas posteriores sobrescrevem o valor da raiz, mas isso não prova que uma alocação separada preserve os efeitos de memória originais da cópia nem a identidade dos vizinhos.

O buffer de origem é mutável: `00439e25` o limpa, `00439e68` o passa como destino de `005a0fbf` e `004b29ab` instala o endereço dele na célula de registro `005d2ac8`. O próximo passo é rastrear esses escritores e aquele consumidor de registro em busca de um valor máximo imposto de 31 caracteres. Caso contrário, recuperar o layout compartilhado original que cubra o buffer anterior, a raiz e o buffer seguinte em `00628964`. Não instancie um frame service fictício nem substitua o comportamento do construtor por inicialização com zero.

O `evidence.json` registra todos os sítios, bytes de instrução originais, metadados de seção e cinco janelas completas de antes/depois da cópia. O `summary.json` usa o manifest de entrada compartilhado imutável comum; o `validation.json` registra a verificação bem-sucedida dos pins. Nenhuma definição de armazenamento, compilação, fixture nativa ou execução do jogo foi adicionada.

```powershell
py -3 scripts/research/trace-v2-frame-root-296.py # produtor, apenas uma vez
py -3 scripts/research/audit-v2-frame-root-296.py
```
