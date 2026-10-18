# Run 303 — Recuperação do subsistema avançado de app_main

Original `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`: 5 funções avançadas (1.536 bytes) chamadas pela árvore de subsistemas de `app_main_004b6a50`:
1. `00531f90` (278 bytes): `heap_pool_block_free_00531f90` — Desalocador de blocos do pool de heap. Trata coalescência física para frente e para trás, cálculo dinâmico de ponto médio para busca bidirecional no nó sentinela da lista livre, e liberação de lock de thread (`005322c0`).
2. `004a6840` (279 bytes): `display_device_transition_004a6840` — Gerenciador de transição de modo de dispositivo de exibição. Aloca buffer temporário via `heap_pool_alloc_00531ca0`, inicializa 8 entradas `DisplayDeviceEntry`, sonda modo de vídeo via `004a66b0`, inicializa modo via `004ae100`, despacha para subsistemas de vídeo `004a8b80`, `004ae2b0`, `004ab4b0`, `00565890` e libera buffer via `00531f90`.
3. `004b67b0` (311 bytes): `app_loop_pre_tick_pipeline_004b67b0` — Pipeline de engine antes do tick de simulação. Executa `step_00536080` no subsistema de simulação, cascata ordenada de pipes (`0044dfb0`, `0056a490`, `00516950`, etc.), notificações de fase `004a4a70(1/2)`, zera flags globais `g_val_00606ac0/4`, faz polling de input via `0048cdf0` e despacha em cauda para `004691c0`.
4. `004b4b80` (331 bytes): `window_event_filter_dispatch_004b4b80` — Filtro e despachante de eventos de janela e engine. Roteia mensagens com ID `>= 0x21e` para buffers baseados em stride, IDs `>= 0x14e` para tabela de callbacks via `005cc5d0`, e copia payloads de rotas de eventos `0x142..0x147`.
5. `004b68f0` (337 bytes): `app_loop_post_tick_pipeline_004b68f0` — Pipeline de engine após o tick de simulação. Executa pipes pré-registro, cópia de strings e subobjetos, transfere instantâneo de 150 dwords (600 bytes) para `g_data_005e75a0` e executa encerramento do pipeline.

## Verificação
- 11 casos de teste diferenciais executados nativamente em slab físico x86 de memória contra os bytes originais do PE (100% de correspondência exata).
- Recibos de execução e auditoria independente validados com sucesso.
