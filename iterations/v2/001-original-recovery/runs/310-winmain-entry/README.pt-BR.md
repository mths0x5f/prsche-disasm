# Run 310 — Recuperação do WinMain e Inicializadores Estáticos Pré-WinMain

## Resumo em Português
Recuperação e validação diferencial da função de ponto de entrada padrão Win32 (`WinMain`) e dos seus inicializadores estáticos companheiros do CRT a partir de `Porsche.exe` (`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`):
1. `004b66d0..004b66e4` (20 bytes): `winmain_set_heap_size_004b66d0` — configura o limite global do buffer de heap `0x0065b290 = 0x800000` (8 MB).
2. `004b66f0..004b6703` (19 bytes): `winmain_compute_scale_004b66f0` — calcula o fator de escala float recíproco `0x0065b28c = 0x005b24a8 (1.0f) / *(float*)0x0065b290`.
3. `004b6710..004b67a5` (149 bytes): `winmain_004b6710` — ponto de entrada padrão Win32 `WinMain(hInstance, hPrevInstance, lpCmdLine, nShowCmd)`. Inicializa `argv[0] = "AppName"`, divide `lpCmdLine` em tokens por espaços (`0x20`), preenche o array `g_argv_0065b20c` (limitado a 32 argumentos), define `g_argc_0065b294` e invoca `app_main_004b6a50(argc, argv)`.

Total de código PE recuperado: 188 bytes.
Validação diferencial nativa: 12/12 casos aprovados no slab de CPU física x86 contra o código de máquina do PE original, cobrindo strings vazias, múltiplos espaços delimitadores, limitação máxima de argumentos, parsing de parâmetros e retorno de código.
Auditoria independente: `scripts/research/audit-v2-app-main-310.py` confirmada com 100% de sucesso.
Pull Request Upstream: https://github.com/xfynx/prsche-disasm/pull/17 (PR #17).
