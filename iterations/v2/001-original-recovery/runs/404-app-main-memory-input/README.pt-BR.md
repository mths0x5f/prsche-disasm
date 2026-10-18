# Run 404 — Funções Auxiliares de Memória, Sessão e Contexto de Render (`00556640`, `005a246e`, `0059ed90`, `004d1ba0`, `005a177b`, `0059ed40`)

Original `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`: recuperadas 6 funções (230 bytes de corpo PE), chamadas diretamente por `app_main_004b6a50`.

### Funções Recuperadas
1. **`00556640` (8 bytes de corpo PE):** `application_main_function_00556640` — leitura do prefixo do cabeçalho do buffer (`[ptr - 12]`), utilizado para extrair campos de tamanho/capacidade em estruturas de string/buffer.
2. **`005a246e` (17 bytes de corpo PE):** `application_main_function_005a246e` — forwarder de chamada `callee_005a2490(arg0, 0, 0)` com argumentos padrão nulos.
3. **`0059ed90` (19 bytes de corpo PE):** `application_main_function_0059ed90` — wrapper de liberação de memória virtual `VirtualFree(ptr, 0, MEM_RELEASE)`.
4. **`004d1ba0` (46 bytes de corpo PE):** `application_main_function_004d1ba0` / `SessionObject_004d1ba0::destructor_004d1ba0` — destrutor virtual do objeto de sessão: restaura a vtable `0x005b683c`, destrói e libera o sub-objeto no deslocamento `+0xd4` (se existente) e invoca o destrutor base `0x00525ec0`.
5. **`005a177b` (65 bytes de corpo PE):** `application_main_function_005a177b` — wrapper com escopo de lock/estado sobre `g_render_context_5e5508`: adquire contexto (`005a3719`), salva estado (`005a533e`), executa operação `005a4371(ctx, arg0, &arg1)`, restaura estado (`005a53cb`) e libera contexto (`005a376b`).
6. **`0059ed40` (75 bytes de corpo PE):** `application_main_function_0059ed40` — alocador de memória alinhada em página (`VirtualAlloc`): no primeiro acesso consulta `GetSystemInfo`, arredonda `*p_size` para o múltiplo do tamanho de página do sistema e solicita memória `MEM_COMMIT | MEM_RESERVE` com proteção `PAGE_READWRITE`.

### Validação e Aceite
- O harness nativo x86 em `local/experiments/v2-app-main-404/app_main_fixture.cpp` compara 230 bytes originais do PE no segmento executável contra o objeto C++ `app_main_memory_input_404.obj` em 12 cenários diferenciais (2 por função).
- 100% de aprovação: compilação MSVC `/std:c++17`, linkagem sem CRT (`/NODEFAULTLIB`), execução em CPU x86 física sem exceções, registros e efeitos colaterais rigorosamente idênticos.
