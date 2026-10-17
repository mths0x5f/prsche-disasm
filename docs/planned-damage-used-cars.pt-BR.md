# Plano 013: Danos Originais e Mercado de Usados

04/10/2026. Escopo acordado da futura iteração; o snapshot 013 ainda não foi criado.
A 012 está ativa. Nela inicia-se a engenharia reversa de contatos físicos e pontos de transmissão de dano (damage).

## Objetivo e Critérios de Conclusão

Restaurar a cadeia confirmada pelo original: impacto → estado do veículo →
alteração de comportamento/visual → resultado do evento → salvamento → reparo/venda.
O mercado de usados cria ofertas com danos iniciais conforme o algoritmo original,
e a compra preserva esses dados e suas consequências. A lista de componentes danificáveis,
o formato de deformação e os efeitos na condução são determinados pelo código, e não inventados.

## Tarefas

- Encontrar a estrutura de danos e os consumidores (consumers) de contato, mecânica, visual e missões.
- Restaurar a geração de usados: seleção de modelos/variantes, quantidade de ofertas,
  RNG/seed e distribuições de estado, restrições por progressão, frequência de atualização.
- Rastrear cálculo de preço, compra, estado da garagem, reparo e revenda.
- Conectar o runtime damage ao salvamento e regras de Factory/Evolution sem
  a constante atual 0.0 em evaluateFactoryResult.
- Verificar as implementações antigas de condition/wear/repair/catalog pela mesma fonte;
  portar cálculos confirmados, marcando explicitamente os demais como incompletos.

## Evidências e Verificações

Para cada função: module/SHA/VA, entradas/unidades, ramificações/cálculos, saídas,
funções chamadoras e chamadas. O índice é navegação, não especificação pronta.
Impactos de referência: veículos idênticos, velocidade, ângulo, superfície; comparação
de estados intermediários, dano final e visual com o original.
Para usados: sequência repetível de RNG sob controle disponível de seed,
ou estados iniciais salvos e rastreamentos de chamadas; verificação de preço/danos
antes e depois da compra, reinicialização do jogo, reparo e venda.
Testes próprios de perfil/gerador sem tal comparação não constituem homologação.

## Fronteira Atual Conhecida

Auditoria da 012: resolve_vehicle_contacts altera posição/velocidade, mas não o dano;
web/main.js::evaluateFactoryResult passa 0.0 para a avaliação da missão. apply_wear/
repair_cost existem separadamente e não comprovam a física dos danos originais.
Próximo passo da 013 após a 012: consumidores do estado original de danos e RNG
da loja; nenhuma geração de mercado "semelhante" antes de restaurar essas dependências.
