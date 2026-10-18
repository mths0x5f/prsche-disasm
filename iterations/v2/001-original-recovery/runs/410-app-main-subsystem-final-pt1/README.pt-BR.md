# Run 410: Recuperação de dependências de subsistema do app_main (parte 1)

## Resumo em Português

### Visão Geral
O Run 410 conclui a recuperação e verificação diferencial exata de 5 funções essenciais de dependência chamadas diretamente dentro de `app_main_004b6a50` do executável original de varejo `Porsche.exe` (`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`):
1. `0056a680` (38 bytes): `render_counters_init_0056a680` — Reinicialização dos contadores de renderização de quadros.
2. `005a0f98` (39 bytes): `ftol_005a0f98` — Truncamento rápido de float para inteiro de 64 bits (`__ftol`).
3. `00412030` (91 bytes): `audio_parameters_sync_00412030` — Sincronização dos 4 parâmetros de áudio de 16 bits da tabela global.
4. `00414eb0` (196 bytes): `session_state_init_00414eb0` — Reinicialização dos estados globais de sessão e quadros.
5. `004dd600` (1.012 bytes): `texture_subsystem_config_004dd600` — Configuração de superfícies e pipeline de blit de texturas.

Volume total recuperado: **1.376 bytes PE** em **5 funções**.

### Detalhes Técnicos e Descobertas
- **Convenções de Chamada:**
  - `00467fc0` é `__stdcall` com 4 argumentos (`ret 16`).
  - `AllocDesc::init_00403520` é método de membro `__thiscall` com 1 argumento (`ret 4`).
  - `TextureContextObj::sub_00536080` e `sub_00536050` são métodos `__thiscall` sem parâmetros na pilha (`ret 0`).
  - `ftol_005a0f98` utiliza `__declspec(naked)` com instruções x87 (`fnstcw`, `fldcw`, `fistp`) retornando `int64` em `edx:eax`.
- **Verificação Diferencial:**
  - 10 de 10 casos de teste diferenciais passaram com 100% de precisão de bits contra o slab de memória x86 físico do executável original.
  - Carregamento de bytes do PE diretamente do arquivo `Porsche.exe` em tempo de execução elimina falso-positivo estático de antivírus.
  - Script de auditoria independente executado com sucesso.
