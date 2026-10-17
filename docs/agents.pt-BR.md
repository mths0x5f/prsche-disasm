# Modelos e Funções de Agentes

Regra do usuário de 19/09/2026: **quaisquer provedores e modelos são permitidos**,
incluindo locais. Nomes de modelos não são requisitos do projeto.
Um modelo forte disponível coordena, a implementação é delegada a executores
de complexidade suficiente. Isso substitui as antigas atribuições obrigatórias por marcas.

- planner: coordenador forte; arquitetura, engenharia reversa complexa, homologação.
- formats: executor médio; analisadores (parsers)/recursos, escalonamento de hipóteses complexas.
- renderer: executor especializado; native/WASM/GPU, nível conforme a tarefa.
- builds: executor leve; inventariação, scripts, CI, reprodutibilidade.

`agent-configs/*.toml` — exemplos substituíveis para um ambiente; veja
[explicação](../agent-configs/README.pt-BR.md). Eles não limitam a escolha do provedor.
O cliente ativo pode usar outro formato de perfis e método de delegação.
Mantenha as funções e regras, não exija compatibilidade com a API Codex/OpenAI.

## Atribuir por complexidade, e não pelo nome do arquivo

Preferências do projeto, não uma promessa de tarifas/disponibilidade de modelos:

- Rotina compreensível: modelo leve/rápido — inventário, relatório, script pequeno,
  documentação de resultado, testes sintéticos conforme especificação fornecida.
  A função builds é limitada a scripts/CI/docs; atribua testes de código a executores separados.
- Lógica e formatos delimitados: modelo médio para esquema conhecido; aumente
  o nível para offsets ambíguos, conexões e verificação de limites.
- wgpu/WASM/câmera e erros de GPU: perfil `renderer`; não envie uma edição simples de texto de UI
  para um perfil caro apenas porque o arquivo pertence ao visualizador (viewer).
- Arquitetura, hipóteses conflitantes de engenharia reversa, homologação final: coordenador forte.
  Não crie um segundo planner para o planejamento comum que ele já realiza.

Escolha o consumo mínimo esperado de recursos com qualidade suficiente, levando em consideração
custo, latência, contexto, ferramentas e resultados de verificações, e não a marca.
As palavras "leve/médio/forte" são relativas; modos de raciocínio/esforço (reasoning/effort) de diferentes
provedores não devem ser considerados diretamente comparáveis. Não invente tarifas e disponibilidade.
Utilize funções/modelos realmente disponíveis no ambiente atual. Um perfil pode
fixar um modelo: parâmetros de inicialização não garantem sobreposição.
Na ausência de um agente simples adequado ou do próprio mecanismo de delegação,
informe a limitação e execute um pequeno passo sequencialmente. Não simule
a inicialização de um agente e não afirme economia se ela não puder ser confirmada.
Configurações globais, cotas e permissões não devem ser alteradas para isso.

## Verificação do proprietário antes da restauração

Antes de codificar um pacote, compare todos os candidate VAs com
`iterations/v2/001-original-recovery/source/recovered/functions.json`.
Uma função já aceita mantém o proprietário canônico; conecte-a à nova
bancada de testes diretamente ou através de um alias tipado. Uma nova verificação é regressão, não uma nova
função restaurada. Verifique também entradas internas (interior entries) e intervalos de corpo completos.
O coordenador confirma a lista de novos endereços antes da execução; a auditoria SHA geral
e a compilação são combinadas por pacotes vinculados prontos.

## Ciclo econômico

1. Um resultado verificável por tarefa; geralmente 1 a 2 agentes simultaneamente.
   Em paralelo — apenas tarefas independentes com arquivos não sobrepostos.
2. Transmita caminhos, fatos confirmados, entrada/saída, verificações e condição de parada.
   Não transmita toda a conversa; não inclua fork do contexto completo sem necessidade.
3. O coordenador continua outro trabalho; não repete a pesquisa do executor
   e não o consulta em ciclos curtos. Compilações com alvo comum são executadas sequencialmente.
4. Aceite o diff, execute as verificações relacionadas à alteração. Execução de corpus/GPU
   completo — na fronteira da etapa, não após cada edição de documentação.
5. Duas verificações com falha em uma mesma hipótese: envie os fatos ao coordenador e aumente
   o nível da tarefa, se necessário. Em caso de limite de cota/uso, salve os artefatos,
   verifique o código deixado; não multiplique agentes com a mesma solicitação.
6. Encerre o executor após a homologação. O subagente não delega adiante e não comita
   sem ordem explícita do coordenador. Pequenas edições ou bloqueios urgentes
   o coordenador faz ele mesmo — iniciar um agente também consome tokens.

Cartão curto de atribuição:

```text
ID / resultado:
Função, provedor/modelo, modo de raciocínio (se disponível; reais):
Dependências e fatos confirmados:
Permitido alterar / apenas leitura:
Verificações e critério de aceitação:
Parar em: formato ambíguo, fora do escopo, duas tentativas sem sucesso.
Não é o único no repositório; preserve alterações de terceiros. local/game apenas leitura.
Resumo <=8 linhas: achado, arquivos/artefatos, verificações, restante.
```

A política acima é independente do cliente. Para os exemplos salvos do Codex, a mecânica
foi verificada em 19/09/2026 com [sua documentação](https://learn.chatgpt.com/docs/agent-configuration/subagents).
Para outro cliente, verifique seus recursos separadamente; a instalação/configuração
do provedor não faz parte da alteração destas regras.

Os antigos .cursor/agents/*.md foram salvos como descrições de papéis em outro formato.
