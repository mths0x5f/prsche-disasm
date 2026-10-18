# Run 289: conectar logging e iteração de frames à entrada do jogo

Uma linkedição real de normal-entry reutiliza as cinco bibliotecas de jogo em cache e adiciona um
novo arquivo estático contendo exatamente quatro objetos de jogo: o bridge de logging da Run 287,
o objeto stdio inalterado da 175 (oito corpos originais mais suas células de buffer),
e os dois novos objetos de serviço de frame da Run 290. Nenhum provedor de fixture, implementação
adivinhada, símbolo não resolvido forçado ou código executável original é linkado.

Comparado com a Run 285, duas arestas reais de `app_main` agora estão implementadas:
`application_main_log` e `application_main_function_00471b60`. Esta última
alcança a `00487e20` original, expondo quatro contratos de chamados (callees) e um contrato
de armazenamento global. Dessa forma, a fronteira observada muda de **267 -> 270 nomes** e
**303 -> 306 referências**; os serviços diretos não resolvidos de `app_main` diminuem de 20 -> 18.
Não há outros erros de linker. **Nenhum EXE de jogo foi produzido ou executado.**
Isto é recuperação de código-fonte conectado, não uma estimativa percentual do jogo.

[A linkedição](logging-frame-001.json) e o [manifesto de integração](logging-frame-001-integration.json)
fixam o arquivo estático real, identidades de objetos, comandos, logs e comprovantes. A
auditoria independente passa 22 pins de entrada mesclados, verifica 12 definições únicas de símbolos
públicos ao longo dos quatro objetos, exclui provedores de fixture/globais, verifica
os diagnósticos reais de 270/306 e registra os dois nomes removidos / cinco nomes expostos.
A biblioteca adicionada é pesquisada normalmente; WHOLEARCHIVE, NOENTRY, ENTRY customizado e
FORCE estão ausentes. Esta etapa não compila nada: somente um arquivo estático mais uma linkedição.

A Run 287 passou em 224 casos nativos. A Run 290 passou em seis casos originais/nativos e 98
bytes PE originais. Essas fixtures delimitadas não comprovam os quatro chamados reais de frame,
o global 00628960 ou a composição completa de saída/execução. Em seu oráculo original,
`004898f0` executa seu corpo PE real; os outros três chamados de frame são pontos de corte
controlados. Seu retorno de ponteiro é o próximo pacote conectado 291. O requisito de prefixo
de lock 48 e o newline original de logging permanecem em aberto no backlog de validação.
Construtores de inicialização, recursos, renderização, entrada e jogabilidade real ainda
necessitam de comparação com o original.

A entrada CMake independente compila os fontes revisados e em seguida o alvo de jogo existente
da Run 102. A configuração foi bem-sucedida como MSVC Win32 em
`local/builds/v2/game-startup-link-289`; uma compilação CMake completa a partir do zero não foi
executada neste checkpoint. A linkedição em cache é explicitamente separada dessa compilação.

```powershell
py -3 scripts/research/audit-v2-game-entry-289.py
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe -S iterations/v2/001-original-recovery/runs/289-game-startup-link -B local/builds/v2/game-startup-link-289 -A Win32
& local/tools/cmake-4.4.3-windows-x86_64/bin/cmake.exe --build local/builds/v2/game-startup-link-289 --config Release --target porsche_original_game_link --parallel 4
```

Não reexecute um nome de tentativa de integração já concluído. As entradas exatas de objetos para a
tentativa capturada sem compilação estão em seu comprovante de arquivamento. Novos objetos revisados
exigem uma nova tentativa e pacotes de comprovação fixados. O arquivo completo de candidatos da Run 274
não é dependência desta linkedição de jogo; em particular, o getter com retorno void da antiga 187
não deve competir silenciosamente com sua substituição tipada corretamente da 291.
