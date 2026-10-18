# Execução 307 — Bomba de eventos de quadro do app_main e despachante de eventos do modo UI 3

Original `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`:
Esta execução recupera a função de bombeamento de eventos de quadro invocada diretamente por `app_main_004b6a50` no ponto de chamada `004b6cc4`:
- `004b4da0..004b51d5` (1.078 bytes): `frame_event_pump_004b4da0` — bomba da fila de eventos de quadro, travessia da árvore do modo de tela 3 e mapeamento de elementos filhos, tradução de eventos, embaralhamento Fisher-Yates de elementos caso a interface esteja ativa (`sub_0048caa0`), validação do buffer de string de nome (`0x00657a84`), regulação de atraso (`sub_0053c380(100)`), atualização da máquina de estados do subsistema de entrada e descarga do estado final para `0x005d1740..50` via `sub_00411760`.

Total de bytes do corpo PE recuperados: 1.078 bytes em 1 função.

Os fontes do jogo são `app_main_frame_event_pump_412.cpp` e `app_main_frame_event_pump_412.hpp` neste diretório. Caminhos dos objetos, valores SHA-256, símbolos COFF i386 definidos/indefinidos, raízes de inclusão do MSVC e arquivos `/sourceDependencies` estão registrados em `summary.json` e validados em `validation.json`. O equipamento de teste controlado e o executor diferencial nativo residem em `local/experiments/v2-app-main-412`.

`python scripts/research/experiment-v2-app-main-412.py --finalize --attempt 1` compila com MSVC `/Od /GS- /GR- /EHsc /TP /W4`, vincula contra o equipamento de teste controlado e verifica comportamento 100% idêntico bit a bit contra os bytes originais do PE em slab de memória x86 físico ao longo de 10 casos de teste diferenciais controlados.
`python scripts/research/audit-v2-app-main-412.py` verifica de forma independente todos os 1.078 bytes de corpo, registros de recibos e símbolos COFF.
