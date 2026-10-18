# Run 305: Recovery of app_main subsystem dependencies (part 1)

## English Summary

### Overview
Run 305 completes the recovery and exact differential verification of 5 core subsystem dependency functions called directly within `app_main_004b6a50` from original retail binary `Porsche.exe` (`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`):
1. `0056a680` (38 bytes): `render_counters_init_0056a680` — Render frame counter reset.
2. `005a0f98` (39 bytes): `ftol_005a0f98` — Fast float-to-integer truncation (`__ftol`).
3. `00412030` (91 bytes): `audio_parameters_sync_00412030` — Audio parameters quad-value sync.
4. `00414eb0` (196 bytes): `session_state_init_00414eb0` — Session and frame state initialization.
5. `004dd600` (1,012 bytes): `texture_subsystem_config_004dd600` — Texture subsystem surface & blit setup.

Total recovered byte footprint: **1,376 PE body bytes** across **5 functions**.

### Key Technical Findings
- **Calling Conventions:**
  - `00467fc0` is `__stdcall` with 4 arguments (`ret 16`).
  - `AllocDesc::init_00403520` is a `__thiscall` member method taking 1 argument (`ret 4`).
  - `TextureContextObj::sub_00536080` and `sub_00536050` are `__thiscall` member methods taking 0 stack arguments (`ret 0`).
  - `ftol_005a0f98` is a naked x87 FPU truncation routine returning `int64` in `edx:eax`.
- **Differential Verification:**
  - 10/10 automated differential test cases passed against live original PE bytes on physical x86 CPU memory slab.
  - Zero divergence in state modifications, register outputs, and call traces.

---

## Русское резюме

### Обзор
Выпуск 305 завершает перенос и дифференциальную верификацию 5 функций подсистем, вызываемых напрямую из `app_main_004b6a50` оригинального бинарника `Porsche.exe`:
1. `0056a680` (38 байт): `render_counters_init_0056a680` — сброс счетчиков рендера кадров.
2. `005a0f98` (39 байт): `ftol_005a0f98` — быстрое усечение float в целое число (`__ftol`).
3. `00412030` (91 байт): `audio_parameters_sync_00412030` — синхронизация четверки аудио-параметров.
4. `00414eb0` (196 байт): `session_state_init_00414eb0` — сброс и инициализация состояния сессии и кадра.
5. `004dd600` (1012 байт): `texture_subsystem_config_004dd600` — конфигурация и блиттинг текстурных поверхностей подсистемы.

Суммарный объем восстановленного кода: **1376 байт PE** в **5 функциях**.

### Технические детали
- **Конвенции вызовов:**
  - `00467fc0` имеет конвенцию `__stdcall` с 4 аргументами (`ret 16`).
  - `AllocDesc::init_00403520` реализована как метод `__thiscall` с 1 аргументом (`ret 4`).
  - `TextureContextObj::sub_00536080` и `sub_00536050` используют `__thiscall` без параметров на стеке (`ret 0`).
  - `ftol_005a0f98` оформлена с `__declspec(naked)` для точного сохранения FPU-пролога и выхода в регистрах `edx:eax`.
- **Дифференциальная верификация:**
  - 10 из 10 автоматических тестов успешно пройдены на физическом x86-слабе оригинального бинарника.
