# Formatos de Topologia de Pistas: JNC, EDG e MAP

Neste documento estão registrados os resultados da engenharia reversa das estruturas de topologia da pista de rolamento a partir do executável `nfs5.exe` (endereços VA `0x48789f`, `0x481080`, `0x488090`, `0x487e80`, `0x485100`, `0x440ee0`).

Os arquivos de recursos originais do jogo ficam em `local/game/GameData/Track` e não são adicionados ao Git.

**Esclarecimento de 2026-09-23, auditoria 005:** os tamanhos dos registros e a leitura dos campos são confirmados
por recursos locais/desmontagem; a semântica dos sinalizadores (flags) `.edg` abaixo permanece como
hipótese, e não como uma classificação estabelecida de superfície. Coeficientes de aderência
ainda não podem ser derivados desses valores. O papel do `.jnc` nos checkpoints de volta
não está confirmado. VA `0x440ee0` não está confirmado como o início do analisador MAP:
a decodificação linear começa dentro de uma instrução. Veja a
[auditoria 005](../iterations/005-unified-driving/research/topology-evidence.md).

---

## 1. Arquivos `.jnc` (Junctions — conexões e bifurcações de estradas)

- **Carregador no `nfs5.exe`**: a função `0x48789f` chama `0x481080(manager, "%s.jnc")`.
- **Verificação de tamanho**: o tamanho do arquivo é dividido por 36 (`0x24`) usando uma multiplicação pela constante `0x38e38e39` e deslocamento à direita por 3 bits. O número de registros é estritamente comparado com a quantidade de nós de bifurcação da pista (`cmp esi, edx; jne error`).
- **Tamanho do registro**: exatamente **36 bytes** (`0x24`):
  * `u32 index` — índice 0-based da bifurcação (`0, 1, 2...`).
  * `f32 weights[8]` — até 8 pesos/probabilidades de seleção de direção na bifurcação (por exemplo, em uma bifurcação com duas vias em `alps.jnc`: `1.0, 0.15, 0.85...` — 15% e 85%).
- Todos os 15 arquivos `.jnc` do jogo são estritamente múltiplos de 36 bytes:
  * `skidpad.jnc`: 36 bytes (1 registro)
  * `alps.jnc`: 216 bytes (6 registros)
  * `autobahn.jnc`: 1260 bytes (35 registros)
  * `canyon.jnc`: 612 bytes (17 registros)
  * `castle.jnc`: 864 bytes (24 registros)
  * `coastal.jnc`: 216 bytes (6 registros)
  * `farmland.jnc`: 504 bytes (14 registros)
  * `foothills.jnc`: 216 bytes (6 registros)
  * `forest.jnc`: 216 bytes (6 registros)
  * `industrial.jnc`: 936 bytes (26 registros)
  * `monaco1.jnc`: 144 bytes (4 registros)
  * `monaco2.jnc`: 216 bytes (6 registros)
  * `monaco3.jnc`: 396 bytes (11 registros)
  * `monaco4.jnc`: 360 bytes (10 registros)
  * `monaco5.jnc`: 216 bytes (6 registros)

---

## 2. Arquivos `.edg` (Road Edges — bordas e limites da pista de rolamento)

- **Carregador no `nfs5.exe`**: a função `0x488090` chama `0x487e80(path)`.
- **Verificação de tamanho**: calculada pela fórmula `(file_size - 4) / 28` usando multiplicação inversa por `0x24924925` e deslocamentos de bits.
- **Cabeçalho**: 4 bytes (valor de verificação / CRC / versão). Ignorado pelo carregador (`sub ecx, 4`).
- **Tamanho do registro**: exatamente **28 bytes** (`0x1c`):
  * `u8 flags` — byte de atributos (lido como `movzx cx, byte ptr [esi - 8]`); os seguintes valores são hipóteses anteriores, ainda não comprovadas:
    - `0x00` — borda de pista padrão (asfalto/acostamento)
    - `0x10` — barreira / guardrail / muro de concreto
    - `0x20` — meio-fio / zebra / grama
    - `0x30`, `0x50`, `0x60` — bordas especiais de divisores e túneis
  * `u8 padding[3]` — 3 bytes não utilizados de alinhamento do registro.
  * `[f32; 3] p1` — coordenadas 3D `[X, Y, Z]` do início do segmento (em metros).
  * `[f32; 3] p2` — coordenadas 3D `[X, Y, Z]` do fim do segmento (em metros).
- **Sistema de coordenadas**: as coordenadas originais `p1` e `p2` durante o carregamento na Scene são convertidas pela regra `[x, y, -z]`.
- **Estrutura geométrica**:
  * Os segmentos são conectados sequencialmente (`p2` do anterior coincide com `p1` do seguinte), formando as bordas esquerda e direita da pista de rolamento.
  * No `skidpad.edg`, 167 registros formam um contorno circular fechado de raio ~240 m.
  * Em pistas complexas (`alps.edg` — 7694 registros, `autobahn.edg` — 10555 registros), as bordas descrevem trechos de múltiplas faixas, saídas, pontes e entroncamentos.
- Todos os 15 arquivos `.edg` no jogo satisfazem a fórmula `(size - 4) % 28 == 0`.

---

## 3. Arquivos `.map` (Sections & Texture Mapping)

- **Formato**: arquivo INI de texto; a atribuição anterior do analisador VA `0x440ee0` requer restauração dos limites da função e verificação de xrefs.
- **Seção `[header]`**:
  * `tint` (4 `f32`) — tonalidade de iluminação
  * `ambient` (4 `f32`) — iluminação difusa de fundo
  * `interior` (4 `f32`) — parâmetros de iluminação da cabine
  * `lightdecal`, `interiordiffuse` — parâmetros adicionais de luz
- **Seções `[sectionN]`**:
  * `startslice`, `endslice` — intervalo de fatias (slices) da pista de rolamento.
  * `texture1.open`, `texture1.covered`, `texture2.open` — identificadores FourCC de texturas do arquivo FSH da pista.
  * `texturesize` (`f32`, padrão `6.0f`) — escala de mapeamento da textura.
  * `aspect` (`f32`, padrão `1.0f`) — proporção de aspecto (aspect ratio) do bloco de textura.
