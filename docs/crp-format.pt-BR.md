# Formatos CRP, FSH e TPG

Esta nota descreve apenas o que é utilizado pelo visualizador (viewer) da primeira iteração.
Fonte dos fatos: verificação local `local/research/inspect_crp.py`, `356a`/`356b` decodificados
e o referencial `local/references/LibOpenNFS/lib/CrpLib`. Os arquivos originais do jogo
permanecem em `local/game` e não são adicionados ao Git.

## CRP

`*.crp` começa com RefPack (`10 FB`) ou já contém dados descompactados.
No RefPack, após a assinatura, localiza-se o tamanho do resultado em três bytes big-endian. Para
a cópia verificada do jogo: `356a` descompacta de 1 640 460 para 3 764 224 bytes (181
artigos, 87 registros misc), `356b` — de 1 577 631 para 3 346 432 bytes (152, 72).

O CRP descompactado começa com `Car ` em little-endian (em bytes `20 72 61 43`). O campo
no offset `0x04` contém o número de artigos nos 27 bits superiores, `0x08` — o número de registros
misc, `0x0c * 16` — o início da tabela. Uma entrada da tabela ocupa 16 bytes:

- ID; para IDs de duas letras, os 16 bits inferiores são o índice e a flag `1` está definida;
- comprimento nos 24 bits superiores da palavra seguinte;
- count;
- offset relativo. Para um contêiner de comprimento zero, ele é medido em blocos de
  16 bytes; para dados — em bytes.

O artigo `Arti` contém `Base`, `Name`, `vt`, `nm`, `uv`, `tr` e `pr`. Para
`vt`/`nm`/`uv`, o índice possui o level no nibble inferior, o número da animação acima dele e a flag
de dano no bit 15. `pr` usa outro índice: level nos quatro bits superiores,
número da peça — nos 12 inferiores.

Para a cena de carro estacionado (parked-car), primeiro seleciona-se o TPG `[style1]` (se ausente — type0).
Os pares geometryN/typeN definem `Base.GeomIndex/TypeIndex`, textureN/typeN definem
um conjunto independente de variantes de textura. Grupos não especificados possuem type0. Em seguida,
para toda a cena, obtém-se o Level mínimo diferente de zero entre os artigos selecionados.
O artigo deve ter este Level ou o level0 comum; `vt`/`nm`/`uv` são selecionados por
este index, `pr` — por `pr.index >> 12`. O Driver é excluído pelo bit `0x80`
em BaseInfo.LevelIndex. Os nomes In/Out não participam da seleção.
O material `mt` armazena o número da página TPG como
um `u32` little-endian no offset `0x28`; este é o índice zero da página, e não o número de `sf`.
A matriz `tr` contém 16 `f32` em ordem column-major e descreve o posicionamento
da peça. No carregador atual, os vértices são redimensionados a partir de unidades CRP `/5`, e de
`tr` usa-se apenas a translação `mat[3]` (também `/5`); em seguida, tanto o vértice quanto a translação
juntos são refletidos uma única vez em Z na transição para a Scene. A parte rotacional da matriz não
é reaplicada a cada vértice ou normal. Isso corresponde
à implementação estabelecida da LibOpenNFS e preserva o posicionamento relativo das peças.

Fonte: `local/references/LibOpenNFS/lib/CrpLib/Common.h` (`tLevelMask`,
`LEVELINDEX_*`) e `Entry.cpp` (`GetPartEntry`, `GetDataEntry`),
`local/references/LibOpenNFS/NFS5/NFS5Loader.cpp` (loop `GetLevel(v)`). Dados:
`local/research/356a.json`, `356b.json`; neles, `TreadFront`/`TreadRear` possuem
o primeiro `tLevelMask.Level == 4`. A regra antiga "primeira mask de cada artigo"
misturava incorretamente o Tread4 de corrida com o frontend1. Isso foi corrigido no run008.
A alternância exata em tempo de execução de portas/capô permanece não verificada.

`pr` contém a tabela de canais e linhas de índices. Os canais `0`, `1`, `2` significam
vértices, normais e UVs. Os índices nos dados são em bytes; o campo Offset do canal define o índice
base no array correspondente (Offset/16 para vt/nm, Offset/8 para uv).
`IndexRowRef` seleciona a linha `tPartIndex`; o valor `0xffff` indica
um canal sequencial (índice i+base), e não uma referência corrompida. Tais canais
existem em 928/930/eas5/gt1; peças completamente não indexadas nd=0 também são permitidas.
Os testes cobrem canais mistos indexados/sequenciais e Offsets diferentes de zero.
A geometria já contém ambos os lados do carro, portanto
o carregador não cria uma cópia espelhada.

Ao refletir CRP→Scene em Z, o carregador reflete posições e normais, mas não altera a ordem
dos índices. Dados de `examples/audit_scene.rs` para 356b antes dessa correção resultaram em
`aligned=107`, `opposed=2984`, `degenerate=0`: o enrolamento (winding) original do CRP é predominantemente CW
em relação à normal fornecida, e o espelhamento sem swap o torna consistente. Este é um fato
de auditoria local; a regra exige nova verificação no corpus e não é uma conclusão
sobre o culling em tempo de execução do jogo original.

