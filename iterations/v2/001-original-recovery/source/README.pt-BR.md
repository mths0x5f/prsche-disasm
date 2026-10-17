# Códigos-Fonte Compiláveis Recuperados

Decisão do usuário: diretamente C/C++, a execução do jogo é permitida mais tarde. Aqui
estão os códigos-fonte regulares com ABIs/algoritmos originais e vinculação a módulo/SHA/VA.

- `include/porsche`: declarações e ABIs verificados.
- `recovered/Porsche.exe/startup.cpp`: primeiro salto recuperado
  `0x4b6710`, quatro argumentos stdcall; 175 comparações native/x86.
- `recovered/Porsche.exe/fe_stream.cpp`: nove funções cdecl de leitura de configuração,
  formação e aplicação de registros FE; 236 comparações native/x86.
- `recovered/Porsche.exe/fe_tables.inc`: dados tipados a partir do PE original,
  exportação repetível `scripts/research/export-v2-fe-tables.py`.
- `recovered/Porsche.exe/heap.cpp`: 11 funções da heap proprietária e auxiliares;
  551 comparações de estado da arena após cada operação. `include/porsche/heap.hpp`
  preserva o cabeçalho original de 16 bytes e o bloco de controle de 64 bytes.
- `recovered/functions.json`: registro de funções manuais, dependências e evidências.
- `recovered/sources.cmake`: lista explícita de fontes da biblioteca `porsche_original`.
- `recovered/recovery_probe.cpp`: bancada de teste isolada em console; substituição
  de gravação do ainda não recuperado `0x4b6a50` existe apenas aqui.
- `recovered/fe_stream_probe.cpp`: bancada FE isolada; gravações de
  arquivo/heap/callback e comparação de strings não são adicionadas à biblioteca do original.
- `recovered/heap_probe.cpp`: comparação completa da heap; VA fixo da arena
  é aplicado apenas na bancada de teste, chamadas externas de SO/CRT/SIMD são registradas.
- `recovered/Porsche.exe/files.cpp`, `io_lists.cpp`: 29 funções de requisições,
  filas, conclusão e leitura em blocos; layout em `include/porsche/files.hpp`.
- `recovered/files_probe.cpp`: 89 comparações conjuntas FE/heap/IO com x86;
  worker imediato, endpoints de disco/VirtualAlloc/SO encontram-se apenas na bancada.
- `recovered/Porsche.exe/file_pages.cpp`, `file_device.cpp`: mais 6 funções
  de invólucros de página (page wrappers), construtores de listas / chave padrão e inicialização de dispositivo (startdevice).
- `recovered/device_probe.cpp`: 474 comparações com x86; endpoints de SO/thread/eventos
  são registrados, loop do worker ainda não executado. Page wrappers reais conectados
  ao files_probe; fronteiras externas de alocação agora em importações Win32.
- `catalog`: catálogo de endereços de todos os módulos e funções, intervalos de bytes
  de pseudo-C, caminhos de dados/listagens/chamadas/importações e status de recuperação.

O pseudo-C automático do Ghidra permanece em `research/v2/binaries`; o catálogo
não o adiciona à compilação. Tipos/assinaturas do Ghidra — material para verificação.
Para extrair uma única função para a próxima migração:

```powershell
py -3 scripts/research/structure-v2.py
py -3 scripts/research/structure-v2.py --extract Porsche.exe --address 0x59e040 --output local/experiments/v2-files/0059e040.c
```

`porsche_original.lib` contém objetos recuperados e ainda possui
dependências não resolvidas; não é um jogo pronto. 56 funções verificadas nas
fronteiras fixadas das bancadas de teste. Isso não confirma UI, física, loop principal,
chamadas (callees) externas de SO/CRT/SIMD/disco/threads ou correspondência de bytes do EXE. Evidências
conjuntas atuais — runs/006-file-device; regressões isoladas de FE/heap
permanecem no Run005. Run001–005 preservam o estado de seus pontos de controle (checkpoints).
Cinco funções suplementares sem pseudo-C estão acessíveis via índice manual
verificável por SHA; o catálogo contém 36 592 registros. O worker nele permanece ainda não recuperado (unrecovered).
