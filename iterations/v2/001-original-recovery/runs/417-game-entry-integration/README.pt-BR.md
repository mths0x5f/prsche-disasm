# Run 417 - Integração das Funções Recuperadas de Frame/Loop/AppMain no Target do Jogo

Todas as 185 unidades de tradução C++ no grafo real do jogo Win32 compilaram de forma limpa sob MSVC Win32 (`Hostx64/x86`). Isto integra 29 unidades de tradução adicionais revisadas dos Runs 400..411 ao `porsche_game_entry_bridges`, juntamente com a ponte de encaminhamento `entry_bridges_417.cpp`.

## Principais Conquistas

1. **Contratos Fechados no Linker (21 símbolos)**:
   - **Controle de Quadros do Loop Principal & Temporizadores**:
     - `?application_main_function_00412030@porsche@@YAXXZ` (Run 400)
     - `?application_main_function_00413ea0@porsche@@YAXXZ` (Run 401)
     - `?application_main_function_00414eb0@porsche@@YAXXZ` (Run 400)
     - `?application_main_function_00425780@porsche@@YAXXZ` (Run 400)
     - `?application_main_function_00467740@porsche@@YAXXZ` (Run 400)
     - `?application_main_function_004acb80@porsche@@YAXXZ` (Run 400)
     - `?application_main_function_00563d30@porsche@@YAXXZ` (Run 400)
   - **Encaminhadores de Subsistemas & Ciclo de Vida da Janela**:
     - `?application_main_function_004640b0@porsche@@YAXXZ` (Run 409 - atualização do listener de áudio)
     - `?application_main_function_0048cdf0@porsche@@YAXXZ` (Run 411 - desenho da árvore de telas da UI)
     - `?startup_sequence_call_0048cdf0@porsche@@YAXXZ` (Run 411 - árvore de telas no startup da UI)
     - `?application_network_change_0048e1a0@porsche@@YIXPAX0III@Z` (Run 411 - apresentação de tela da UI)
     - `?application_main_function_004a54b0@porsche@@YAXXZ` (Run 402 - âncora de liberação de heap)
     - `?application_main_function_004a54e0@porsche@@YAXXZ` (Run 402 - entrada de liberação de heap)
     - `?application_main_function_004a88a0@porsche@@YAXXZ` (Run 409 - sincronização de probe do modo de vídeo)
     - `?application_main_function_004b68f0@porsche@@YAXXZ` (Run 408 - pipeline pós-tick do loop principal)
     - `?heap_fill_0053c290@porsche@@YAXPAXII@Z` (Run 405 - preenchimento de heap)
     - `?resource_invalid_module_path_0059d650@porsche@@YAXPBD@Z` (Run 409 - resolução de caminho de CD-ROM)
     - `?game_setup_resource_file_open_0059d8e0@porsche@@YAPAXPBDI@Z` (Run 407 - localização/abertura de recursos de asset)
     - `?splash_progress_load_resource_0059d8e0@porsche@@YAPAXPBDI@Z` (Run 407 - carregamento de recurso do splash de progresso)
     - `?render_display_texture_report_005a177b@porsche@@YAXPBDI@Z` (Run 404 - relatório de textura de exibição)
     - `?startup_sequence_report_005a177b@porsche@@YAXII@Z` (Run 404 - relatório de sequência de startup)

2. **Zero Conflitos de Duplicação**:
   - `00471b60` já havia sido definido no Run 290. A ponte de encaminhamento `entry_bridges_417.cpp` isola `004a54b0` e `004a54e0` do Run 402 sem re-exportar `00471b60`, prevenindo erros LNK2005.

3. **Saúde do Compilador e Linker**:
   - Erros de compilação: **0**
   - Outros erros de linkagem: **0**
   - Source pins: **427** verificados via `v2_shared_manifests.py`.
   - A fronteira atualizada do linker reporta **348 nomes não resolvidos / 381 referências**, rastreando com precisão as dependências filhas e células de dados globais não recuperadas dos subsistemas introduzidos.

## Verificação Independente

```powershell
py -3 scripts/research/audit-v2-game-entry-417.py
```

## Próximos Passos Conectados

- Binding original de encerramento de heap `004a54e0 -> 0059eb20`
- Armazenamento de dados e layout de inicialização da raiz compartilhada de frames (`00628960` e globais associadas).
