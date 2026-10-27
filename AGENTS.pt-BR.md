# Trabalho no Projeto

## Reconstrução verbatim (decisão do usuário, 2026-10-26)

- O código recuperado é reconstrução da história, não só um programa que roda. Deve ser o mais
  próximo possível do fonte verbatim que gerou o binário: não inventar absolutamente nada.
- Linguagem e compilador do original (pelo cabeçalho Rich e pelo CRT): C continua C89 para o
  compilador C do VC6, C++ continua C++. Nunca passar C para C++ por conveniência.
- Estrutura do original: não criar funções auxiliares, não fatorar laços repetidos, não juntar nem
  dividir funções, não criar abstrações, macros ou tabelas que o binário não mostra.
- Nada que não seja original dentro da árvore do original (stubs, fronteiras, camadas de
  plataforma): isso fica numa pasta separada e marcada. Nomes da EA têm prioridade; os demais
  nomes, nomes de arquivos e de pastas são marcados como não atestados.
- Esta regra vai em toda instrução a executores e é conferida antes da aceitação.

## Restauração do original — método principal

- A decisão do usuário de 04/10/2026 é válida para todo o projeto e código antigo:
  física, danos, IA, scripts, progressão, formatos, UI e som.
  Restaure os algoritmos e o comportamento originais, e não crie uma implementação semelhante
  do zero nem ajuste coeficientes por sensação subjetiva.
- Antes da portabilidade, registre a fonte: módulo/SHA/endereços e cálculos para o algoritmo,
  campos do recurso original para os dados, quadros/transições de referência para a interface.
  A presença de uma string, carregador ou tabela SIM não comprova o algoritmo de aplicação.
- Compare entradas → estado intermediário → saídas com o original. Testes próprios
  e uma condução estável não substituem essa verificação.
- Deixe o comportamento não investigado explicitamente incompleto. Teste hipóteses separadamente
  em local/experiments; não conecte uma aproximação à compilação do jogo sem a aprovação
  explícita do usuário. A infraestrutura de plataforma moderna é permitida,
  mas não deve alterar silenciosamente a semântica original do jogo.
- Verifique a implementação existente pelos mesmos critérios: mantenha o que for confirmado,
  substitua o restante de acordo com os consumidores (consumers) originais específicos. Não edite os snapshots 001–011.
  Não faça uma reescrita completa sem rastreamento.

## Primeiro o índice do original

- Antes de implementar ou alterar o comportamento do jogo, física, scripts,
  formatos e interface, procure primeiro o original no índice de binários.
  Ponto de entrada: `research/binary-index/README.md`; os índices são versionados no repositório.
- Procure strings/recursos/importações, em seguida, verifique as funções, as funções que as chamam
  e as funções chamadas por elas. O índice é para navegação, não como prova de semântica.
- No plano ou relatório de alteração, indique a consulta, o módulo/endereços, as evidências encontradas
  e a conexão com a implementação. Separe o comportamento confirmado das hipóteses.
- Se o código necessário não estiver no índice, verifique a cobertura e os erros de análise, em seguida,
  complemente o índice. Não substitua a ausência de evidências por uma suposição sobre o original.
- A pesquisa no índice não autoriza a implementação por suposição. Se a semântica não for comprovada,
  mantenha o próximo passo concreto de rastreamento. A regra se aplica a todos os executores.

## Economia de tokens — para o coordenador e todos os subagentes

- Escreva de forma concisa: resultado, achado relevante, bloqueador ou próximo passo.
- Não repita a solicitação, o plano, fatos já conhecidos e registros completos de comandos.
- Leia os trechos necessários via `rg` e limite a saída; salve o log completo
  em um artefato local, imprima erros e o resultado no contexto.
- Delegue tarefas independentes e delimitadas, com arquivos de escopo e resultado esperado.
  Transmita um contexto compacto, não duplique a pesquisa dos agentes.
- Use as funções de `docs/agents.md`. Resultado do agente: achado, arquivos modificados,
  verificações, restante. A brevidade das mensagens não significa parada do trabalho.

## Atribuição de executores

Regras para escolha do executor — `docs/agents.md`; agente simples por padrão para
implementação delimitada, complexo — apenas com necessidade comprovada.

- Quaisquer provedores e modelos são permitidos; marcas específicas não são um requisito.
- Modelo forte — coordenador: decisões, engenharia reversa complexa, integração e homologação.
- Executores leves — inventários, scripts, documentação, testes simples;
  médios — analisadores (parsers) e implementação comum; especializados/fortes — formatos complexos
  e GPU. Escolha um modelo suficiente com o consumo mínimo esperado de recursos.
- Normalmente, 1 a 2 executores são suficientes. Não crie um agente para uma pequena alteração
  ou para uma etapa imediatamente bloqueadora se for mais fácil executá-la você mesmo.
- Verifique modelo/esforço na atribuição; não considere o perfil fixo de papel
  como um parâmetro de inicialização (spawn) substituído. Sem um modelo leve disponível, informe isso.
- Após duas tentativas frustradas em uma mesma hipótese — envie fatos concisos ao coordenador,
  e não reinicializações infinitas. Após o limite, verifique alterações incompletas.

## Plano e transferência de trabalho

- Antes do trabalho, leia `PLAN.md`, `STATUS.md`,
  `iterations/<iteração-ativa>/PLAN.md` e os últimos `runs/*/README.md`.
  Se a próxima iteração ainda não foi criada, o plano dela é `docs/next-iteration.md`;
  não considere o PLAN de um snapshot finalizado como tarefa ativa.
- Mantenha o `PLAN.md` geral e o `PLAN.md` separado da iteração ativa.
  Atualize após um achado substancial, mudança de direção, conclusão
  de subtarefa/verificação e antes de encerrar a sessão; não deixe o plano desatualizado
  durante uma tarefa longa.
- No plano da iteração, mantenha a meta e critérios de conclusão, o que foi executado,
  fatos confirmados e hipóteses separadamente, tarefas atuais/responsáveis,
  comandos exatos de verificação e o próximo passo concreto mais próximo.
- Ao transferir o trabalho, remova atribuições desatualizadas, indique arquivos e artefatos,
  defeitos conhecidos e bloqueadores. Outro agente deve continuar sem precisar reler
  toda a conversa. Verifique `STATUS.md` com os resultados reais.
- Uma compilação/análise bem-sucedida não substitui a verificação visual. Não declare
  uma iteração como encerrada se os critérios não forem atendidos.

Os recursos do jogo `local/game` são apenas para leitura. Salve o histórico de `runs` dentro do seu snapshot;
pastas com snapshots de `runs` não são transferidas ao criar uma nova iteração (cada iteração mantém
seus próprios runs, começando em `001`).
