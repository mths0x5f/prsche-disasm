# Need for Speed: Porsche Unleashed — restauração do original

O objetivo do projeto é restaurar o jogo a partir dos binários originais em C/C++, compilar
uma versão funcional para Windows/x86, em seguida descrever a estrutura do código e portá-lo para Rust
para plataformas modernas nativas e web. O escopo inclui ambas as carreiras, física,
danos, IA, economia, salvamentos, interface e som.

Os algoritmos são restaurados a partir do desassemblador e recursos originais. O comportamento
é verificado comparando entradas, estado e saídas com o original.
Regras de trabalho: [AGENTS.pt-BR.md](AGENTS.pt-BR.md).

## Resultado atual

Ativa [v2 / 001 — restauração do código-fonte](iterations/v2/001-original-recovery/README.pt-BR.md).
**O jogo completo a partir das fontes restauradas ainda não executa.**

Em 17/10/2026:

- [Candidatos de compilação, Run261](iterations/v2/001-original-recovery/runs/261-canonical-reuse-union/README.md):
  1122 endereços de funções distintos compilados em COFF x86 e combinados em uma biblioteca.
  A linkedição diagnóstica deixa 417 nomes não resolvidos; EXE/DLL não obtido.
  A compilação bem-sucedida desses candidatos ainda não confirma a precisão do comportamento.
- [Integração verificada, Run173](iterations/v2/001-original-recovery/runs/173-float-transport-integration/README.md):
  476 funções totalmente restauradas e 6 consumidores (consumers) parciais;
  24 560 comparações com o original e 12 verificações nativas/link passaram.
  Este é um conjunto verificado separado, e não mais 482 funções além dos 1120 candidatos.

[Tradução estática x86→C++, Run258](iterations/v2/001-original-recovery/runs/258-x86-call-chain/README.md):
três cadeias originais de CALL/RET, 36 864 comparações de registradores, flags, memória e pilha
passaram. Esta é uma verificação do backend experimental, não a execução do jogo completo.

Trabalho imediato — fechar dependências de funções e dados globais,
restaurar convenções de chamadas e compilar o primeiro EXE jogável.
Limite exato e resultados: [STATUS.pt-BR.md](STATUS.pt-BR.md).

## Compilação dos alvos C++ atuais

Necessários Windows x64, Visual Studio 2022 Build Tools com carga de trabalho C++ x86/x64,
Windows SDK e CMake. Para scripts de pesquisa, também é necessário Python 3.
Configuração do ambiente: [docs/building.pt-BR.md](docs/building.pt-BR.md) e
[scripts/tool-env.ps1](scripts/tool-env.ps1).

A partir da raiz do repositório:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-v2.ps1
```

O script compila os alvos CMake existentes do MSVC Win32 na configuração Release.
Resultados: `local/builds/v2/001-original-recovery/`.
Esta é a compilação de módulos restaurados e programas de teste; ela ainda não cria
um jogo totalmente funcional. O conjunto experimental de candidatos é compilado separadamente;
o comando da última união é fornecido em [Run261](iterations/v2/001-original-recovery/runs/261-canonical-reuse-union/README.md).

Binários e recursos originais estão localizados em `local/game/` e são usados
apenas para leitura. Experimentos locais e compilações são armazenados fora do Git.

## Navegação

- [Plano do projeto](PLAN.pt-BR.md) e [plano da iteração ativa](iterations/v2/001-original-recovery/PLAN.pt-BR.md).
- [Índice de binários](research/binary-index/README.md) — primeiro ponto de pesquisa do código original.
- [Validações pendentes](docs/recovery-validation-backlog.pt-BR.md) — fila obrigatória até a homologação final.
- [Automação de restauração](docs/recovery-automation.pt-BR.md) — compilação, feedback e fila de dependências.
- [Trabalho em andamento salvo](docs/recovery-wip.pt-BR.md).
- [Documentação](docs/README.pt-BR.md) e [regras dos executores](docs/agents.pt-BR.md).

## Protótipo anterior v1

Os protótipos em Rust/WebGPU estão salvos em `iterations/`. Os snapshots 001–011 estão congelados.
[012 — campaign fidelity](iterations/012-campaign-fidelity/README.md) permaneceu
incompleto; sua integração foi interrompida após a transição para a restauração v2.
Instruções de execução e controle do protótipo estão no README desta iteração.

## Agradecimentos

Na pesquisa de CRP e FSH foram utilizadas descrições e implementações abertas:
[CrpLib / FSHTool, Denis Auroux](https://auroux.free.fr/),
[OpenNFS / LibOpenNFS](https://github.com/OpenNFS/LibOpenNFS) e
[dima424658 / LibOpenNFS](https://github.com/dima424658/LibOpenNFS).
