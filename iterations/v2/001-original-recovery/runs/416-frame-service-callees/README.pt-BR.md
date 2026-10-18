# Run 416 — funções chamadas pelo frame service

`Porsche.exe` original, SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.

Este run fecha a fronteira externa que o Run 290 deixou aberta. O
`frame_service_290.hpp` declarava como não recuperadas as três funções chamadas pelo
ciclo `00487e20` e também a célula de armazenamento `00628960`. O Run 416 recupera os
três corpos (305 bytes de código PE), de modo que o consumidor do Run 290 passa a
linkar contra definições reais para eles. A célula de armazenamento permanece em
HOLD — veja abaixo.

Numerado como 311 porque o slot 310 já está ocupado no `main` pelo `415-winmain-entry`.
O PR upstream desta branch foi aberto com o número 310.

## Recuperado

| Alvo | Faixa | Bytes | SHA-256 do corpo |
| --- | --- | --- | --- |
| `advance_00423840` | `00423840..00423882` | 67 | `8b75f5520e19b4380d2165f85398dfb9d39e71290de039430625dd5d7f6ef911` |
| `invoke_00482e50` | `00482e50..00482e94` | 69 | `ebc3fb1a31138079e8fc8ff47b5a7e6309bd69c607b7e14b27fb4bf763d1446b` |
| `invoke_00476170` | `00476170..00476218` | 169 | `0a4456508d1f9ad2a42da22096714106580b57fa5b16aa299fe2644f515b5d3e` |

- `00423840` é o sucessor em ordem na árvore, sobre `+0x04` pai, `+0x08` esquerda,
  `+0x0c` direita. `ECX` aponta para o único slot de ponteiro de nó do iterador.
- `00482e50` avança o temporizador `+0x04` de cada elemento ativo do vetor de passo
  `0x38` em `this+0x40`. A contagem em `this+0x18` e o ponteiro base são relidos a
  cada iteração, exatamente como no original.
- `00476170` executa a transição de ciclo de vida por elemento: chama `00476710` e
  então ou destrói pelo slot `0x00` da vtable e copia seis dwords de `element+0x1c`
  para `*(element+0x34)`, ou despacha o slot `0x1c`; `element+0x08` é zerado sempre.

A comparação de `00482e50` foi reproduzida como `!(timer > limite)`, que corresponde ao
`fcomp` seguido de `test ah,0x41` do original — um teste de `C0|C3`, ou seja "não maior",
que também é tomado no caso não ordenado. Assim um temporizador NaN recebe o ajuste
igual ao original. Escalares somente-leitura verificados contra os bytes da imagem:
`005b47d8` = `8000.0f` e `005b2764` = `10000.0f`.

## Célula de armazenamento 00628960

Uma varredura dos operandos HIGHLOW em `.text` encontra exatamente três escritas na
célula, em dois proprietários:

- `00471b70` (inicializador): `00471bae` grava o objeto construído por `004874a0`
  depois de `operator new(0x3c)`; `00471bb5` grava `0` quando a alocação falha.
- `00471c40` (encerramento): `00471c6d` grava `0` depois de destruir via `00487590`
  e liberar via `0059f050`.

**Nenhum dos dois proprietários foi recuperado aqui, e a célula deliberadamente não é
definida.** Este run contribui apenas com a prova de propriedade.

Uma definição isolada inicializada com zero não seria fiel. A cópia de string em
`00471b72..00471b97` é um `REP MOVSD` sem limite para `00628940`, que fica apenas 32
bytes antes da célula, portanto no original uma string de origem com 32 bytes ou mais
alcança o armazenamento da célula. Objetos C++ separados perdem essa adjacência. A
célula permanece, então, uma fronteira de linkedição não resolvida até que o layout
original compartilhado que cobre `00628940`, a célula e `00628964` seja recuperado
em conjunto.

## Validação

12/12 casos diferenciais controlados sobre um slab de memória x86 física contendo os
corpos originais. A fixture corrige os dois operandos HIGHLOW de `00482e50` e o único
`CALL 00476710` relativo de `00476170`, e então roda cada caso duas vezes sobre a mesma
memória de cena: primeiro os bytes originais, depois o C++ recuperado. Um caso só passa
quando os bytes do estado final e o traço de chamadas são idênticos.

```
python scripts/research/experiment-v2-frame-service-416.py --finalize --attempt 1
python scripts/research/audit-v2-frame-service-416.py
```

O experimento compila com MSVC `/Od /Oi /Gy /GS- /GR- /EHsc /TP /W4 /Zl` (sem
avisos), linkedita com `/NODEFAULTLIB /ENTRY:entry /MACHINE:X86` e reporta 12/12
casos. A auditoria re-deriva as faixas dos corpos, o `RET` terminal, os valores
SHA-256 dos corpos, os dois escalares e as três escritas na célula de armazenamento a
partir da imagem de varejo em vez de a partir do `summary.json`, e verifica os
símbolos COFF e os recibos de build.

A recuperação define exatamente os três símbolos de função que eram a fronteira do
Run 290: `advance_00423840`, `invoke_00482e50` e `invoke_00476170`. Ela deixa
indefinidos o `00476710`, os dois escalares somente-leitura e o
`frame_service_root_00628960`; a fixture fornece os dois primeiros, e uma build do
alvo do jogo ainda precisa fornecê-los.

A validação da fixture foi, ela mesma, conferida por controle negativo: quatro
mutações separadas dos fontes recuperados (remover a guarda final de `00423840`, usar
`<` em vez de "não maior" em `00482e50`, remover a limpeza de `element+0x08` e copiar
cinco dwords em vez de seis) falharam somente nos casos que deveriam detectá-las.

## Limites

- `00476710` (136 B), `00471b70` (198 B), `00471c40` (65 B), `004874a0` (230 B) e
  `00487590` seguem não recuperados.
- `00476170` lê o flag do objeto em `+0x04` antes da verificação de nulo que vem
  depois, portanto o original desreferencia incondicionalmente o ponteiro relido após
  `00476710`. A recuperação preserva essa ordem em vez de antecipar a verificação.
- Campos que estes três corpos nunca leem estão nomeados `opaque_*`; seus tipos não
  ficam estabelecidos aqui.
