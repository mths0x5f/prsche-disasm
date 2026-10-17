# Etapa Adiada: Som e Cockpit

Plano elaborado em 24/09/2026 após a homologação e encerramento bem-sucedidos de `011-factory-driver` (tag `iteration-011`).
Os snapshots 001–011 finalizados estão congelados e inalterados. O novo snapshot `audio-cockpit (número após homologação das correções)`
é criado pelo script `scripts/new-iteration.py` sem transferência dos runs anteriores.

[Plano geral](../PLAN.pt-BR.md) · [Status atual](../STATUS.pt-BR.md) · [Roteiro](roadmap.pt-BR.md).

## Resultado para o Jogador

1. **Som autêntico**:
   - Reprodução de amostras de áudio originais de motores do diretório `Sound/` do jogo (pitch-shifting conforme RPM do simulador).
   - Sons de troca de marchas, cantadas de pneus em diferentes pisos (asfalto, cascalho, neve), impactos contra barreiras e colisões com oponentes.
   - Reprodução da trilha sonora eletrônica original do jogo.
2. **Interior e instrumentos do cockpit (Cockpit View)**:
   - Visão completa da cabine (visão em primeira pessoa) com volante giratório.
   - Ponteiros animados de tacômetro e velocímetro no painel de instrumentos baseados em dados reais do simulador.
   - Retrovisores funcionais.

## O que Já Está Pronto a Partir da 011

- Modos completos Evolution (eras Classic, Golden, Modern) e Factory Driver (todas as 34 missões).
- Economia completa: compra de carros novos, mercado de carros usados com desgaste, peças e tuning, reparos.
- 142 testes Rust, 0 alertas do Clippy, Rustfmt limpo, testes Playwright Chromium E2E.
- Sintetizador de som WebAudio e beeper WinMM para efeitos básicos.

## Tarefas da Etapa 012

### T01: Engenharia Reversa dos Formatos de Áudio EA Sound
- Análise (parsing) de bancos de sons de motor e ambiente em `GameData/Audio` e `Sound/`.
- Modelo de interpolação de tom e volume conforme as rotações (RPM) do simulador.

### T02: Integração do Motor de Áudio
- Buffers de amostras WebAudio para o navegador e rodio / cpal para execução nativa.
- Áudio espacial de oponentes e efeitos de derrapagem.

### T03: Cockpit 3D e Painel de Instrumentos
- Geometria do interior extraída de `.crp` (volante `Steer`, ponteiros `Needle1`, `Needle2`, painel de instrumentos `ShinyDash`).
- Sincronização do giro do volante e ponteiros com a física de `vehicle.rs`.

### T04: Integração, Regressão e Homologação Ponta a Ponta
- Verificação da sonorização em todos os modos (arcade / simulador 6 DOF).
- Execução completa de regressão de testes, Clippy, Rustfmt, Playwright.
