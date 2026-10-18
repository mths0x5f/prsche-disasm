# Run 401 — Despacho de Ciclos de Frame e Simulação (`00413ea0`)

Original `Porsche.exe` SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`: recuperada a função `00413ea0..00413fc7` (296 bytes de corpo PE), invocada diretamente do laço de quadros de `app_main_004b6a50` no endereço `004b6dbe` (`application_main_function_00413ea0`).

### Algoritmo e Comportamento
1. **Modos 0 e 1 (Reset da arena de frames):** limpa a arena `005ed848` (0x6400 DWORDs / 0x19000 bytes via `rep stosd`), zera o contador `005e99f8` e flag `005e99fc`, armazena o tick do sistema `0065741c` em `00606858`, e zera os acumuladores de passos fracionários `005e9a00..005e9a04`.
2. **Modo Negativo (`< 2` com sinal):** saída antecipada zerando `005e9a00..005e9a04`.
3. **Modo de Simulação Ativa (`>= 2`):**
   - Zera os flags de frame `005e99fc`, `00606860`, `00606868..00606870` e define o estado `00606864 = 2`.
   - Invoca o predicado `0046d960`. Se retornar 1:
     - No estado de sessão de corrida `006573e8 == 9`, ajusta o ritmo via `004659e0(0, 10)` e crava a taxa `00606850 = 20`.
     - Em outros estados de sessão, itera sobre o vetor de entidades `005e8c00` (tamanho `005e8bfc`), obtém a amostra do relógio `0046d890`, grava no deslocamento `entity+0x10e4`, despacha o passo via `00413960(clock_val)` e crava a taxa `00606850 = 20`.
   - Se o predicado `0046d960` retornar 0: define `00606850 = 10` e invoca `004659e0(0, 10)`.
   - Finaliza o passo gravando o tick do sistema `0065741c -> 00606858` e zerando `005e9a00`, `00606854`, `005e9a04`.

### Validação e Aceite
- O harness nativo x86 em `local/experiments/v2-frame-clock-401/frame_clock_fixture.cpp` executa os 296 bytes originais do PE em memória executável (com 31 relocações resolvidas) comparando contra o objeto C++ compilado `00413ea0.obj` em 7 cenários distintos (modos 0, 1, negativo, simulação normal com predicado 1, corrida com sessão 9, fallback com predicado 0, e contagem zero de entidades).
- Aprovadas 7/7 verificações diferenciais rigorosas de registradores (`EAX`, `ESP`, `EBP`, `EBX`, `ESI`, `EDI`, `DF`), integridade de memória da arena e trilha de chamadas externas.
