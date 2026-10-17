# Notas de Engenharia Reversa do nfs5.exe

Este documento registra a metodologia, os trechos em assembly x86 e as deduções matemáticas obtidas na análise do binário original de `Need for Speed: Porsche Unleashed` (`local/game/nfs5.exe`, versão 3.5 / patch 2019, base PE32 `0x00400000`, compilado com MSVC++ 6.0).

---

## 1. Contexto e Motivação

Projetos open source de terceiros (como `OpenNFS/LibOpenNFS` e `CrpLib`) já documentavam os formatos 3D dos carros (`.crp`) e pacotes de texturas (`.fsh`). No entanto, os formatos de **topologia das pistas** (`.edg`, `.jnc`), **objetos dinâmicos de cenário** (`.scn`) e **mapeamento de texturas** (`.map`) eram completamente desconhecidos publicamente.

Para implementar a navegação correta dos carros da IA, a geometria da estrada e as decorações do cenário, foi necessário dissecar o código do motor original dentro do `nfs5.exe`.

### Características do Executável:
- **Formato**: PE32 (x86, 32-bit little-endian).
- **Endereço Base (ImageBase)**: `0x00400000` (sem ASLR na época).
- **Offset da seção `.text`**: Mapeamento linear direto:
  $$\text{Offset no Arquivo} = \text{VA} - 0x400000$$
- **Compilador Original**: Microsoft Visual C++ 6.0 (uso pesado de otimizações de divisão inteira por multiplicação por constantes recíprocas / *magic numbers*).

---

## 2. Localização dos Pontos de Entrada (String Xrefs)

A busca por strings nas seções de dados (`.rdata` / `.data`) revelou os nomes dos formatos:
- A string `"%s.jnc"` está no endereço VA `0x5d05e4`.
- A string `".edg"` está no endereço VA `0x5d05fc`.
- A string `".map"` está nas proximidades do parser de arquivos INI em VA `0x440ee0`.

As referências cruzadas (*xrefs*) a partir do código `.text` levaram às funções responsáveis:
- **`0x48789f`**: Monta o caminho do arquivo de cruzamentos: `sprintf(buf, "%s.jnc", track_name)` e passa para o gerenciador de recursos em `0x481080`.
- **`0x488090`**: Monta o caminho dos limites de pista: `sprintf(buf, "%s.edg", track_name)` e chama o leitor em `0x487e80`.

---

## 3. Engenharia Reversa do Formato `.jnc` (Junctions — Bifurcações e Cruzamentos)

### 3.1. Trecho Assembly da Função de Leitura (VA `0x00481080`)

```x86asm
; ecx = ponteiro para o objeto TrackManager
; [esp + 0x18] = nome do arquivo / descritor .jnc
0x00481080: sub     esp, 8
0x00481083: push    ebp
0x00481084: push    esi
0x00481085: push    edi
0x00481086: mov     edi, dword ptr [esp + 0x18]
0x0048108a: mov     ebp, ecx
0x0048108c: push    edi
0x0048108d: call    0x59ddd0                ; Obtém o tamanho do arquivo em bytes
0x00481092: mov     ecx, eax                ; ecx = file_size
0x00481094: mov     eax, 0x38e38e39         ; Constante mágica para divisão por 36
0x00481099: mul     ecx                     ; edx:eax = file_size * 0x38e38e39
0x0048109b: mov     eax, dword ptr [ebp + 0x1c]
0x0048109e: mov     esi, edx                ; esi = 32 bits mais significativos
0x004810a0: shr     esi, 3                  ; esi = esi >> 3 (divide por 8)
...
0x004810c0: cmp     esi, edx                ; Valida o número de junções esperadas
0x004810c2: jne     0x481180                ; Erro se o tamanho não bater
...
; Loop de leitura das junções:
0x00481103: add     ebx, 4                  ; Pula o índice u32 de 4 bytes e vai para os pesos
0x00481106: mov     dword ptr [esp + 0x1c], ebx
0x0048110e: mov     ecx, dword ptr [edi + eax + 0x20]
```

### 3.2. A Matemática da Divisão por 36 (`0x24`)

O compilador MSVC substitui a divisão lenta por 36 por uma multiplicação por fração binária:
$$\frac{2^{35}}{36} = \frac{34359738368}{36} = 954437176.888\dots \approx 0x38E38E39$$

