# Run 418 — fechamento do algoritmo de encerramento de heap e pool (`0059eb20`)

Original: `Porsche.exe`, SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Consulta do índice: `004a54e0`, `0059eb20`, `005678f0`, `0055ec30`, `005699f0`, `0059ee30` em `research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl` e `disassembly.asm`.

## Funções confirmadas (5 corpos, 623 bytes de PE)

1. **`0055ec30` (`printf_shutdown_0055ec30`, 20 bytes, `0055ec30..0055ec43`):**
   Verifica `printf_initialized_006a57cc` (`006a57cc`) e, se for diferente de zero, redefine-o para `0`.
2. **`005678f0` (`application_pool_shutdown_005678f0`, 248 bytes, `005678f0..005679e7`):**
   Se `devices_006a5c7c == nullptr`, retorna imediatamente. Caso contrário, drena a lista auxiliar `free_auxiliary_006a5c38` via `io_pop_00580790`, fechando o descritor no deslocamento `+0x0c` (`file_physical_close_00592290`) e liberando o nó (`file_object_free_0056e640`). Define `file_shutdown_006a5c80 = 1`, percorre as 32 entradas `FileDevice` (passo `0x70`, limite `0xe00`) relendo `devices_006a5c7c` a cada iteração: para dispositivos inicializados, sinaliza `queued_event` (`0055fb30`), aguarda `initialized` zerar via `file_sleep_0055f740(0)`, fecha `queued_event` (`0055fc10`), sinaliza e fecha `completed_event` (`0055fc80`), e descarta as filas `completed` (`+0x40`) e `queued` (`+0x24`) via `network_worker_queue_dispose_005806c0`. Em seguida, libera `free_operation_arena_006a5c54` e `devices_006a5c7c` (`0056e640`), descarta as filas `free_operations_006a5c58` e `free_auxiliary_006a5c38` (`005806c0`), destrói a trava `application_pool_lock_006a5c78` (`heap_lock_destroy_005322d0`) e zera `devices_006a5c7c`.
3. **`005699f0` (`heap_destroy_slot_005699f0`, 72 bytes, `005699f0..00569a37`):**
   Calcula o índice `slot & 0xf` e lê `heaps_006b4f20[idx]`. Se o slot estiver vazio, retorna `0`. Caso contrário, se houver trava em `+0x38`, destrói-a via `heap_lock_destroy_005322d0`, limpa os 64 bytes da estrutura `OriginalHeap` via `heap_fill_0053c290(heap, 0, 0x40)`, zera `heaps_006b4f20[idx]` e retorna `1`.
4. **`0059ee30` (`queue_drain_0059ee30`, 124 bytes, `0059ee30..0059eeab`):**
   A partir do índice de slot negativo ou zero, calcula o registro `state_005e4fe8 - slot * 0x8c + 0x28`, entra na trava no deslocamento `+0x00` (`heap_enter_005322b0`), move todos os nós da lista `+0x08` para a cabeça da lista `+0x04` (encadeamento em `+0x04`), percorre a lista combinada `+0x04` salvando o próximo ponteiro antes de invocar a função de liberação `*(state_005e4fe8 + 8)` (relendo `005e4fe8` a cada nó), zera 16 DWORDs (`0x40` bytes) em `+0x0c..+0x4b` (mantendo `+0x04` e `+0x08` sem escrita adicional) e sai da trava (`heap_leave_005322c0`).
5. **`0059eb20` (`platform_flush_0059eb20`, 159 bytes, `0059eb20..0059ebbe`):**
   Se `application_heap_initialized_006af3f4 == 0`, retorna imediatamente. Chama `application_pool_shutdown_005678f0()` e `printf_shutdown_0055ec30()`, lê `EDI = application_object_heap_006af3fc` e procura-o na tabela de 16 entradas apontada por `heap_selector_005e4fec` (`005e4fec`). Ao encontrar correspondência no índice `i`, chama `queue_drain_0059ee30(-i)`, relê `005e4fec`, zera a entrada `i` e interrompe a busca. Em seguida, chama `heap_destroy_slot_005699f0(EDI)`, libera a arena do slot `EDI` (`006af3b4 + EDI * 4`) via `VirtualFree(..., 0, 0x8000)`, relê `EAX = application_object_heap_006af3fc`, zera a arena do slot `EDI`, zera `application_primary_arena_006af3b4`, redefine `heap_state_005e4fe8` para `default_heap_state_005e3e18` (`005e3e18`) e zera a arena do slot `EAX`.

## Verificação

```powershell
py -3 scripts/research/experiment-v2-heap-shutdown-418.py --finalize-existing --attempt 3
py -3 scripts/research/audit-v2-heap-shutdown-418.py
```

A compilação de `heap_shutdown_418.cpp` com o compilador x86 MSVC (`19.51.36231`) usando `/W4` conclui sem avisos ou erros. O fixture x86 físico (`heap_shutdown_fixture.cpp`) executa os bytes de máquina originais de todas as 5 funções extraídas de `Porsche.exe` (`623` bytes) e confirma paridade exata de traces de chamada, memória e valores de retorno em todos os 8 casos diferenciais.
