# Run 420: Integração do Heap Shutdown (418) e Frame Root Lifecycle (419) no Target do Jogo

> **Nota de correção:** o bridge **não** define mais a célula `00628960`. Ela vem do objeto do Run 419, que define `frame_service_root_00628960` — o mesmo símbolo que o header congelado do Run 290 declara. Antes, o bridge definia uma célula própria: o contrato de linkedição fechava, mas o consumidor `00471b60` lia um armazenamento que nada escrevia. A reconstrução mantém 188 fontes, 446 referências não resolvidas e zero erros, com o símbolo resolvido pelo 419.
>
> **Correção da contagem (`build-003.json`):** o parser pegava o primeiro nome `(?decorado)` de cada linha LNK, então, para um símbolo faltante com ligação C, registrava *quem chama* (10 linhas). A contagem correta é **423 nomes / 446 referências**: os 348 do Run 417, menos os 8 contratos fechados aqui, mais 83 dependências novas que os Runs 418/419 trazem ao grafo. A auditoria agora reextrai a frontier do log de link e exige que bata com o relatório; ela reprova o `build-002.json` antigo.

## Resumo
- Integradas 188 unidades de translação C++ no grafo real do jogo (`porsche_original_game_link`), compilando 100% de forma limpa no MSVC Win32 (`/MP6`, 0 erros de compilação, 0 outros erros de linker).
- Conectados `heap_shutdown_418.cpp` (5 funções PE, 623 bytes) e `frame_root_lifecycle_419.cpp` (2 funções PE + layout de armazenamento contíguo).
- Fechados 8 contratos não resolvidos do linker da fronteira da Run 417:
  1. `?platform_flush_0059eb20@porsche@@YAXXZ`
  2. `?application_pool_shutdown_005678f0@porsche@@YAXXZ`
  3. `?startup_sequence_call_00471b70@porsche@@YAXXZ`
  4. `?frame_service_root_00628960@porsche@@3IA`
  5. `?app_loop_post_tick_pipeline_004b68f0@porsche@@YAXXZ`
  6. `?application_context_heap_selector_005e4fec@porsche@@YAIXZ`
  7. `?application_context_heap_state_005e4fe8@porsche@@YAPAXXZ`
  8. `?context_selector_pointer_005e4fec@porsche@@YAPAXXZ`
- Fornecida a ponte limpa `entry_bridges_420.cpp` resolvendo acessores de estado/seletor de heap e interligando os limites C/C++.
- Verificados 433 source pins via `v2_shared_manifests.py`.
- Auditoria em lote independente (`audit-v2-game-link-420.py`) PASSOU 100%.
