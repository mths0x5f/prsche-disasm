# Decisões Tomadas

- 04/10/2026, decisão explícita do usuário: em todos os subsistemas restauramos
  o original, incluindo a revisão da lógica antiga. A pesquisa no índice é insuficiente:
  são necessários consumers, cálculos e comparação de estados. Aproximações não são incluídas
  na compilação do jogo por padrão. Regra: AGENTS.pt-BR.md.
  O sweep de limites foi adiado para local/experiments/012-swept-boundaries-20261004;
  a versão publicada do jogo permanece fa56d05.
- 04/10/2026: 013 é planejada para danos e mercado de usados: geração de ofertas,
  danos iniciais aleatórios, preço, compra, impacto no carro, reparo/venda.
  A pesquisa de contatos e conexão com danos começa na 012 ativa.

- Novo motor: Rust, wgpu, winit. O comportamento nós restauramos; binary matching não é o objetivo.
- Primeiro marco visual — 356a, sem física temporária.
- Snapshots completos e independentes de fontes por iteração, um único repositório Git.
- Dados comuns do jogo e ferramentas — local/, fora do Git.
- Cópia de referência do jogo inalterada; todas as execuções em cópias experimentais.
- A conclusão da etapa é determinada por verificações, e não pelo volume de código escrito.
- Esclarecimento de 19/09/2026: quaisquer provedores e modelos são permitidos. Um modelo forte
  coordena, leves executam rotina, médios — implementação delimitada.
  Model IDs específicos nos perfis são exemplos substituíveis, não requisitos. Veja agents.pt-BR.md.
- Adição: o primeiro marco inclui WebAssembly/WebGPU e site local, sem
  hospedagem externa. Um único comando compila Windows e navegador. O usuário seleciona os recursos
  no disco, eles permanecem no navegador; o servidor HTTP não distribui a pasta do jogo.
