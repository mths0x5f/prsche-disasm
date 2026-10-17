# Notas de Engenharia Reversa do nfs5.exe

Este documento registra a metodologia, as listagens em assembly e as deduções matemáticas obtidas durante a investigação do binário original de `Need for Speed: Porsche Unleashed` (`local/game/nfs5.exe`, versão 3.5 / patch 2019, base PE32 `0x00400000`, MSVC++ 6.0).

---

## 1. Contexto e Premissas

Projetos de código aberto de terceiros (como `OpenNFS/LibOpenNFS` e `CrpLib`) documentam os formatos de geometria dos carros (`.crp`) e arquivos de textura (`.fsh`). No entanto, os formatos de topologia de pistas (`.edg`, `.jnc`), objetos dinâmicos de cenário (`.scn`) e seções de mapeamento de textura (`.map`) estavam ausentes nas fontes públicas.

Para implementar a navegação correta, a geometria viária e o posicionamento de elementos de cenário, foi necessário investigar o código do motor original em `nfs5.exe`.

### Características do Arquivo Executável
- **Formato**: PE32 (x86, 32-bit little-endian).
- **Endereço Base de Carregamento (ImageBase)**: `0x00400000` (sem ASLR).
- **Deslocamento da Seção `.text`**: mapeamento linear $\text{File Offset} = \text{VA} - 0x400000$.
- **Compilador**: Microsoft Visual C++ 6.0 (uso ostensivo de otimizações de divisão inteira por multiplicação por constantes recíprocas).

---

## 2. Localização dos Pontos de Entrada (String Xrefs)

A busca por literais de strings binárias nas seções de dados (`.rdata` / `.data`) revelou os nomes dos formatos:
- A string `"%s.jnc"` localiza-se no endereço VA `0x5d05e4`.
- A string `".edg"` localiza-se no endereço VA `0x5d05fc`.
- A string `".map"` localiza-se nas proximidades do analisador INI no endereço VA `0x440ee0`.

Referências cruzadas (xrefs) a partir da seção de código `.text` conduziram às funções manipuladoras:
- **`0x48789f`**: formatação do caminho do arquivo de junções/bifurcações `sprintf(buf, "%s.jnc", track_name)` e repasse ao gerenciador de recursos `0x481080`.
- **`0x488090`**: preparação do buffer de caminho do arquivo de bordas de pista `sprintf(buf, "%s.edg", track_name)` e chamada da função de leitura `0x487e80`.

---

## 3. Engenharia Reversa do Formato `.jnc` (Junctions — Junções / Bifurcações de Pista)

### 3.1. Listagem em Assembly da Função de Verificação (VA `0x00481080`)

```x86asm
; ecx = ponteiro para o objeto TrackManager
; [esp + 0x18] = nome do arquivo / descritor de .jnc
0x00481080: sub     esp, 8
0x00481083: push    ebp
0x00481084: push    esi
0x00481085: push    edi
0x00481086: mov     edi, dword ptr [esp + 0x18]
0x0048108a: mov     ebp, ecx
0x0048108c: push    edi
0x0048108d: call    0x59ddd0                ; Obter o tamanho do arquivo em bytes
0x00481092: mov     ecx, eax                ; ecx = file_size
0x00481094: mov     eax, 0x38e38e39         ; Constante mágica de divisão por 36
0x00481099: mul     ecx                     ; edx:eax = file_size * 0x38e38e39
0x0048109b: mov     eax, dword ptr [ebp + 0x1c]
0x0048109e: mov     esi, edx                ; esi = 32 bits mais significativos do produto
0x004810a0: shr     esi, 3                  ; esi = esi >> 3 (divisão por 8)
...
0x004810c0: cmp     esi, edx                ; Comparação com o número esperado de junções
0x004810c2: jne     0x481180                ; Divergência -> saída com erro
...
; Leitura dos registros de junções:
0x00481103: add     ebx, 4                  ; Pula índice u32 de 4 bytes, segue para os pesos
0x00481106: mov     dword ptr [esp + 0x1c], ebx
0x0048110e: mov     ecx, dword ptr [edi + eax + 0x20]
```

### 3.2. A Matemática da Divisão por 36 (`0x24`)

