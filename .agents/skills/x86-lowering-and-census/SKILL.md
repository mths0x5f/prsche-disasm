---
name: x86-lowering-and-census
description: >-
  Use this skill to automatically lower/transpile x86-32 and x87-FPU machine code from
  Porsche.exe into deterministic C++ functions (using scripts/research/x86-cpp-backend-fpu.py),
  run frontier or global census evaluations, and compile/execute physical x86 CPU hardware fixtures.
---

# Skill: x86 Static Lowering, Census e Oráculos de CPU

Esta skill orienta o uso, extensão e validação do motor estático de descompilação de código de máquina x86 de 32 bits e x87 FPU do *Need for Speed: Porsche Unleashed* (`Porsche.exe`) para C++ determinístico com estado `Machine257`.

---

## 1. Arquitetura e Componentes

1. **Backend de Tradução Estática**:
   * Arquivo: `scripts/research/x86-cpp-backend-fpu.py`
   * Herança: herda de `x86-cpp-backend-277.py` via verificação estrita de hash `BASELINE_SHA`.
   * Cobertura: cobre 98,82% de todo o binário original (`5.627 / 5.694` funções).
   * Estado do modelo: `Machine257` com registradores `r[8]`, `flags` (EFLAGS), `pc`, pilha FPU em anel `st[8]`, `fpu_top`, `fpu_status` e `fpu_cw`.
2. **Censo do Frontier Oficial (Run 252)**:
   * Script: `scripts/research/census-v2-x86-fpu.py`
   * Avalia os 85 corpos de funções congelados do frontier.
   * Regra: **100% de sucesso obrigatório (85/85) e 0 regressões**.
3. **Censo Global do Binário Inteiro**:
   * Script: `scripts/research/census-v2-x86-global.py`
   * Avalia todas as 5.772 funções do catálogo `research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl`.
4. **Bancada de Testes de CPU Física (Hardware Oracles)**:
   * Script: `scripts/research/verify-v2-x86-fpu.py`
   * Compila via MSVC x86 (`cl.exe /O2`) um fixture nativo contendo naked-functions com assembly inline dos fragmentos sintéticos.
   * Executa **62.464 permutações de teste** comparando registradores, flags e memória com o silício real da CPU.

---

## 2. Procedimentos Operacionais

### 2.1 Traduzir uma Função Específica por VA
Para extrair os bytes de uma função do jogo e gerar seu código C++ equivalente:

```python
import importlib.util, json, struct
from pathlib import Path

# Carregar o tradutor
spec = importlib.util.spec_from_file_location('backend_fpu', 'scripts/research/x86-cpp-backend-fpu.py')
backend = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backend)

# Obter bytes da função do PE
catalog = {x['entry_va']: x for x in map(json.loads, open('research/v2/binaries/Porsche.exe-ddd748fdbe6d/functions.jsonl', encoding='utf-8-sig')) if x.strip()}
fn = catalog['004b68f0'] # Exemplo: VA desejado
start, end = (int(z, 16) for z in fn['ranges'][0])
# Obter bytes brutos com pe_map() e traduzir:
cpp_code, witness = backend.translate(raw_bytes, start)
print(cpp_code)
```

### 2.2 Executar o Censo do Frontier (85 corpos)
```powershell
python scripts/research/census-v2-x86-fpu.py
```
*Critério de aceitação*: Deve imprimir `85 / 85 (100.0%)` e `Regressions: 0`.

### 2.3 Executar o Censo Global (5.772 funções)
```powershell
python scripts/research/census-v2-x86-global.py
```
*Gera relatório em*: `local/experiments/v2-x86-global-census/summary.json`.

### 2.4 Executar o Oráculo de CPU Nativa
```powershell
python scripts/research/verify-v2-x86-fpu.py
```
*Critério de aceitação*: Deve testar 62.464 casos com **0 falhas** em menos de 1 segundo.

---

## 3. Diretrizes para Adicionar Novos Opcodes
Caso um novo opcode x86 seja necessário:
1. Adicione a função auxiliar ou assinatura em `HEADER` (usando tipos primitivos ou `extern "C"` sem headers pesados).
2. Adicione a decodificação do opcode em `PATCHES` dentro do bloco `elif m == '...'`.
3. Adicione o fragmento de teste sintético no array `FRAGMENTS` de `scripts/research/verify-v2-x86-fpu.py`.
4. Execute `verify-v2-x86-fpu.py` e `census-v2-x86-fpu.py` para garantir que o silício da CPU comprova o comportamento com zero regressões.
