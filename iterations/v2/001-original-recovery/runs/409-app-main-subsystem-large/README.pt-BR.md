# Run 409 — Cluster de Grandes Subsistemas de app_main

Original `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`:
Este run recupera 4 rotinas grandes de inicialização e sincronização de subsistemas chamadas diretamente por `app_main_004b6a50`, totalizando 2.302 bytes de corpo PE:

1. `0059d650..0059d8c1` (625 bytes) — `cdrom_path_resolve_0059d650`: detector de unidade de CD-ROM e resolução da pasta raiz do jogo através de `GetModuleFileNameA`, `GetDriveTypeA` e validação do arquivo de presença de dados (`probe.dat`).
2. `004a88a0..004a8a77` (471 bytes) — `display_mode_probe_sync_004a88a0`: sondagem de capacidades de modos de exibição e sincronização dos 32 slots de display.
3. `004640b0..004642e4` (564 bytes) — `audio_listener_update_004640b0`: sincronização 3D de orientação do ouvinte e emissores de áudio nos slots de 0x10c bytes.
4. `00467470..004676f2` (642 bytes) — `input_subsystem_init_00467470`: inicialização do subsistema de entrada do usuário e criação/configuração dos dispositivos de controle.

Todos os alvos chamados permanecem como fronteiras externas tipadas. Verificado com 10 casos diferenciais nativos diretamente contra a slab física de execução da CPU x86 (`scripts/research/experiment-v2-app-main-409.py`, `scripts/research/audit-v2-app-main-409.py`).
