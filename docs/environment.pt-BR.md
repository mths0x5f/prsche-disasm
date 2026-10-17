# Ambiente de Desenvolvimento

Verificado no Windows x86-64, 16/09/2026. Todas as ferramentas portáteis estão localizadas
em `local/tools`, as configurações de PATH são aplicadas apenas ao processo atual através de
`. ./scripts/tool-env.ps1`.

## Versões Instaladas

- Git 2.49.0.windows.1 (já existente).
- Python 3.12.10, executável `py -3.12` (já existente; `python` era um alias da Microsoft Store).
- Rust/Cargo 1.98.1, rustfmt 1.9.0, Clippy 0.1.98; rustup do usuário.
- Targets: x86_64-pc-windows-msvc e wasm32-unknown-unknown.
- MSVC 14.44.35207, Build Tools em local/tools/BuildTools.
- Windows SDK headers/libs 10.0.26100.0; instalador 10.1.26100.7705,
  instalado no registrado `C:\Program Files (x86)\Windows Kits\10`.
- CMake 4.4.3, Ninja 1.13.2.
- Ghidra 12.1.3 PUBLIC, Temurin JDK 25.0.4.1+1.
- x64dbg snapshot 27/05/2026, executáveis x32 e x64 verificados.
- wasm-bindgen-cli 0.2.128 (versão idêntica ao crate Rust).

## Fontes

- https://rustup.rs/ (rustup-init.exe), https://static.rust-lang.org/
- https://aka.ms/vs/17/release/vs_BuildTools.exe
- https://github.com/Kitware/CMake/releases/tag/v4.4.3
- https://github.com/ninja-build/ninja/releases/tag/v1.13.2
- https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.3_build
- https://github.com/adoptium/temurin25-binaries/releases/tag/jdk-25.0.4.1%2B1
- https://github.com/x64dbg/x64dbg/releases/tag/2026.05.27
- https://github.com/wasm-bindgen/wasm-bindgen/releases/tag/0.2.128

Os arquivos baixados foram salvos em local/tools/downloads. Ghidra, JDK e wasm-bindgen
foram verificados pelo SHA-256 dos lançamentos oficiais; o instalador do SDK possui assinatura
válida da Microsoft. Os valores completos podem ser obtidos via Get-FileHash dos arquivos compactados.

## Instalação e Verificação

O Rust é fixado pelo rust-toolchain.toml de cada iteração. O Rust foi instalado através do
rustup-init com o perfil minimal; os componentes rustfmt/clippy e wasm32 foram adicionados pelo rustup.
O MSVC foi instalado pelo vs_BuildTools.exe padrão em F:. A primeira tentativa do pacote completo
do SDK não concluiu; a repetição instalou apenas DesktopCPPx64/DesktopCPPx86:

```text
winsdksetup.exe /features OptionId.DesktopCPPx64 OptionId.DesktopCPPx86 /quiet /norestart /ceip off
```

O SDK exigiu o diretório registrado existente Windows Kits.
A reinstalação concluiu com código 0. Relatórios do instalador — local/tools/downloads.

Verificações:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-environment.ps1 -Smoke
. ./scripts/tool-env.ps1
cargo check --manifest-path iterations/001-car-viewer/Cargo.toml --target-dir local/builds/001-car-viewer/.cargo-target --locked
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/analyze-game.ps1
```

A verificação do ambiente e o smoke test do Rust passaram. O Bootstrap imprimiu
`Porsche Unleashed bootstrap: windows x86_64`. A análise do Ghidra é executada separadamente;
o resultado é registrado em STATUS.pt-BR.md. Suas configurações de usuário/cache requerem gravação
em AppData, projetos e registros são salvos em local/.

## Limitações

A presença do x32dbg/x64dbg foi verificada por arquivos; o funcionamento interativo do depurador ainda não
foi confirmado. O serviço de automação de UI nativa relatou indisponibilidade de named pipe.
Isso não impede CLI, análise headless e geração de imagens offscreen.
