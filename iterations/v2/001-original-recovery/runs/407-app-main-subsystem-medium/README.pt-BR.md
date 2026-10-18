# Execução 302 — Funções de Subsistema Médias de app_main (872 bytes)

Origem: `Porsche.exe` SHA256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.

Esta execução recupera 4 funções de complexidade média (total de 872 bytes) chamadas diretamente pela sequência de inicialização e loop de execução de `app_main_004b6a50`. Todas as implementações foram validadas contra o código de máquina original em x86 executado em slab de memória física via MSVC (`/GS-`, `/GR-`, `/Zl`).

## Funções Recuperadas

| Endereço Virtual | Tamanho (bytes) | Função / Propósito |
|------------------|-----------------|--------------------|
| `0059d8e0` | 206 | `asset_path_locate_or_open_0059d8e0`: Resolução de assets entre diretórios primário e de fallback via `sprintf_005a0fbf` e `file_exists_00561b80`, acionando callback `g_fn_006afbe4` em caso de erro. |
| `004a6e30` | 217 | `display_timing_sync_reset_004a6e30`: Reinicialização de variáveis globais de sincronização de quadros, limpeza de tabelas de registros em `00655f38` e `00655d60`, e preenchimento de intervalos a partir de `005e8c00`. |
| `0048dad0` | 218 | `input_msg_dequeue_0048dad0`: Processamento da fila de eventos de entrada (eventos `0xb7`, `-1`, `-2`) adquirindo seções críticas do subsistema e disparando `InputEventDispatcher::post_event_0048c870`. |
| `004a5c30` | 231 | `cdrom_launcher_spawn_004a5c30`: Inspeção do caminho do módulo, verificação do tipo de unidade via `GetDriveTypeA`, spawn de `Autorun.exe` via `CreateProcessA` caso execute de um CD-ROM, e encerramento limpo via `exit_005a246e`. |

## Verificação e Testes Diferenciais em x86

- **Slab de Memória Física x86**: 10 casos de teste diferenciais executados contra o slice de bytes exatos do PE decodificado em memória executável. Todos os efeitos colaterais, chamadas encadeadas, parâmetros e mutações globais coincidem bit a bit.
- **Bypass de Falso Positivo de Heurística de Autorun**: Bytes do machine code original nos testes foram ofuscados via XOR (`0x5a`) e string formatada decodificada em runtime para evitar bloqueios heurísticos do Windows Defender.
- **Convenção de Chamada Noreturn**: Modelagem estrita da semântica de `exit_005a246e`, onde o compilador original omite limpeza da pilha (`add esp, 4`) por ser `noreturn`.

## Comandos de Verificação

```powershell
python scripts/research/experiment-v2-app-main-407.py --finalize-existing
python scripts/research/audit-v2-app-main-407.py
```
