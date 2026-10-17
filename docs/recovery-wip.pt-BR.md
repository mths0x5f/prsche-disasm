# Trabalho em Andamento Salvo

17/10/2026: 278/280 não concluído salvo separadamente dos pacotes verificados.
- `scripts/research/audit-v2-native-union-280.py`, `native-replacements-280.py`,
  `native-platform-contract-280.py`: scaffold de substituições de chamadores fixadas por identidade
  e uma ponte cdecl SetLastError. Apenas verificação de sintaxe; não foram executados,
  recibos de substituição/nativos ausentes, jogo/arquivo inalterados.
- Quatro chamadores brutos 568ae0/b10/b50/b90 ainda possuem a declaração de
  char handle_device 595d0. A correção, a fixture 282 e a lacuna física 281 não foram iniciadas.
- Antes de utilizar o 280, são necessárias proteções negativas delimitadas,
  metadados/COFF reais de substituição e comparação nativa de ABI. O coletor ativo é o 268.
- A prioridade mudou para normal-entry 285; este protótipo não fecha a retenção de 595d0.


15/10/2026: fontes não rastreadas, probes, verificadores e relatórios foram salvos a pedido
do usuário. Esta é uma preservação de trabalho, não uma integração de produção.

- 111: relatórios históricos; dependências comuns foram parcialmente atualizadas posteriormente.
- 131: pacote de áudio-init isolado, integração ainda em aberto.
- 172/174/175: pesquisa de formatador, RTTI de rede e stdio; a fila de integração 176 permanece.
- 200: sete visões externas de float4; COFF 00485100 inseguro com lacunas de conversão FP/raw32
  foi excluído da união. Candidato corrigido obtido na 202 e incluído na 206.
- 201: triagem histórica somente leitura de 109 corpos ausentes. O piloto de declaração 203 forneceu
  21/25 COFFs reais; 4 falhas de chamada por ponteiro permanecem. A fronteira 206 agora possui 97 corpos ausentes.
- 202: concluídas 9 gravações raw32 / 8 visões de bits, 97 instruções originais e 1024 casos de bits nativos PASS.
  Captura: local/experiments/v2-float-bits-202/export; projeto original do Ghidra inalterado.
  Corpo completo/x87/equivalência de registrador do chamador adiados para o backlog de validação.
- 203–206: checkpoint completo de candidatos de compilação, 1094 objetos nativos; integração
  de produção e execução do jogo não foram realizadas. Não confundir com trabalhos em andamento (WIP) históricos salvos.

Próximo passo: consumidores originais de chamadas por ponteiro das quatro falhas da 203 e dependências da 206;
relatórios antigos 111/131/172/174/175 não são considerados verificações recentes.

Checkpoint 216 em 15/10/2026: pacotes de candidatos 207–214 e arquivos 215/216 concluídos,
1108 VAs de função distintas. Valor de saída de som 214 corrigido/verificado em fixture; provedor completo e
vínculo de armazenamento/ABI nativo permanecem no backlog. Produção original 173 permanece inalterada.