O compilador MSVC otimiza a divisão não assinada por uma constante $D = 36$:
$$\frac{2^{35}}{36} = \frac{34359738368}{36} = 954437176.888\dots \approx 0x38E38E39$$

Durante a execução:
1. `mul ecx` multiplica o tamanho do arquivo $N$ por $0x38E38E39$, guardando o resultado no par de registradores `edx:eax`.
2. O registrador `edx` passa a conter $\lfloor (N \times 0x38E38E39) / 2^{32} \rfloor$.
3. A instrução `shr esi, 3` desloca o valor para a direita por mais 3 bits ($2^3 = 8$).
4. O divisor final resultante é: $2^{32} \times 2^3 / 0x38E38E39 = 2^{35} / 0x38E38E39 = 36.000000003 \approx 36$.

**Conclusão**: o tamanho de cada registro de um arquivo `.jnc` é de **exatamente 36 bytes**.

### 3.3. Estrutura do Registro `.jnc` (36 bytes)
| Offset | Tipo | Nome | Descrição |
|---|---|---|---|
| `0x00` | `u32` | `index` | Número ordinal sequencial (0-based) da junção na pista |
| `0x04` | `f32[8]` | `weights` | Até 8 probabilidades/pesos para a IA escolher o caminho na bifurcação |

---

## 4. Engenharia Reversa do Formato `.edg` (Road Edges — Bordas / Limites de Pista)

### 4.1. Listagem em Assembly do Carregador (VA `0x00487e80`)

```x86asm
0x00487e80: sub     esp, 0x34
0x00487e83: mov     eax, dword ptr [esp + 0x38]
0x00487e87: push    edi
0x00487e88: push    0
0x00487e8a: push    eax
0x00487e8b: call    0x59da80                ; Abrir arquivo .edg
0x00487e90: mov     edi, eax                ; edi = descritor de arquivo / buffer
...
0x00487ea4: push    edi
0x00487ea5: call    0x556640                ; Obter tamanho do arquivo em bytes
0x00487eaa: mov     ecx, eax                ; ecx = file_size
0x00487eac: mov     eax, 0x24924925         ; Multiplicador mágico Granlund-Montgomery
0x00487eb1: sub     ecx, 4                  ; Subtrai 4 bytes de cabeçalho!
0x00487eb4: add     esp, 4
0x00487eb7: mul     ecx                     ; edx:eax = (file_size - 4) * 0x24924925
0x00487eb9: sub     ecx, edx
0x00487ebb: shr     ecx, 1
0x00487ebd: add     ecx, edx
0x00487ebf: shr     ecx, 4                  ; Divisão final por 28 (0x1c)
0x00487ec2: je      0x48807c                ; Se registros == 0 -> encerra
...
; Laço sobre os registros de bordas:
0x00487ecb: lea     esi, [edi + 0xc]        ; Ponteiro para o primeiro registro com deslocamento
0x00487ece: mov     dword ptr [esp + 0x18], esi
0x00487ed2: mov     dword ptr [esp + 0x1c], ecx ; ecx = quantidade de segmentos
; Leitura de 6 números em ponto flutuante (p1 e p2 de 12 bytes cada):
0x00487ed6: mov     ecx, dword ptr [esi - 4] ; p1.x
0x00487ed9: mov     edx, dword ptr [esi]     ; p1.y
0x00487edb: mov     eax, dword ptr [esi + 4] ; p1.z
0x00487ede: mov     dword ptr [esp + 0x24], ecx
0x00487ee2: mov     ecx, dword ptr [esi + 8] ; p2.x
0x00487ee5: mov     dword ptr [esp + 0x28], edx ; p2.y
0x00487ee9: mov     edx, dword ptr [esi + 0xc] ; p2.z
...
; Leitura da flag de tipo de superfície:
0x00487f0d: movzx   cx, byte ptr [esi - 8]  ; cx = byte de flags (offset +4 do início do registro)
0x00487f12: lea     edx, [esp + 0x24]       ; edx = array de coordenadas [p1, p2]
0x00487f16: push    ecx                     ; Argumento 2: flags
0x00487f17: push    edx                     ; Argumento 1: ponteiro de pontos
0x00487f18: mov     ecx, eax                ; this
0x00487f1a: call    0x485100                ; Construtor do objeto C++ EdgeSegment
```

### 4.2. A Matemática da Divisão por 28 (`0x1c`) pelo Esquema de Granlund-Montgomery

