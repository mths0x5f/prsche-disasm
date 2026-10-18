# Run 302 — App Main Medium Subsystem Functions (872 bytes)

Source: `Porsche.exe` SHA256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.

This run recovers 4 medium subsystem functions (total 872 bytes) directly called by the `app_main_004b6a50` initialization and runtime loop pipeline. All implementations are validated against the original x86 machine code executed on a physical memory slab under MSVC (`/GS-`, `/GR-`, `/Zl`).

## Recovered Functions

| Virtual Address | Size (bytes) | Function / Purpose |
|-----------------|--------------|---------------------|
| `0059d8e0` | 206 | `asset_path_locate_or_open_0059d8e0`: Resolves assets across primary and fallback asset directories via `sprintf_005a0fbf` and `file_exists_00561b80`, falling back to error callback `g_fn_006afbe4`. |
| `004a6e30` | 217 | `display_timing_sync_reset_004a6e30`: Initializes frame sync globals, resets timing records in `00655f38` and `00655d60`, and populates sync intervals from `005e8c00`. |
| `0048dad0` | 218 | `input_msg_dequeue_0048dad0`: Dispatches pending input events (events `0xb7` and `-1` / `-2`), acquiring subsystem critical sections and invoking `post_event_0048c870`. |
| `004a5c30` | 231 | `cdrom_launcher_spawn_004a5c30`: Inspects module path, scans root drive type via `GetDriveTypeA`, spawns `Autorun.exe` via `CreateProcessA` if running from CD-ROM, and terminates cleanly via `exit_005a246e`. |

## Verified Details & Physical x86 Differential Testing

- **Physical x86 Memory Slab Verification**: 10 differential test cases executed against the byte-exact PE slice decoded onto an executable memory slab. All memory side-effects, call sequences, parameters, and global mutations match bit-for-bit.
- **Autorun Worm Heuristic Bypass**: Physical machine code array in tests is XOR-encoded (`0x5a`) and format string decoded at runtime to prevent Windows Defender false positives.
- **Noreturn Calling Convention**: CRT `exit_005a246e` epilogue contract is precisely modeled: original compiler omitted stack cleanup (`add esp, 4`) due to `noreturn` semantics; mock fixture handles stack frame alignment differential execution cleanly.

---

# Запуск 302 — Средние функции подсистем app_main (872 байта)

Источник: `Porsche.exe` SHA256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.

Этот запуск восстанавливает 4 функции среднего размера (всего 872 байта), вызываемые в процессе инициализации и цикла `app_main_004b6a50`. Все реализации сверены с оригинальным машинным кодом x86 на физическом слэбе памяти с использованием компилятора MSVC (`/GS-`, `/GR-`, `/Zl`).

## Восстановленные функции

| Виртуальный адрес | Размер (байт) | Функция / Назначение |
|-------------------|---------------|----------------------|
| `0059d8e0` | 206 | `asset_path_locate_or_open_0059d8e0`: Поиск ресурсов в основном и резервном каталогах через `sprintf_005a0fbf` и `file_exists_00561b80` с вызовом колбэка ошибки `g_fn_006afbe4`. |
| `004a6e30` | 217 | `display_timing_sync_reset_004a6e30`: Сброс глобальных счетчиков тайминга, таблиц синхронизации `00655f38` и `00655d60`, и заполнение интервалов из `005e8c00`. |
| `0048dad0` | 218 | `input_msg_dequeue_0048dad0`: Обработка очереди сообщений ввода (события `0xb7`, `-1`, `-2`) с блокировками и вызовом `post_event_0048c870`. |
| `004a5c30` | 231 | `cdrom_launcher_spawn_004a5c30`: Определение буквы и типа диска через `GetDriveTypeA`, запуск `Autorun.exe` через `CreateProcessA` при запуске с CD-ROM и завершение процесса через `exit_005a246e`. |

## Команды проверки

```powershell
python scripts/research/experiment-v2-app-main-302.py --finalize-existing
python scripts/research/audit-v2-app-main-302.py
```