1. `mul ecx` calcula $N \times 0x38E38E39$. O registrador `edx` recebe o resultado dividido por $2^{32}$.
2. `shr esi, 3` divide por mais $2^3 = 8$.
3. Total: divisão por $2^{35} / 0x38E38E39 \approx 36$.

**Conclusão**: Cada registro de bifurcação no arquivo `.jnc` tem **exatamente 36 bytes**.

### 3.3. Estrutura do Registro `.jnc` (36 bytes)
| Offset | Tipo | Nome | Descrição |
|---|---|---|---|
| `0x00` | `u32` | `index` | Índice sequencial da bifurcação na pista |
| `0x04` | `f32[8]` | `weights` | Até 8 probabilidades/pesos para a IA escolher qual caminho seguir |

---

## 4. Engenharia Reversa do Formato `.edg` (Road Edges — Bordas da Pista)

### 4.1. Trecho Assembly do Carregador (VA `0x00487e80`)

```x86asm
0x00487e80: sub     esp, 0x34
0x00487e83: mov     eax, dword ptr [esp + 0x38]
...
0x00487ea5: call    0x556640                ; Obtém tamanho do arquivo em bytes
0x00487eaa: mov     ecx, eax                ; ecx = file_size
0x00487eac: mov     eax, 0x24924925         ; Multiplicador mágico de Granlund-Montgomery
0x00487eb1: sub     ecx, 4                  ; Subtrai 4 bytes de cabeçalho!
0x00487eb4: add     esp, 4
0x00487eb7: mul     ecx                     ; Multiplica (file_size - 4) * 0x24924925
0x00487eb9: sub     ecx, edx
0x00487ebb: shr     ecx, 1
0x00487ebd: add     ecx, edx
0x00487ebf: shr     ecx, 4                  ; Divisão final por 28 (0x1c)
0x00487ec2: je      0x48807c
...
; Leitura dos 6 floats de coordenadas (p1 e p2):
0x00487ed6: mov     ecx, dword ptr [esi - 4] ; p1.x
0x00487ed9: mov     edx, dword ptr [esi]     ; p1.y
0x00487edb: mov     eax, dword ptr [esi + 4] ; p1.z
0x00487ede: mov     dword ptr [esp + 0x24], ecx
0x00487ee2: mov     ecx, dword ptr [esi + 8] ; p2.x
0x00487ee5: mov     dword ptr [esp + 0x28], edx ; p2.y
0x00487ee9: mov     edx, dword ptr [esi + 0xc] ; p2.z
...
; Leitura da flag de superfície:
0x00487f0d: movzx   cx, byte ptr [esi - 8]  ; cx = byte de flag
0x00487f18: mov     ecx, eax                ; ponteiro "this"
0x00487f1a: call    0x485100                ; Construtor C++ do objeto EdgeSegment
```

### 4.2. A Matemática da Divisão por 28 (`0x1c`)

Usa o algoritmo de Granlund-Montgomery para divisão inteira otimizada:
$$\frac{2^{34}}{28} = \frac{17179869184}{28} \approx 0x24924925$$

O cálculo determina exatamente a fórmula:
$$\lfloor (N - 4) / 28 \rfloor$$

**Conclusão**: O arquivo possui um cabeçalho inicial de **4 bytes**, seguido por registros de **28 bytes cada**.

### 4.3. Estrutura do Registro `.edg` (28 bytes)
| Offset | Tamanho | Tipo | Nome | Descrição |
|---|---|---|---|---|
| `0x00` | 1 byte | `u8` | `flags` | Tipo de borda (`0x00` = asfalto, `0x10` = parede/guard rail, `0x20` = zebra/grama) |
| `0x01` | 3 bytes | `u8[3]` | `padding` | Padding de alinhamento em memória |
| `0x04` | 12 bytes | `f32[3]` | `p1` | Coordenada 3D do ponto inicial `[X, Y, Z]` (em metros) |
| `0x10` | 12 bytes | `f32[3]` | `p2` | Coordenada 3D do ponto final `[X, Y, Z]` (em metros) |

---

## 5. Construtor dos Segmentos de Pista (VA `0x00485100`)

No endereço `0x00485100`, o jogo instancia a classe C++ `EdgeSegment`:
- A tabela de métodos virtuais (`vtable`) da classe fica em **`0x005b484c`**.
- Para cada segmento de pista, o código calcula usando a FPU x87 uma caixa delimitadora alinhada aos eixos (**AABB — Axis-Aligned Bounding Box**), que o motor de física usa para testes rápidos de colisão e para reposicionar o carro na pista após uma batida.
