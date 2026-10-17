---
name: translate-docs
description: >-
  Use this skill whenever the user asks to translate, re-translate, or update
  documentation files (*.md) from Russian into Brazilian Portuguese (*.pt-BR.md).
  Enforces 100% faithful, exhaustive, line-by-line translation without summarizing.
---

# Skill: Tradução Fiel de Documentação Técnica (Russo -> pt-BR)

Esta skill orienta a tradução e sincronização contínua de qualquer documentação Markdown (`.md`) deste projeto para o Português Brasileiro (`.pt-BR.md`), garantindo fidelidade técnica absoluta de 100%, sem resumos, omissões ou simplificações.

---

## 1. Regras Fundamentais de Tradução

1. **Fidelidade Integral (Zero Resumo)**:
   - Toda e qualquer seção, parágrafo, observação histórica, notas de checkpoint e listas devem ser traduzidas na íntegra.
   - NUNCA resuma, corte ou adapte o texto como resumo executivo. A tradução deve refletir o documento original parágrafo por parágrafo.
2. **Preservação Estrutural e de Dados**:
   - Manter todos os blocos de código (`x86asm`, `powershell`, `c`, `rust`, etc.) exatamente como no original.
   - Preservar sem alteração: hashes SHA-256, endereços de memória (VAs como `0x00481080`), offsets (`+0x33c`), nomes de funções (`FUN_...`), nomes de arquivos, tabelas e links markdown.
3. **Formato dos Arquivos de Saída**:
   - O arquivo traduzido deve SEMPRE ficar lado a lado com o original, adicionando o sufixo `.pt-BR.md`.
   - Exemplo: `docs/roadmap.md` $\rightarrow$ `docs/roadmap.pt-BR.md`.
   - Certifique-se de que `*.pt-BR.md` esteja no `.gitignore` para não sujar o histórico Git.

---

## 2. Glossário Técnico Padronizado (Russo $\rightarrow$ pt-BR)

| Termo em Russo | Tradução Padrão | Contexto / Nota |
|---|---|---|
| **Восстановление** | Restauração / Descompilação | Reconstrução do código original a partir dos binários |
| **Потребители (consumers)** | Consumidores (*consumers*) | Funções ou módulos que chamam/consomem um dado ou função |
| **Линковка** | Linkedição / Ligação | Processo do linker (MSVC link.exe) |
| **Соглашение вызовов** | Convenção de chamada (*calling convention*) | `__cdecl`, `__stdcall`, `__thiscall` |
| **Снимки / итерации** | Snapshots / Iterações | Versões isoladas em `iterations/` |
| **Приёмка** | Homologação / Aceitação formal | Aprovação de conformidade com o original |
| **Оракулы** | Oráculos (*oracles*) | O executável original da EA usado como gabarito de teste |
| **Развилки (.jnc)** | Junções / Bifurcações de pista | Pontos de decisão de caminho para a IA |
| **Кромки полотна (.edg)** | Bordas / Limites de pista | Segmentos de colisão das laterais da pista |
| **Отложенные проверки** | Validações pendentes (*backlog*) | Fila de testes formais em aberto |
| **Стенд / проба (probe)** | Bancada de teste / Sonda (*probe*) | Programa isolado de teste comparativo de registradores |
| **Откаты / регрессии** | Regressões | Perda de comportamento previamente verificado |

---

## 3. Procedimento Operacional Passo a Passo

### Passo 1: Verificar o Status das Traduções
Execute o script de cobertura de tradução para saber quais arquivos estão sem tradução ou desatualizados:
```bash
python3 .agents/skills/translate-docs/scripts/coverage.py
```

### Passo 2: Executar a Tradução Integral
Para o arquivo solicitado:
1. Leia o arquivo `.md` original na íntegra.
2. Traduza cada parágrafo com fidelidade técnica estrita usando o glossário.
3. Salve o resultado no arquivo correspondente `<caminho>/<nome>.pt-BR.md`.

### Passo 3: Verificação de Integridade
Compare o arquivo traduzido contra o original:
* A quantidade de blocos de código e tabelas deve ser **exatamente idêntica**.
* Links relativos continuam apontando para seus respectivos alvos.
