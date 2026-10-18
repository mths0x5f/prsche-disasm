# Run 298 — Funções Auxiliares do Laço Principal (`0048da60`, `004acb80`, `00425780`, `004b4cd0`)

Original `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`: recuperadas 4 funções (509 bytes de corpo PE / 544 bytes de alocação PE), invocadas diretamente a partir de `app_main_004b6a50`.

### Funções Recuperadas
1. **`0048da60` (99 bytes de corpo / 112 bytes PE):** `application_main_function_0048da60` — adquire o mutex do subsistema `00628c70` (`005322b0`), despacha o evento `0xb7` via chamada membro em `0048c870`, marca a flag `dirty_flag = 1` e libera o mutex (`005322c0`).
2. **`004acb80` (141 bytes de corpo / 144 bytes PE):** `application_main_function_004acb80` — itera sobre os 2 contextos globais de frame `00656aa8`, zera flags de frame, redefine 32 slots de estado e libera os slots ocupados via `00565d60`.
3. **`00425780` (135 bytes de corpo / 144 bytes PE):** `application_main_function_00425780` — percorre o vetor de itens de frame `0060c9f4`, valida se o item está ativo via método virtual do slot 6 (`is_active_00425780`), executa o passo via método virtual do slot 5 (`on_step_00425780`), e compacta a fila `0060c9c4`.
4. **`004b4cd0` (134 bytes de corpo / 144 bytes PE):** `application_main_function_004b4cd0` — decodifica o comprimento do pacote/fluxo de comandos em palavras de 32 bits (DWORD) com base nos opcodes `>= 0x21e` (3 DWORDs), `>= 0x14e` (2 DWORDs), `>= 0x142` (comprimento a partir do cabeçalho), `>= 0x10e` (alinhamento de string para múltiplo de 4 bytes).

### Validação e Aceite
- O harness nativo x86 em `local/experiments/v2-app-main-298/app_main_fixture.cpp` executa os 509 bytes originais do PE em memória executável comparando com o objeto C++ `app_main_helpers_298.obj` em 8 cenários diferenciais.
- Aprovadas 8/8 verificações diferenciais rigorosas de registradores, estruturas de memória, vetores de slots, despacho de eventos e comprimentos decodificados de pacotes.
