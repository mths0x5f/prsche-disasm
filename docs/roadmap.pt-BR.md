# Roteiro da Portabilidade Completa de Porsche Unleashed

Atualizado em 25/09/2026. Ativa **012-campaign-fidelity**; o último snapshot concluído é
011-factory-driver. Os snapshots 001–011 estão congelados. Seus READMEs e resultados de verificações são um
registro histórico do trabalho, e não uma prova de conformidade total de 1:1 com o original. O status atual e critérios
da 012 estão nos arquivos raiz [PLAN.pt-BR.md](../PLAN.pt-BR.md), [STATUS.pt-BR.md](../STATUS.pt-BR.md) e no
[plano da iteração](../iterations/012-campaign-fidelity/PLAN.md).

O objetivo é o jogo completo: Evolution e Factory Driver, os demais modos descobertos, regras de eventos,
economia, perfis/salvamentos, interface e som. Alvos suportados — Windows, Linux, macOS e web.
O visualizador e a máquina de arcade continuam sendo meios de pesquisa da portabilidade.

## Critério de Conclusão

O port deve ler os recursos originais e reproduzir regras, progressão, corridas, interfaces,
som e salvamento de estado. Ambas as carreiras devem ser percorridas desde um novo perfil até a conclusão,
com saída do jogo e continuação. O registro de modos deve abranger todos os modos da versão original;
um modo não investigado não pode ser considerado excluído do escopo.

A compatibilidade de comportamento é verificada através de cenários do original: entrada e condições iniciais → estado →
resultado. A correspondência byte a byte do EXE antigo não é exigida. As diferenças do port moderno são explicitamente
documentadas. As tolerâncias são determinadas antes da comparação, e não ajustadas após ela.

## Base Histórica: Snapshots 001–011

Os snapshots cobrem modelos e materiais de automóveis, geometria e ambiente das pistas, topologia,
visualizador, condução experimental, formatos de sistemas de jogo, simulação, corrida, shell,
Evolution e Factory Driver. Esses snapshots foram preservados sem alterações. Defeitos identificados
posteriormente e dúvidas sobre a precisão são tratados em novas iterações; a presença de uma implementação ou teste aprovado
por si só não comprova o comportamento do original.

## Agora: 012-campaign-fidelity

Eliminar divergências confirmadas das telas de campanhas, largada e roteiro de Factory Driver, contato
da suspensão e frenagem/marcha à ré. Verificar a separação de Evolution e Factory por recursos e
transições e, para missões — a vinculação ao SCN, regras de conclusão e largada/reset. Registrar separadamente
o que é conhecido a partir de recursos e código e o que permanece hipótese. Não encerrar a iteração por uma única
correção ou compilação bem-sucedida; são exigidas verificações de comportamento e conferência visual.

## Método para Todas as Etapas e Implementação Existente

Decisão do usuário de 04/10/2026: restaurar o comportamento original em vez de
selecionar algoritmos semelhantes. Dados de origem não comprovam o solver: são necessários
rastreamento de consumers e comparação de entradas/saídas. O código antigo é auditado da mesma forma;
partes não confirmadas não são consideradas restauradas.

## 013 (plano): Danos e Mercado de Automóveis Usados

Na 012, pesquisar a cadeia contato → reação → dano, para que a portabilidade da física
considere as dependências originais. Na 013, portar danos confirmados
e deformação, impacto no automóvel, condições de missões, salvamento e reparo.
Não considerar condition/custo de reparo atuais como física de danos.

A pedido do usuário, o mercado de usados entra nesta mesma iteração: seleção de modelos,
geração de estado inicial/danos, distribuições e chamadas de RNG,
precificação e atualização do sortimento. Danos comprados devem passar
pelo mesmo caminho através da física/perfil/reparo que os danos após uma corrida.
Valores e dependências devem ser restaurados a partir de consumers, não substituídos por um percentual
aleatório arbitrário de condition. Plano: [planned-damage-used-cars.pt-BR.md](planned-damage-used-cars.pt-BR.md).
A 013 ainda não foi criada, a 012 permanece aberta. Áudio/cockpit vêm após esta etapa.

## Depois Disso: Áudio e Cockpit

Após correções de conformidade das campanhas e do controle, restaurar sons ausentes e cockpit:
sons de motor, pneus e colisões, voz/música, instrumentos, câmeras e transições associadas. Conferir
cada função com os recursos e comportamento observável do original. Elementos já restaurados
são considerados comprovados apenas dentro dos limites da verificação correspondente.

## Trabalho Futuro: Demais Modos e Rede

Concluir o inventário dos modos do jogo original e implementar cada modo descoberto conforme suas
regras, dados, resultados e condições de salvamento. Não transferir automaticamente a mecânica
de uma corrida comum para desafios e regras adicionais.

Pesquisar o jogo em rede separadamente: modelo de sessão, regras, sincronização, conexão,
desconexão e reconexão. O jogo conjunto native↔web exige um transporte acessível
ao navegador; a compatibilidade com o protocolo antigo não é prometida sem verificação. A dependência de
serviços inacessíveis deve ser registrada e substituída por uma solução explicitamente definida. Não publicar servidores
no âmbito da implementação comum.

## Trabalho Futuro: Plataformas e Homologação Final

Verificar compilação, execução e conclusão nos ambientes disponíveis de Windows, Linux, macOS e web,
incluindo controles, redimensionamento, modo de tela cheia, pausa/foco, memória e carregamento no
navegador. O runtime nativo deve fornecer funções gerais de jogo sem dependência do
invólucro do navegador. Recursos do jogo são fornecidos pelo usuário; eles não são incluídos nos pacotes.

A homologação final inclui conclusões completas de Evolution e Factory Driver, cobertura dos demais
modos, migração de salvamentos, reprodução de cenários e verificações de gráficos/som nas
plataformas-alvo. A compilação em um único SO não comprova a execução nos demais.

## Regras Permanentes

- Cada nova iteração é conduzida como um snapshot separado com seus próprios PLAN, README e runs; snapshots
  concluídos não são editados, `local/game` permanece somente leitura.
- Testes de formato, corpus de dados, quadros de UI e compilação não substituem a verificação de comportamento. Para cada
  conclusão sobre engenharia reversa, preserve a fonte e o nível de confiança.
- O roteiro define as grandes direções, e o PLAN ativo — tarefas concretas e homologação. Direções
  futuras aqui propositalmente não são numeradas para não colidir com o número da iteração ativa.
