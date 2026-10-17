---
name: translate-to-russian
description: >-
  Use this skill whenever the user asks to document progress, create run reports,
  or translate documentation from Brazilian Portuguese (pt-BR) into Russian (ru-RU).
  Adheres strictly to the project's native Russian technical style, terminology, and conciseness.
---

# Skill: Documentação e Tradução Técnica (pt-BR -> Russo)

Esta skill orienta a tradução e redação de relatórios de progresso, planos de iteração, novos *Runs* e documentações do Português Brasileiro (`pt-BR`) para o Russo técnico (`ru-RU`), respeitando rigorosamente o estilo telegráfico, a precisão matemática e as convenções do autor original do projeto.

---

## 1. Regras de Estilo e Tom Técnico

1. **Estilo Conciso e Telegráfico (Regra de `AGENTS.md`)**:
   * O estilo do projeto é direto, sem introduções floreadas ou cortesias.
   * Estrutura clássica de relatório: **Resultado $\rightarrow$ Achado relevante $\rightarrow$ Bloqueio $\rightarrow$ Próximo passo**.
   * Exemplo: em vez de *"Nós conseguimos compilar com sucesso a função após fazer alguns testes"*, escreve-se *"00485100: 97 PE instructions и 1024 native bit cases PASS; тело COFF включено в union"*.
2. **Preservação de Dados e Sintaxe**:
   * Manter inalterados todos os identificadores em inglês/código: registradores (`EAX`, `ECX`, `ESP`), VAs (`0x00481080`), flags (`CF/ZF/SF/OF`), opcodes assembly, caminhos de arquivo e hashes SHA-256.
   * Manter termos como *HighIR*, *thiscall*, *cdecl*, *stdcall*, *COFF*, *probe*, *frontier*, *pins*.

---

## 2. Glossário Técnico Inverso (pt-BR $\rightarrow$ Russo)

| Termo em Português | Termo Canônico em Russo | Exemplo de Aplicação |
|---|---|---|
| **Restauração / Descompilação** | Восстановление | восстановление исходного кода |
| **Consumidores / Chamadores** | Consumers / потребители | по original consumers |
| **Linkedição / Ligação** | Линковка / связывание | диагностическая линковка, unresolved names |
| **Convenção de chamada** | Соглашение вызовов | восстанавливать соглашения вызовов |
| **Bancada de testes / Sonda** | Стенд / проба (probe) | files_probe.cpp, консольный стенд |
| **Snapshots / Iterações** | Снимки / итерации | снимки 001–011 заморожены |
| **Oráculos (gabarito)** | Оракулы (oracles) | x86 оракулы, сравнение с оригиналом |
| **Fila de pendências / Backlog** | Отложенные проверки / очередь | validation backlog, очередь зависимостей |
| **Homologação / Aceitação** | Приёмка | итоговая приёмка, семантическая приёмка |
| **Fronteira de símbolos** | Frontier / фронтир | linked frontier, frontier unresolved names |
| **Bifurcações de pista (.jnc)** | Развилки | число развилок, веса развилок |
| **Bordas / Limites de pista (.edg)**| Кромки полотна | кромки полотна дороги, EdgeSegment |
| **Passou nos testes** | PASS | 36 864 native comparisons PASS |

---

## 3. Estruturas Padrão de Documentação

### A. Adicionando um Novo Run (`runs/XXX-.../README.md`)
Seguir o padrão de resumo adotado nas runs 240–261:
```markdown
# RunXXX — [Nome conciso da etapa]

[Entradas utilizadas] formam **X candidate function VAs + Y support objects**:
Archive: X members, Y bytes. Archive SHA-256: `...`.

Actual diagnostic link leaves **N names / M diagnostics**.
Resolved: [nomes de funções fechadas].
Exposed / dependencies: [novas dependências identificadas].

[Quantidade] pins PASS before and after; [X] compiler commands, [Y] link passes.
Next step: [próximo passo imediato delimitado].
```

### B. Atualizando o `PLAN.md`
Sempre adicionar o novo checkpoint no topo com o carimbo de data:
```markdown
Checkpoint YYYY-MM-DD, RunXXX: **X candidate function VAs + Y support objects**,
...
```

---

## 4. Procedimento Operacional Passo a Passo

1. **Receber a instrução do usuário em português** (ex: *"documente que revertemos a função 0x00401000 e passamos nos testes"*).
2. **Formatar os dados brutos**: conferir o VA, bytes da função, quantidade de comparações e status do linker.
3. **Gerar o texto em russo técnico** seguindo o tom e os termos canônicos desta skill.
4. **Atualizar os arquivos oficiais** (`PLAN.md`, `runs/`, etc.) diretamente em russo, mantendo a integridade histórica do repositório.
