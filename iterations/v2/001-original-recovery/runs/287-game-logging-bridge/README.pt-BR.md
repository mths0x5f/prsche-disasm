# Run 287 — aresta de logging original

Preflight pronto; compilação requer aprovação do coordenador. Porsche.exe original
SHA-256 `ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39`.
Navegação no índice: CALL original de app_main 004b6b13 -> 005a177b, corpo completo de
printf com 65B e prova congelada de oito corpos da 175 (4152 casos originais em x86).

A integração ao jogo utiliza `application-log-bridge.cpp` somado ao arquivo em cache existente
`local/builds/v2/formatter-stdio-175/formatter_stdio_probe.dir/Release/formatter_stdio.obj`.
O bridge repassa sua string única, ignora o resultado inteiro original e
fornece `?application_main_log@porsche@@YAXPBD@Z`. Nenhum algoritmo copiado de printf,
nenhum segundo proprietário de alocação de buffer ou provedor de fixture ingressa na biblioteca do jogo.
Novo objeto de jogo esperado: `local/experiments/v2-game-logging-287/objects/application-log-bridge.obj`.

O SHA-256 do COFF em cache de 6534B é
`837e17652f2975e3a8ec3c2f2de8348c02dc53a7724140db7f5fd50790cadb07`.
Todos os 26 pins de código-fonte congelados da 175 continuam conferindo. O COFF real define oito funções
públicas 005a177b/36ea/3719/373c/376b/533e/53cb/76a1 e o global de buffers com dois ponteiros.
Todas as oito possuem zero proprietários exatos aceitos no registro. Suas nove definições
possuem zero sobreposições com índices de definições reais das cinco bibliotecas de jogo em cache;
todos os dez símbolos indefinidos contam com provedores lá. Nenhuma dependência de fixture/trace
aparece. Sua diretiva de MSVCRT é compatível com /MD. As interseções completas por biblioteca
e os nomes exatos estão em proof-before-compile.json.

A TU exclusiva de fixture `fixture.cpp` linka esse mesmo objeto em cache, e não um fragmento
recompilado. Sua referência nativa exata de 65B normaliza cinco campos CALL REL32 e um ponteiro
stdout DIR32 com addend32. A referência e o printf em cache utilizam os mesmos helpers reais da 175,
com pontos de corte de dependência tipados apenas na fixture. 192 casos diretos de printf comparam
oito varargs reais e seis padrões de resultado inteiro ao longo de quatro caminhos de buffer temporário.
32 casos de bridge passam somente o formato e nunca leem varargs. As comparações abrangem o estado
de 640B de FILE, ponteiros/contador de buffer, fronteiras ordenadas, EAX para chamadas de retorno
inteiro, ESP em cdecl, registradores não-voláteis e DF. Nenhuma alegação sobre todos os EFLAGS ou composição de provedores.

A tabela de bloqueios canônica real permanece como um prefixo comprovado de 26 entradas, enquanto stdout
seleciona 29 e a 175 exige 48. Isto é uma RETENÇÃO (HOLD) em tempo de execução mesmo quando a linkedição é bem-sucedida;
a fixture registra o lock 29 sem acessar uma tabela de jogo fabricada. O literal original 005d6e84
inclui uma quebra de linha (newline); o app_main atual a omite. Este bridge preserva sua entrada
exatamente e não repara o chamador compartilhado.

Preparação (sem execução de compilador/linker/binário nativo):

```powershell
py -3 scripts/research/experiment-v2-game-logging-287.py
```

Após aprovação explícita do coordenador, um lote de 2 TUs com /MP6 /MD, seguido pela linkedição da fixture
e execução (os comandos estão registrados exatamente em proof-before-compile.json):

```powershell
py -3 scripts/research/experiment-v2-game-logging-287.py --execute
```

Cada execução grava seu comprovante exclusivo de saída/temporização antes das asserções ou
da atribuição. O /sourceDependencies registra os includes reais sem que o /showIncludes
desative a compilação paralela. A prova existente de 4152 casos não é repetida.
A integração na biblioteca do jogo e a linkedição de normal-entry pertencem à raiz 289; nenhum EXE
do jogo ou composição real de provedores de saída formatada é executado aqui.