A divisão por 28 é implementada pelo padrão de compilador padrão para multiplicadores ímpares não-potências de dois:
$$\frac{2^{34}}{28} = \frac{17179869184}{28} = 613566756.57\dots \approx 0x24924925$$

Sequência de instruções:
```x86asm
mul     ecx             ; edx = (N * 0x24924925) >> 32
sub     ecx, edx        ; ecx = N - edx
shr     ecx, 1          ; ecx = (N - edx) / 2
add     ecx, edx        ; ecx = (N + edx) / 2
shr     ecx, 4          ; ecx = ecx >> 4 (divisão por 16)
```
O valor resultante calcula rigorosamente a operação inteira $\lfloor (N - 4) / 28 \rfloor$.

### 4.3. Estrutura do Registro `.edg` (28 bytes)
Cada registro segue imediatamente após o cabeçalho de arquivo de 4 bytes:
| Deslocamento no registro | Tamanho | Tipo | Nome | Descrição |
|---|---|---|---|---|
| `0x00` | 1 byte | `u8` | `flags` | Tipo de superfície/restrição (`0x00`=asfalto, `0x10`=parede/guard-rail, `0x20`=zebra/grama) |
| `0x01` | 3 bytes | `u8[3]` | `padding` | Não utilizados pelo código do carregador (alinhamento em memória) |
| `0x04` | 12 bytes | `f32[3]` | `p1` | Coordenada 3D do início do segmento `[X, Y, Z]` (em metros) |
| `0x10` | 12 bytes | `f32[3]` | `p2` | Coordenada 3D do término do segmento `[X, Y, Z]` (em metros) |

---

## 5. Construtor dos Segmentos Espaciais de Pista (VA `0x00485100`)

Na função `0x00485100`, o motor instancia o objeto C++ que representa a borda do traçado:
```x86asm
0x00485100: mov     eax, dword ptr [esp + 4]
0x00485104: sub     esp, 0x18
0x00485107: lea     edx, [ecx + 0xc]
0x0048510a: mov     dword ptr [ecx], 0x5b484c   ; Gravação do ponteiro de vtable da classe
...
; Cálculo de AABB (Axis-Aligned Bounding Box) via FPU para aceleração das colisões:
0x0048514e: fld     dword ptr [edx]         ; Carrega p1.x
0x00485150: fcomp   dword ptr [esi]         ; Compara com p2.x
0x00485152: fnstsw  ax                      ; Salva status da FPU no registrador AX
0x00485154: test    ah, 1
0x00485157: je      0x48515d
0x00485159: fld     dword ptr [edx]         ; min_x = p1.x
0x0048515b: jmp     0x48515f
0x0048515d: fld     dword ptr [esi]         ; min_x = p2.x
...
```
- A tabela de métodos virtuais (`vtable`) da classe de segmentos de pista fica no endereço **`0x005b484c`**.
- Para cada segmento, o motor calcula em tempo real uma caixa delimitadora alinhada aos eixos (`AABB`), empregada pelo núcleo de física para colisões e retorno do veículo à pista.

---

## 6. Correlação com o Código no Projeto

Os resultados de engenharia reversa foram transferidos para código Rust seguro no crate `nfs-formats`:

- [topology.rs](file:///f:/claude/porsche%20disasm/iterations/004-track-topology/crates/nfs-formats/src/topology.rs):
  - Estrutura `RoadEdge` com os campos `p1: [f32; 3]`, `p2: [f32; 3]`, `flags: EdgeFlags`.
  - Estrutura `Junction` com a lista de pesos `weights: [f32; 8]`.
  - Analisador com verificações de multiplicidade do tamanho `(size - 4) % 28 == 0` e `size % 36 == 0`.
- [track_loader.rs](file:///f:/claude/porsche%20disasm/iterations/004-track-topology/crates/nfs-assets/src/track_loader.rs):
  - Carregamento de bordas na cena e transformação do sistema de coordenadas do NFS5 (`[x, y, -z]`).
- [arcade.rs](file:///f:/claude/porsche%20disasm/iterations/004-track-topology/crates/porsche-viewer/src/arcade.rs):
  - Vinculação do veículo ao traçado e cálculo de elevação/inclinação conforme os segmentos de `RoadEdge`.
