# Regras de Git, Branches de Feature e Isolamento de PRs

## 1. Origem e Isolamento de Branches de Feature
- **Base sempre no `upstream`**: Toda branch de feature/frente de trabalho (`feat/*`, `fix/*`, etc.) deve ser criada e baseada diretamente na branch correspondente do repositório `upstream` (ex.: `upstream/main`), NUNCA na branch `main` local caso ela contenha customizações do fork (como documentação traduzida `*.pt-BR.md`).
- **Escopo 100% isolado para PR**: Uma branch de feature destina-se exclusivamente a ser aberta como Pull Request para o `upstream`. Ela deve conter **apenas e unicamente** os arquivos técnicos modificados/criados daquela frente de ação específica.

## 2. Direção Estrita de Commits e Merges
- **Fluxo: Feature $\to$ Main (NUNCA Main $\to$ Feature)**:
  - O desenvolvimento e os commits de código são feitos **primeiro na branch de feature**.
  - **PROIBIDO fazer merge da `main` para dentro da branch de feature** (`git merge main` em branch de feature é estritamente proibido), pois isso polui a branch de PR com commits e arquivos locais (como traduções em português).
  - A branch `main` é que recebe os merges/fast-forwards da branch de feature quando concluída, NUNCA o contrário.

## 3. Proibição de Arquivos de Tradução (`*.pt-BR.md`) em Features
- Em nenhuma hipótese arquivos de documentação traduzidos em português (`*.pt-BR.md`) devem ser adicionados, commitados ou mergeados em branches de feature destinadas a PR no `upstream`.
- Antes de qualquer `push` para uma branch de feature, deve ser verificado com `git diff` / `git log` que zero arquivos `*.pt-BR.md` ou não relacionados àquela frente de ação estejam presentes.
