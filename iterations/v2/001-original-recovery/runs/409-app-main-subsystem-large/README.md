# Run 409 — original app_main large subsystem cluster

Original `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`:
This run recovers 4 large subsystem initialization and sync routines directly called by `app_main_004b6a50` totaling 2,302 PE body bytes:
1. `0059d650..0059d8c1` (625 bytes) — `cdrom_path_resolve_0059d650`: CD-ROM detection & root path resolver querying `GetModuleFileNameA`, `GetDriveTypeA`, and verifying game data presence (`probe.dat`).
2. `004a88a0..004a8a77` (471 bytes) — `display_mode_probe_sync_004a88a0`: Display mode capability probing and 32-entry display slot synchronization.
3. `004640b0..004642e4` (564 bytes) — `audio_listener_update_004640b0`: 3D audio listener orientation and emitter synchronization updating 0x10c-byte listener slots.
4. `00467470..004676f2` (642 bytes) — `input_subsystem_init_00467470`: User input subsystem and controller device initialization.

All callees remain typed external boundaries. Verified with 10 native differential cases against original physical x86 execution slab (`scripts/research/experiment-v2-app-main-409.py`, `scripts/research/audit-v2-app-main-409.py`).

## Russian / Описание

Восстановлены 4 крупные подсистемные функции инициализации и синхронизации, вызываемые из `app_main_004b6a50`, общим объемом 2302 байта PE:
1. `0059d650` (625 байт) — `cdrom_path_resolve_0059d650`: поиск CD-ROM привода и пути установки игры через `GetModuleFileNameA` и `GetDriveTypeA`.
2. `004a88a0` (471 байт) — `display_mode_probe_sync_004a88a0`: опрос возможностей графических режимов и очистка 32 слотов дисплея.
3. `004640b0` (564 байта) — `audio_listener_update_004640b0`: обновление 3D-позиционирования слушателя и ориентации источников звука в слотах по 0x10c байт.
4. `00467470` (642 байта) — `input_subsystem_init_00467470`: инициализация подсистемы ввода и устройств контроллера.

Все 10 дифференциальных тестов успешно пройдены на физическом x86 CPU memory slab с побитовой идентичностью состояний и трасс вызовов.