`Material.alpha_mode` é determinado sem o número da página: os métodos de renderização `CarExt`,
`CarExtEnv` usam Mask para alpha0 e valores intermediários opacos
(marcação de pintura), `CarInt` por enquanto é Opaque;
para os demais, o carregador usa o `bpp` da `[tpageN.details]` alvo e o alpha do atlas
selecionado. `1555` com alpha 0 — Mask/cutoff 0, `4444` — Blend, caso contrário o alpha binário resulta em
Mask, fracionário — Blend. A flag `mt +0x0c` está documentada na CrpLib apenas como cull (`0x20`)
e não participa da classificação de alpha. Fato EAS1: `WheelShadow*` usa
`CarWheel` com `shadow.fsh` (4444, alpha 0..199), enquanto wheel tiles possuem 1555/0..255.
No run008, retângulos de shadow/cutout de rodas do tráfego foram eliminados. O run009 verifica
Mask exterior e pintura de teste: alpha255 preserva faróis/cromados, alpha
intermediário é colorido. O CLR completo e o significado em tempo de execução dos níveis de alpha ainda não foram restaurados.

Filtros de tile FSH fileN.tile são selecionados por geometryK ou textureK e typeK do mesmo
style1; pares alternativos são combinados com OR, dicionários de geometry/texture não se misturam.
Exemplo: 928/944 file3.whf1 requer texture13/type1; um type0 rígido deixava as rodas vazias.

## Superfícies coincidentes e deslocamento de profundidade (depth bias)

Run010: no 356b, Body e Light1 interceptam o raio de controle com o mesmo
`t=0.919246852`. `mt4` e `mt12` possuem o mesmo método de renderização, TPG e cull;
diferenças de dados: signed `mt+0x114` = 0/-3, `mt+0x134` = 0/2.
`pr.TransInfo` = 0/0x200. `tPartInfo.Level` em ambos é igual a 1, RMOffs coincidem,
portanto a divergência de canais não explica o desaparecimento dos faróis.

O visualizador passa o signed `mt+0x114` para o constant depth bias do pipeline de GPU.
Em 1578 materiais da carroceria, os valores são: 0 (987), 1 (65), 3 (73), -10 (75),
-3 (288), 5 (28), -2 (34), -1 (28). A geometria não é deslocada, os nomes das peças
não são verificados. O teste sintético `coplanar_material_bias_gpu` comprova a independência
da visibilidade de detalhes coplanares em relação à ordem das peças. A ordenação por ID de material ajudou
como experimento de controle, mas não é uma correção operacional definitiva.

Esta é uma interpretação do campo, confirmada por dados e experimento em GPU, não uma prova
das unidades/algoritmo exatos de deslocamento de profundidade do renderizador original.
Comando de auditoria numérica (da raiz, após tool-env):

```powershell
cargo run --manifest-path iterations/001-car-viewer/Cargo.toml --target-dir local/builds/001-car-viewer/.cargo-target -p nfs-assets --example audit_scene -- local/game/GameData/CarModel 356b --ray-light1
```

## FSH e TPG

FSH possui `SHPI`, comprimento do arquivo e catálogo de entradas de oito bytes. Os FSHs integrados
e compartilhados necessários usam o formato `0x7d`: BGRA32, que é convertido para RGBA. Para
compatibilidade, também são lidos BGR24 `0x7f` e indexado `0x7b` com paletas.
Os limites são lidos pelo comprimento do próprio FSH, e não pelo buffer do CRP envolvente.

TPG é formato INI. As páginas `[tpageN.details]` são numeradas a partir de 1, enquanto `mt.tpg` a partir de 0.
`[fileN.details].tpage` define a página de destino do atlas. A posição do tile está
no cabeçalho do FSH: x/y nos offsets `+0x0c/+0x0e`; o TPG adiciona `offsetx/offsety`.
`sf` no CRP mapeia-se para `fileN` como `sf.index == N - 1`. No `356a` e `356b`, isso
cobre file 1–4 e 8; os pacotes necessários restantes são obtidos do catálogo compartilhado.

O posicionamento é uma operação raster com corte (clipping) nas bordas da página TPG, e não
uma exigência de enquadramento completo do retângulo. Isso é confirmado por dados locais:
`944`/`file2.full` possui `x=209`, largura 48 e página com largura 256, ou seja, um
pixel sai pela direita. `eas2`/`file1.top` grava a coordenada esquerda como
`0x0fff`, e `eas3`/`file1.fro` a superior como `0xffff`; ambos representam a origem `-1`
e preservam a interseção com o atlas. O carregador aceita essas duas variantes do NFS5
de codificação de `-1`, aplica o deslocamento TPG, rotação e, em seguida, copia apenas os pixels dentro
dos limites da página. Um tile sem uma única interseção ou com tamanho inconsistente
do buffer de pixels continua gerando erro.

Fonte do campo x/y: `local/references/LibOpenNFS/Shared/FSH/FshTypes.h` (`FshEntryHeader` de 16 bytes,
quatro `misc` u16) e a descrição da estrutura geral do FSH:
<https://modthesims.info/wiki.php?title=FSH>. Os valores de `944`/`eas2`/`eas3` foram obtidos
por `local/research/inspect_crp.py` a partir de `local/game/GameData/CarModel`. Hipótese:
`0x0fff` é uma representação de 12 bits e `0xffff` de 16 bits da mesma origem de borda
`-1`; isso é consistente com a interseção não vazia e a compactação densa de tiles, mas ainda não
foi verificado contra o código de máquina do original.

Para o carro estacionado, são obrigatórios os seguintes arquivos compartilhados, caso não estejam embutidos:
`INTGLASS.FSH`, `Shadow.fsh`, `Cabrio.fsh`. Traje e cabeça (`global=3/4`) propositalmente não
são solicitados: o motorista não faz parte desta cena. O erro do carregador lista todos os
FSHs compartilhados ausentes em uma única mensagem, para que as interfaces nativa e WASM possam solicitá-los
em uma única seleção de arquivos.

## Não confirmado

A máscara CLR de repintura da carroceria e a regra exata de espelhamento da página TPG ainda não foram confirmadas
pelo código original. O canal alpha da carroceria com valores 77/204 por enquanto não altera a escolha do material;
o renderizador a mantém como opaca até investigação separada.
