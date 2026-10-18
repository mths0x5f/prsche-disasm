# Execução 306 — manipuladores de renderização e apresentação de telas da UI do app_main

Binário original `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`:
Esta execução recupera as 3 funções pesadas de renderização e atualização de telas da interface gráfica invocadas diretamente por `app_main_004b6a50`:
1. `0048cdf0..0048d343` (1.364 bytes): `ui_draw_screen_tree_0048cdf0` — coordenador multifásico de desenho da árvore de telas com 4 fases de sincronização, tratamento de abort/escape e bombeamento de eventos de quadro.
2. `0048dcb0..0048e191` (1.250 bytes): `ui_screen_refresh_0048dcb0` — coordenador de layout de tela e despachante de pacotes de rede entre modos 0, 1 e 2.
3. `0048e1a0..0048e6ec` (1.357 bytes): `ui_screen_render_present_0048e1a0` — renderização de tela, percurso da lista encadeada de nós filhos e apresentação de quadro.

Volume total de código PE recuperado: 3.971 bytes distribuídos em 3 funções.

Os arquivos de código do jogo são `app_main_ui_screen_handlers_306.cpp` e `app_main_ui_screen_handlers_306.hpp` neste diretório. Os caminhos reais dos objetos, hashes SHA-256, símbolos COFF i386 definidos/indefinidos, raízes de include do MSVC ordenadas e dependências `/sourceDependencies` estão registrados em `summary.json` e validados em `validation.json`. O fixture de teste controlado e o executor de teste diferencial nativo residem em `local/experiments/v2-app-main-306`.

`python scripts/research/experiment-v2-app-main-306.py --finalize --attempt 1` compila com MSVC `/Od /GS- /GR- /EHsc /TP /W4`, linka contra o fixture nativo controlado e valida comportamento idêntico bit a bit contra os bytes originais do PE em uma slab física de memória x86 através de 10 casos de teste diferenciais controlados.
`python scripts/research/audit-v2-app-main-306.py` audita de forma independente todos os 3.971 bytes dos corpos de função, registros de execução e símbolos COFF.
