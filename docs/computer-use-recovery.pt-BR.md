# Computer Use: Transferência Após Reinicialização, 25/09/2026

Nova verificação em 26/09/2026: `@oai/sky` foi importado no `node_repl` disponível,
mas `sky.list_apps()` encerrou com `spawn EPERM`. Um `cua.getState()` separado retornou
`apps: [], browsers: []`. Este é o bloqueador atual, diferente do anterior `os error 2`;
janelas e capturas do original não foram obtidas. Configurações e processos auxiliares não foram alterados.

O Computer Use nativo ainda não foi verificado em um novo processo. Até a reinicialização, continuamos
o trabalho com código, recursos e verificações automáticas. A correspondência visual
entre o original e o port não é considerada confirmada.

O `@oai/sky.list_apps()` anterior retornava `Computer Use native pipe is unavailable`
e Windows `os error 2`. No `~/.codex/config.toml` do usuário foram removidas apenas
duas sobreposições desatualizadas: `SKY_CUA_NATIVE_PIPE` e `SKY_CUA_NATIVE_PIPE_DIRECTORY`.
Cópia de segurança: `~/.codex/config.toml.backup-computer-use-20260925-034039`.
O TOML foi verificado após a edição. O MCP já em execução mantém as variáveis anteriores;
a reinicialização do JavaScript não atualizou o ambiente do processo.

Após a reconexão do Computer Use/reinicialização da sessão:

1. Leia as instruções atualizadas do Computer Use disponível e verifique a lista de aplicativos.
2. Se o original estiver disponível, trabalhe com a cópia em `local/experiments/runtime`; `local/game`
   permanece estritamente somente leitura.
3. Grave as telas originais de Evolution, Factory Driver, briefing/map e a largada de 0M01.
   Verifique as condições reais de conclusão, posicionamento do carro e transições.
4. Compare com a iteração 012 ativa. Salve as evidências em seus `runs`, e não em snapshots antigos.

A inicialização manual de processos auxiliares internos ou o encerramento do Codex para reinicialização
forçada não foram executados. A correção da configuração não significa que o acesso nativo
já esteja restabelecido.
