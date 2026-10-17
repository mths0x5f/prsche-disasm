# Compilação da Iteração Ativa

A partir da raiz do repositório, execute um único comando:

```powershell
./scripts/build.ps1
```

Por padrão, compila-se a iteração ativa `012-campaign-fidelity` na configuração `release`.
Executável Windows: `local/builds/012-campaign-fidelity/windows/porsche-viewer.exe`.
Pacote Web: `local/builds/012-campaign-fidelity/web`, UI estática mais wasm-bindgen
em `package` (`viewer_impl.js`, `viewer_impl_bg.wasm` e o `.d.ts` acompanhante).

Para as imagens originais da interface, execute uma vez `./scripts/extract-fe-ui.ps1`.
O script lê `local/game/FEData` e cria 119 PNGs em `local/derived/fe-ui`;
o servidor local da 012 ativa os serve em `/assets/`. O cache e os recursos do jogo não entram
no Git ou no pacote web. IDs repetidos dentro do FSH mantêm a regra anterior do último
elemento, a seleção é registrada na saída da extração. Isso ainda não é a restauração de fontes originais,
salas e todas as camadas da interface.

Os resultados exatos e verificações em aberto da iteração ativa estão descritos nos arquivos raiz
[PLAN.pt-BR.md](../PLAN.pt-BR.md), [STATUS.pt-BR.md](../STATUS.pt-BR.md) e no seu [checkpoint run](../iterations/012-campaign-fidelity/runs/001-fidelity-repair/README.md).
Os snapshots 001–011 estão congelados; relatórios e verificações de iterações passadas não comprovam
conformidade total de 1:1 com o original.

Inicialização: `./scripts/launch-viewer.ps1 -Mode desktop|web|native` (escolher um valor).
O desktop adicional usa o mesmo pacote web em uma janela separada do Edge/Chrome;
são necessários um navegador instalado e Python para o servidor local somente leitura.
O helper escuta em uma porta loopback livre, o PID é verificado, os logs de cada inicialização
são salvos em `local/builds/<iteration>/launcher/<id>`. Parada do servidor — Ctrl+C
no console do launcher; fechar a janela do navegador ainda não para o servidor automaticamente.
O Native funciona de forma autônoma: sem argumentos — catálogo; `catalog --game-dir <path>`
seleciona outra fonte; os `inspect/view` anteriores foram preservados.

Os parâmetros `-Iteration`, `-Config debug|release` e `-Target all|native|web` permitem selecionar o snapshot, a configuração ou parte da compilação. O script requer Rust `1.98.1` do `rust-toolchain.toml`, um `Cargo.lock` verificado na raiz da iteração e `wasm-bindgen-cli 0.2.128` no `PATH`; para um novo snapshot, primeiro crie o lock-file com o comando `cargo generate-lockfile --manifest-path iterations/<iteration>/Cargo.toml`. O ambiente pode ser preparado via `./scripts/tool-env.ps1`.

Os arquivos do jogo não são copiados para os resultados da compilação. Todas as iterações usam o `local/game` compartilhado; o caminho pode ser explicitamente indicado com o parâmetro `-GameDir`, e ao iniciar, passar para o viewer o seu `--game-dir <path>` padrão.
