# Run 300 — Cluster de temporizador do app_main, resolução de tela, vetor SIMD/MMX e pacote de stream

## Português (Brasil)

Original `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`:
Este run recupera quatro funções autênticas (420 bytes de corpo PE), invocadas diretamente por `app_main_004b6a50` ou por sua sequência imediata de inicialização, vídeo e temporizadores:

1. `0053c290` (77 bytes): Despachante de operações vetoriais com ramificação por recursos de CPU SIMD/MMX. Testa o sinalizador 3DNow (`005deb1c`), depois o sinalizador MMX (`005deb18`), invocando as rotinas especializadas de transformação `005b0b00` ou `005b0a40`, ou recorrendo à rotina genérica `005b0980`.
2. `004b6660` (99 bytes): Despachante de serialização de pacote de fluxo e descarga de buffer. Aloca buffer temporário (`00531ca0`), inicializa cursor de contexto na pilha (`004b5ee0`), serializa a carga útil do pacote (`004b60d0`), grava terminador zero de 4 bytes, descarrega o fluxo (`00569640`) e retorna o ponteiro do buffer.
3. `00467fc0` (112 bytes): Comutador de resolução de exibição e modo de vídeo (`DisplayManager_00467fc0::set_resolution_00467fc0`). Compara as dimensões ativas (`00619784`, `00619788`, `0061978c`), encerra precocemente se as resoluções forem idênticas ou altera o modo via `00468030` (modo 0 em tela cheia ou resultado de `find_display_mode_005376c0` em modo janela).
4. `005366e0` (132 bytes): Despachante do subsistema de temporizadores periódicos do jogo. Compara `g_timer_last_tick_0069de24` com `g_current_time_006b7c40`, itera pela tabela de 16 temporizadores `g_timer_table_0069dd20` (16 bytes por entrada: callback, period, next_fire_time, is_running), despacha callbacks pendentes com o tempo decorrido, avança `next_fire_time` e retorna o OU binário dos resultados retornados pelos callbacks.

### Verificação Física em CPU x86
- Os bytes de código de máquina capturados foram testados em `local/experiments/v2-app-main-300/native-fixture.exe` contra a sequência original de bytes em slab de memória executável.
- Todos os 10 casos de teste diferenciais passaram com correspondência exata bit a bit.
- Validado pelo script de auditoria independente `scripts/research/audit-v2-app-main-300.py`.
