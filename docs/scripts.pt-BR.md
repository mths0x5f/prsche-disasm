# Scripts do Projeto e Utilitários

Na pasta `scripts/` encontram-se scripts de serviço para compilação, execução, testes, criação de iterações e engenharia reversa dos recursos originais de Porsche Unleashed.

## Principais Comandos de Compilação e Execução

### `scripts/build.ps1`
Script principal de compilação do projeto.
- **Parâmetros**:
  - `-Iteration <string>`: nome da iteração (por padrão `009-game-shell`, `010-evolution-career`, etc.).
  - `-Config <debug|release>`: perfil de compilação (por padrão `release`).
  - `-Target <all|native|windows|web>`: plataforma de destino (por padrão `all`).
  - `-GameDir <string>`: caminho dos recursos (por padrão `local/game`).
- **Ação**:
  - Configura automaticamente o ambiente através de `tool-env.ps1`.
  - Compila o binário nativo `porsche-viewer.exe` em `local/builds/<iteration>/windows/`.
  - Compila a biblioteca WASM `porsche_viewer.wasm`, copia o diretório estático `web/` para `local/builds/<iteration>/web/` e invoca o `wasm-bindgen` gerando o pacote em `local/builds/<iteration>/web/package/`.
  - Gera os inicializadores `Launch-desktop.cmd`, `Launch-web.cmd`, `Launch-native.cmd`.

### `scripts/launch-viewer.ps1`
Inicializador universal do visualizador para a iteração atual ou indicada.
- **Parâmetros**:
  - `-Iteration <string>`: nome do snapshot da iteração.
  - `-Mode <desktop|web|native>`: modo de inicialização.
    - `desktop`: inicialização do servidor web local `serve-web.py` e abertura de janela dedicada do navegador (Edge/Chrome) em modo app.
    - `web`: inicialização do `serve-web.py` e abertura no navegador padrão.
    - `native`: execução do binário nativo `porsche-viewer.exe` com argumentos `--game-dir`.
  - `-GameDir <string>`: caminho para os recursos do jogo.
  - `-Port <int>`: porta do servidor web (por padrão 8080).

### `scripts/tool-env.ps1`
Configuração das variáveis de ambiente do compilador (PowerShell dot-sourcing: `. ./scripts/tool-env.ps1`).
- Conecta `$env:USERPROFILE/.cargo/bin` ao `$env:PATH`.
- Localiza e conecta toolsets locais em `local/tools` (`wasm-bindgen-cli 0.2.128`, Ninja, CMake, JDK, Ghidra).
- Entra automaticamente no Microsoft Visual Studio Developer Shell (`Enter-VsDevShell -arch=x64`).

### `scripts/new-iteration.py`
Criação de novo snapshot isolado da próxima iteração.
- **Parâmetros**:
  - `--from <source_iteration>`: iteração de origem concluída (por exemplo, `009-game-shell`).
  - `--name <new_iteration>`: novo nome no formato `NNN-name` (por exemplo, `010-evolution-career`).
- **Ação**:
  - Copia recursivamente a árvore da iteração de origem.
  - Exclui arquivos temporários, caches do compilador (`target`, `.cargo-target`), histórico de execuções (`runs`) e `node_modules`.
  - Cria um `README.md` recente e a pasta `runs/` com um `README.md` limpo.

### `scripts/serve-web.py`
Servidor local leve em Python para testes e execução da versão web.
- Serve o diretório da compilação com proteção contra cache (`Cache-Control: no-store`).
- Fornece acesso seguro somente leitura aos recursos de `local/game` através da rota `/game/` e da API `/api/game-files`.
- Suporta tipos MIME para os formatos do jogo: `.wasm`, `.crp`, `.fsh`, `.tpg`, `.edg`, `.jnc`, `.map`, `.scn`.

---

## Scripts Diagnósticos e de Inventário

### `scripts/check-environment.ps1`
Verificação de prontidão do sistema hospedeiro:
- Verifica a presença de `cargo`, `rustc`, `node`, `python`, `git`.
- Verifica versões de compiladores e a presença dos componentes `clippy` e `rustfmt`.

### `scripts/prepare-game.py`
Validação da integridade dos arquivos do jogo em `local/game`.
- Compara os arquivos do jogo com o manifesto `docs/game-manifest.json` (hashes SHA-256 e tamanhos).

### `scripts/inventory-tracks.py`
Inventário e auditoria de todas as 15 pistas do jogo:
- Verifica a presença dos pares obrigatórios `.crp`, `.fsh`, arquivos de topologia (`.edg`, `.jnc`, `.map`) e cenários (`.scn`).

### `scripts/validate-cars.ps1`
Validador em lote de modelos de automóveis:
- Verifica 44 modelos de automóveis no diretório `local/game/Carmodel/` quanto à correta leitura de CRP, texturas FSH e topologia TPG.

### `scripts/inventory-pe.py`
Inventário de seções do executável `nfs5.exe`:
- Analisa cabeçalhos PE, exportações, seções de código e dados para auxiliar na engenharia reversa.

### `scripts/capture-game-modules.ps1`
Coleta de informações sobre módulos e DLLs carregados dinamicamente no jogo original durante a execução.

### `scripts/contact-sheet.ps1`
Geração de folhas de contato (contact sheets) panorâmicas a partir de capturas de tela da renderização de pistas e automóveis para comparação visual.

---

## Testes Automatizados dos Scripts

- `scripts/test_iterations.py`: verifica invariantes da estrutura de pastas de iterações e o funcionamento de `new-iteration.py`.
- `scripts/test_inventory_tracks.py`: testes unitários para o inventariador de pistas.
- `scripts/test_track_cli.py`: testes de linha de comando CLI do inventário.
