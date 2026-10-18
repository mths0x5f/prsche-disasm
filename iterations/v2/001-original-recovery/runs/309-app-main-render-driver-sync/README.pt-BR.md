# Execução 309 — Recuperação da Sincronização do Driver de Renderização do App Main (`render_driver_sync_004d3420`)

[English](README.md#english) | [Русский](README.md#русский) | [Português](#português)

---

## Português

### Visão Geral
A Execução 309 recupera `render_driver_sync_004d3420` (8.592 bytes: `0x004d3420..0x004d55b0`) no executável de lançamento de `Porsche.exe` (`ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`).
Esta função representa o **70º e último destino direto de CALL** originado do ponto de entrada de alto nível `app_main_004b6a50`.
Com a conclusão desta execução, **100% de todos os destinos diretos de chamada de `app_main_004b6a50` (70 funções, 26.209 bytes de corpo PE) estão recuperados e verificados de forma exata bit a bit**.

### Detalhes da Função
- **Nome da Função:** `render_driver_sync_004d3420`
- **Endereço Virtual:** `0x004d3420..0x004d55b0`
- **Tamanho do Corpo:** 8.592 bytes
- **Convenção de Chamada:** `__thiscall`
- **Parâmetros:**
  - `this`: ponteiro para a estrutura de estado de sincronização do driver de renderização (512 bytes)
  - `setup_name`: ponteiro para string de configuração (`const char*`, ex: `"gamesetup"`)
  - `save_buf`: ponteiro opcional para buffer de armazenamento de replays/configuração (`0x4000` bytes)
  - `param_4`: flag / parâmetro de modo (`std::int32_t`)
- **Principais Responsabilidades:**
  1. Resolução e inicialização dos submodos de exibição e resoluções DirectDraw / 3D (`0x280 x 0x1e0`, 16-bit).
  2. Análise e despacho de scripts de interface e layout (`gamesetup`, `bottombar.lay`, `serverlist`, `victoryroom`, etc.).
  3. Gerenciamento de modos de sincronização de rede e comunicação multijogador (P2P IP, modem, IPX, LAN).
  4. Coordenação de consultas RTTI da hierarquia de acessores de Front-End (`FEAccessor`, `FEPositionableAccessor`, `FECharVectAccessor`).
  5. Sincronização de parâmetros de cena da engine 3D, drivers de som, fluxos de vídeo de replay e framebuffers do driver.

### Verificação Diferencial
A execução diferencial nativa é realizada por `local/experiments/v2-app-main-309/native-fixture.exe` contra a memória física original do CPU x86:
1. **10/10 Casos de Teste Aprovados (100% exatos bit a bit):**
   - TC 1: `01_quick_setup_p4_1` (`orig_ret = 0, cpp_ret = 0`)
   - TC 2: `02_cold_startup_p4_0` (`orig_ret = 1, cpp_ret = 1`)
   - TC 3: `03_warm_path_sync_flag_1` (`orig_ret = 1, cpp_ret = 1`)
   - TC 4: `04_warm_path_sync_flag_0` (`orig_ret = 1, cpp_ret = 1`)
   - TC 5: `05_resolution_320x240_16bpp` (`orig_ret = 1, cpp_ret = 1`)
   - TC 6: `06_resolution_640x480_16bpp` (`orig_ret = 1, cpp_ret = 1`)
   - TC 7: `07_resolution_800x600_16bpp` (`orig_ret = 1, cpp_ret = 1`)
   - TC 8: `08_resolution_1024x768_32bpp` (`orig_ret = 1, cpp_ret = 1`)
   - TC 9: `09_save_config_buf` (`orig_ret = 1, cpp_ret = 1`)
   - TC 10: `10_full_driver_negotiation` (`orig_ret = 1, cpp_ret = 1`)
2. **Equivalência de Traço e Estado:**
   - Traço de chamadas: 100% idêntico na ordem, tags de funções e argumentos.
   - Valores de retorno: 100% idênticos em todos os 10 casos de teste.
   - Flag global de sincronização (`g_dat_00619800`): correspondência exata bit a bit.
   - Memória de estado do objeto (`s_this`, 512 bytes): correspondência exata bit a bit.
   - Buffer de armazenamento de configuração (`0x4000` bytes): correspondência exata bit a bit.
