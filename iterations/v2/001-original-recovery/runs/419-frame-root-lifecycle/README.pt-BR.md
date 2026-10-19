# Run 419 — Recuperação do Ciclo de Vida da Raiz de Frame (00471b70 & 00471c40)

### Visão Geral
A Run 419 estreita a retenção de longa data (`HOLD`) sobre a célula de armazenamento da raiz de frame `00628960` (veja abaixo o que fica fechado e o que não) e recupera seus dois únicos proprietários no executável `Porsche.exe` (`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`):
- `00471b70..00471c36` (198 bytes de corpo PE): `frame_root_init_00471b70` (`BWorld_Init`) — copia o nome da pista (`00657444` para `00628940`), aloca `0x3c` bytes via `0059ef90`, instancia o objeto de serviço da raiz de frame através de `004874a0` armazenando o ponteiro em `00628960`, formata o caminho em `00628964`, tenta carregar a pista via `004876e0` (com log de erro via `0059fd90` se falhar), calcula parâmetros de contexto a partir de `00628bc0` chamando `005323a0`, e grava o log de conclusão.
- `00471c40..00471c81` (65 bytes de corpo PE): `frame_root_teardown_00471c40` (`BWorld_DeInit`) — emite o log `"BWorld_DeInit..."`, destrói a raiz via `00487590`, libera a memória com `0059f050`, zera a célula `00628960` e emite o log `"done.\n"`.

Total de código PE recuperado: **263 bytes em 2 funções**.

### Resolução da Célula de Armazenamento `00628960`
- A célula é **um** objeto, definido aqui como `frame_service_root_00628960` — exatamente o símbolo que o header congelado `frame_service_290.hpp` da Run 290 declara. Assim o consumidor `00471b60` lê o que `00471b70` escreve. Não existe uma segunda célula para este endereço em nenhum lugar do grafo; a Run 296 do upstream mostrou que um ponteiro isolado perde a relação de memória compartilhada.
- `00628940` (nome da pista, 32 bytes), a célula e `00628964` (caminho formatado) são emitidos numa única seção gravável, na ordem de declaração, então a adjacência é real em vez de apenas descrita. A fixture nativa confere os deslocamentos antes de qualquer caso de comportamento: **raiz − nome = 32**, igual ao original.
- **Lacuna remanescente:** o original tem 4 bytes entre a célula e o buffer seguinte; este toolchain insere padding e entrega **8**. Portanto a cópia sem limite alcançando a célula é reproduzida (Run 301 do upstream), mas o alcance dela até `00628964` não é. A disposição em seção é propriedade do toolchain, não garantia da linguagem, e por isso é conferida em tempo de execução em vez de afirmada.
- Fecha o contrato pendente de `?startup_sequence_call_00471b70@porsche@@YAXXZ` em `porsche_original_game_link`.
- Fecha o destino do pipeline `pipe_00471c40` chamado em `app_loop_post_tick_pipeline_004b68f0`.

### Verificação
- Compilação limpa no MSVC Win32 (`/W4 /Od /Zl`), **0 avisos, 0 erros**.
- Verificação diferencial em slab de memória x86 física (`native-fixture.exe`) com 8/8 casos aprovados.
- Auditoria de aceitação independente (`scripts/research/audit-v2-frame-root-419.py`) **100% PASS**.
