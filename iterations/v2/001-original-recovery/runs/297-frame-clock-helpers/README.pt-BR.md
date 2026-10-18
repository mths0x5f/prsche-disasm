# Run 297 — Cluster de Funções Auxiliares de Relógio e Encerramento (`0046d960`, `0046d9b0`, `004659e0`, `00471b60`, `004a54e0`, `004a54b0`)

Original `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`: recuperadas 6 funções (199 bytes de corpo PE), responsáveis pelo suporte ao mecanismo de despacho de frames `00413ea0` e pelas etapas de encerramento do laço principal `app_main_004b6a50`.

### Funções Recuperadas
1. **`0046d960` (17 bytes):** `frame_clock_predicate_0046d960` — predicado de tamanho do vetor dinâmico `(vec->end - vec->begin) / 4`.
2. **`0046d9b0` (6 bytes):** `frame_clock_get_items_0046d9b0` — acessor do ponteiro do cabeçalho do vetor `00628168`.
3. **`004659e0` (116 bytes):** `frame_clock_adjust_rate_004659e0` — zera os 9 temporizadores de canal `006280e0..00628100`, valida o flag de canal `00627f40[channel].flags & 1`, e invoca a rotina de reset de canal `00465790(channel, rate)`.
4. **`00471b60` (11 bytes):** `application_main_function_00471b60` — encaminhador do passo de contexto de renderização `00487e20` com `this = 00628960`.
5. **`004a54e0` (5 bytes):** `application_main_function_004a54e0` — thunk de salto para descarga das filas de plataforma `0059eb20`.
6. **`004a54b0` (44 bytes):** `application_main_function_004a54b0` — sequência de descarga e liberação do subsistema `00628c70` (`004b7070`, destrutor `0048ff30`, `free(0059f050)`, e anulação do ponteiro global).

### Validação e Aceite
- O harness nativo x86 em `local/experiments/v2-helpers-297/helpers_fixture.cpp` executa os 199 bytes originais do PE em memória executável confrontando contra o objeto C++ `frame_helpers_297.obj` em 9 cenários diferenciais.
- Aprovadas 9/9 verificações diferenciais rigorosas de registradores, integridade de memória, flags, temporizadores e registros de chamadas externas.
