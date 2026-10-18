# Resultado da Run 287

Concluído após aprovação do coordenador: um lote de duas TUs em `/MP6`, linkedição da fixture e
224 comparações nativas aprovadas (192 casos de printf e 32 casos de bridge somente com formato).
O objeto stdio antigo da 175 foi reutilizado sem alterações. Seus oito corpos originais não foram
recompilados e a suíte anterior de 4152 casos não foi repetida.

`summary.json` e `validation.json` fixam 83 entradas, 65 bytes exatos do oráculo original,
cinco relocações CALL e a relocação única DIR32 de stdout. O COFF real do bridge
define apenas `application_main_log` e importa o printf original canônico. A raiz re-hasheou
independentemente todas as 83 entradas antes da integração na Run 289.

O README permanece como a descrição pré-compilação com hash fixado. Não reexecute seus
comandos de produção concluídos sobre as tentativas salvas. Endpoints privados de fixture
estão excluídos do arquivo do jogo. O prefixo de lock 26->48 e o newline ausente
no chamador canônico permanecem como pendências separadas em aberto neste checkpoint.
